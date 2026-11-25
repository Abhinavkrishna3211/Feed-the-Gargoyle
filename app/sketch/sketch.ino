#include <Arduino_LED_Matrix.h>
#include <Adafruit_NeoPixel.h>
#include <Servo.h>
#include "Arduino_RouterBridge.h"

// RPClite 0.3.1 never recovers from a damaged stream: a stray byte at the head of its buffer is never consumed, and a packet
// longer than the request buffer is never dropped, so the MCU stops answering until App Lab reloads the sketch.
// flush_bridge() empties the decoder under the Bridge's own read lock. The members are private, so they are reached with
// the explicit-instantiation access idiom (legal C++, no library edits). Checked against Arduino_RouterBridge 0.4.3.
template <typename Tag, typename Tag::type M> struct Rob { friend typename Tag::type get(Tag) { return M; } };
#define ROB(name, T, member) struct name { typedef T type; friend type get(name); }; template struct Rob<name, member>;
ROB(BServer, RPCServer* BridgeClass::*, &BridgeClass::server)
ROB(BLock, struct k_mutex BridgeClass::*, &BridgeClass::read_mutex)
ROB(SDec, RpcDecoder<>* RPCServer::*, &RPCServer::decoder)
ROB(DStored, size_t RpcDecoder<>::*, &RpcDecoder<>::_bytes_stored)
ROB(DSize, size_t RpcDecoder<>::*, &RpcDecoder<>::_packet_size)
ROB(DType, int RpcDecoder<>::*, &RpcDecoder<>::_packet_type)
ROB(DROff, size_t RpcDecoder<>::*, &RpcDecoder<>::_response_offset)
ROB(DRSize, size_t RpcDecoder<>::*, &RpcDecoder<>::_response_size)

void flush_bridge() {
    struct k_mutex* lock = &(Bridge.*get(BLock()));
    if (k_mutex_lock(lock, K_MSEC(50)) != 0) return;
    RpcDecoder<>* d = (Bridge.*get(BServer()))->*get(SDec());
    d->*get(DStored()) = d->*get(DSize()) = d->*get(DROff()) = d->*get(DRSize()) = 0;
    d->*get(DType()) = NO_MSG;
    k_mutex_unlock(lock);
}

// Pins and numbers marked CAL are placeholders: set them to the real wiring and measure on the build.
const int PADDLE_PIN = 9;       // CAL paddle servo signal
const int EYE_PIN = 5;          // eye L (7) then eye R (7), one chain
const int SPINE_PIN = 6;        // spine chain, tail (bottom) plate first
const int FOG_PIN = 4;          // CAL mist board switch, HIGH = on (low-side MOSFET with a pulldown)
const int DROP_PIN = 2;         // CAL LM393 IR module OUT, LOW while a sweet is in front of it
const int PADDLE_LOAD = 170;    // CAL degrees: rotor pocket facing up the sweet tube, takes one sweet
const int PADDLE_DUMP = 25;     // CAL degrees: pocket facing down the chute, 145 from LOAD over the top (hardware/cad/dispenser); swap the two if the servo turns the other way
const uint32_t PADDLE_MS = 500;        // CAL how long the pocket stays tipped, counted from when it gets there
const uint32_t SWEEP_MS = 3;           // CAL ms per degree: 160 degrees in about 0.5 s, no slam and no flung sweet
const uint32_t DROP_WAIT_MS = 2500;    // how long after the paddle is back to wait for the beam
const uint32_t BEAT_MS = 1000;         // no heartbeat for this long means the safe state
const int PLATES = 8, PLATE_PX = 3;  // eight spine plates, tail to head, three pixels under each
const int EYES = 14, SPINE = PLATES * PLATE_PX, NPIX = EYES + SPINE;  // pixel i < EYES is on the eye chain, the rest on the spine chain
const uint8_t EYE_MAX = 51, SPINE_MAX = 180;           // CAL colour caps: eyes about 20 percent, spine about 70; at 255 a full spine dropped the USB camera off the bus on the UNO Q (fullrun, 2026-11-16)
const uint32_t TICK_MS = 200;         // CAL personality step. draw() only calls px.show() when a pixel changed, so a still tick costs nothing on the Bridge
const int BREATH_STEPS = 20;           // listen breath cycle in ticks (4 s)
const uint32_t METER_MS = 40;          // CAL the meter gains one plate per 40 ms (full in 0.32 s) and loses one per FALL_TICKS of these: it keeps up with a voice but never jumps dark to full
const int FALL_TICKS = 3;
const int SLEEP_STEPS = 50, SLEEP_LO = 8, SLEEP_HI = 20;  // CAL sleep breath: 10 s cycle between 8 and 20 percent of the eye cap
const uint32_t FOG_MAX_MS = 3000;      // CAL longest burst
const uint32_t FOG_REST_MS = 6000;     // CAL pause after a burst so the disc and the water cup can settle

Arduino_LED_Matrix matrix;
Adafruit_NeoPixel px(EYES, EYE_PIN, NEO_GRB + NEO_KHZ800), spine(SPINE, SPINE_PIN, NEO_GRB + NEO_KHZ800);
Servo paddle;

// One 8x13 frame per mode: idle, listen, win, fail, awake.
static const uint32_t FRAMES[5][4] = {
    {0x00000000, 0x00600600, 0x00000000, 0x00000000},
    {0x0F00F000, 0x0F00F000, 0x00000000, 0x00000000},
    {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x00000000},
    {0xAAAAAAAA, 0x55555555, 0xAAAAAAAA, 0x00000000},
    {0x0F00F000, 0x0F00F000, 0x00000000, 0x00000000},
};

// Test only: redraw every N ms, to measure what LED traffic does to Bridge latency.
// 0 means redraw on change only, which is the normal behaviour.
volatile uint32_t stress_ms = 0;

enum Dispense { REST, TIPPED, WAITING };  // TIPPED: pocket over the chute; WAITING: paddle back, waiting for the beam
volatile Dispense phase = REST;
volatile bool safe = false;
volatile uint32_t last_beat = 0;
volatile uint32_t arrived = 0, wait_start = 0;
volatile int target = PADDLE_LOAD;    // handlers set this; loop() walks the servo there one degree at a time
volatile int fails = 0;
volatile int cur_mode = 0, level = 0;  // level is the spine fill, 0 to 100
int meter = 0;                         // plates the meter shows, chasing level one plate at a time
volatile uint32_t tick = 0;            // ticks since the last mode change; win and fail play out from 0
volatile int eye_l = 40, eye_r = 40;   // percent of the eye colour cap, per eye, so one eye can glance or flicker alone
volatile int talk = -1;                // loudness of the line being spoken, 0 to 100 (set_talk), -1 when silent
volatile uint32_t talk_at = 0;
int glow = -1;                         // eye level while talking or easing back, also picks the talk colour; -1 when the mode owns the eyes
volatile bool dirty = true;            // handlers only set this; loop() does the slow pixel write
volatile uint32_t quiet_at = 0;        // when a Bridge call was last answered: Python sends one at a time and sleeps GAP_S (20 ms) after the reply, so the line is idle just after it
const uint32_t QUIET_MS = 5;           // CAL px.show() may start only this soon after a reply. A plain flag stayed set until the next tick and drew while the next call arrived
const uint32_t HUNG_MS = 1500;         // CAL Python calls every 0.1 to 0.2 s; silence this long means a wedged decoder, so flush it (again every HUNG_MS)
volatile bool fog_on = false;
volatile uint32_t fog_until = 0, fog_ready = 0;
volatile bool send_drop = false, send_jam = false;  // Bridge notices are sent from loop(), never from a handler

void show(int mode) {
    matrix.loadFrame(FRAMES[mode]);  // called on a change only
}

void fog_off() {
    digitalWrite(FOG_PIN, LOW);
    fog_on = false;
    fog_ready = millis() + FOG_REST_MS;
}

uint32_t rgb(const uint8_t *c, uint8_t cap, int pct) {  // colour c at cap and pct percent of it
    return px.Color((uint32_t)c[0] * cap * pct / 25500, (uint32_t)c[1] * cap * pct / 25500, (uint32_t)c[2] * cap * pct / 25500);
}

void draw() {  // px.show() blocks interrupts for about 0.9 ms and can damage a Bridge packet (docs/benchmarks/heartbeat-under-load.md), so it only runs when a pixel changed
    static const uint8_t EYE[5][3] = {{255, 70, 0}, {255, 140, 0}, {255, 190, 40}, {255, 0, 0}, {255, 140, 0}};  // warm only, the orange iris swallows green and blue: idle ember, listen amber, win gold, fail red, awake amber
    static const uint8_t SPN[5][3] = {{0, 0, 0}, {0, 0, 0}, {0, 255, 0}, {255, 0, 0}, {255, 110, 0}};  // listen picks its colour per plate below
    int m = cur_mode, t = tick;
    bool changed = false, spine_changed = false;
    for (int i = 0; i < NPIX; i++) {
        int plate = (i - EYES) / PLATE_PX, pct;
        if (i < EYES) pct = i < 7 ? eye_l : eye_r;
        else if (m == 0 || m == 1) pct = m == 1 && plate < meter ? 100 : 0;  // asleep dark; listening, the scream alone lights it
        else if (m == 2) pct = plate < t ? 100 : 0;   // win: green fills tail to head, one plate per tick, and stays
        else if (m == 3) pct = plate >= PLATES - t ? 70 : 0;  // fail: red fills head to tail, one plate per tick, and stays
        else pct = 25 + 10 * (t % 20 < 10 ? t % 20 : 20 - t % 20) / 10;  // awake: a slow amber breath, 25 to 35
        uint8_t heat[3] = {(uint8_t)min(255, 510 * plate / (PLATES - 1)), (uint8_t)min(255, 510 * (PLATES - 1 - plate) / (PLATES - 1)), 0};  // meter: green at the tail, yellow mid, red at the head
        uint8_t hot[3] = {255, (uint8_t)(20 + 130 * glow / 100), (uint8_t)(10 * glow / 100)};  // blood red when it whispers, hot amber when it roars; at 40 it matches the idle ember
        uint32_t c = i < EYES ? rgb(glow >= 0 ? hot : EYE[m], EYE_MAX, pct) : rgb(m == 1 ? heat : SPN[m], SPINE_MAX, pct);
        Adafruit_NeoPixel &chain = i < EYES ? px : spine;
        int j = i < EYES ? i : i - EYES;
        if (c != chain.getPixelColor(j)) {
            chain.setPixelColor(j, c);
            (i < EYES ? changed : spine_changed) = true;
        }
    }
    if (changed) px.show();  // each chain shows only when it changed, so a still spine costs nothing while the eyes talk
    if (spine_changed) spine.show();
}

void mood();

void step() {  // one tick of eye and spine personality, never in the safe state
    static int lag = -1;
    if (talk >= 0 && millis() - talk_at < 600) {  // speaking: the eyes follow the voice; a lost set_talk(-1) times out here
        tick++;
        if (glow < 0) glow = eye_l;
        int goal = 20 + talk * 80 / 100;
        glow += constrain(goal - glow, -6, 20);  // swells with a phrase, sinks slowly to an ember in the pauses; at most 20 percent a tick, so no flash
        eye_r = lag < 0 ? glow : lag;             // the right eye answers a tick late
        eye_l = lag = glow;
        return;
    }
    lag = -1;
    mood();
    if (glow >= 0) {  // the line just ended: ease from the talk level to the mode's own eyes
        int goal = eye_l;
        glow += constrain(goal - glow, -8, 8);
        if (glow == goal) glow = -1;
        else eye_l = eye_r = glow;
    }
}

void mood() {  // the mode's own eyes and spine
    static int blink = 25;
    int t = ++tick, m = cur_mode;
    if (m == 0) {  // asleep until a visitor wakes it: a slow dim breath, one percent a tick, so nothing jumps
        int k = t % SLEEP_STEPS, up = k < SLEEP_STEPS / 2 ? k : SLEEP_STEPS - k;
        eye_l = eye_r = SLEEP_LO + up * (SLEEP_HI - SLEEP_LO) * 2 / SLEEP_STEPS;
    } else if (m == 1 || m == 4) {  // awake and listen: breathes, blinks at uneven gaps, and widens with level (the scream meter, or the time left in a riddle)
        int k = t % BREATH_STEPS, up = k < BREATH_STEPS / 2 ? k : BREATH_STEPS - k;
        int eye = min(100, 30 + 60 * up * 2 / BREATH_STEPS + level / 4);
        blink--;
        if (blink < -1) blink = random(15, 45);
        eye_l = eye_r = blink == 0 ? 0 : blink == -1 ? eye / 2 : eye;
    } else if (m == 2) {  // win: a flare, then a steady glow
        eye_l = eye_r = t == 1 ? 100 : 80;
    } else {  // fail: a flash, then the eyes narrow
        eye_l = eye_r = t == 1 ? 100 : 30;
    }
}

void enter_safe() {  // paddle back at load, fog off, idle glow
    safe = true;
    fog_off();
    cur_mode = 0;
    level = meter = 0;
    tick = 0;
    eye_l = eye_r = 40;  // the safe state holds a still idle glow
    talk = glow = -1;
    dirty = true;
    phase = REST;
    target = PADDLE_LOAD;
    show(0);
}

int heartbeat() {
    quiet_at = millis();
    last_beat = millis();
    return (int)last_beat;
}

int set_mode(int mode) {
    quiet_at = millis();
    if (mode < 0 || mode > 4) return -1;
    if (safe) {  // only a fresh heartbeat plus an explicit idle clears it
        if (mode != 0 || millis() - last_beat > BEAT_MS) return -2;
        safe = false;
        fails = 0;
    }
    show(mode);
    cur_mode = mode;
    tick = 0;
    if (mode != 1) level = meter = 0;
    if (mode == 1 && fog_on) fog_off();  // the fan and the mist hiss must not reach the mic
    dirty = true;
    return mode;
}

int set_talk(int pct) {  // loudness of the playing line, every 0.2 s; it doubles as the heartbeat while audio plays
    quiet_at = millis();
    last_beat = talk_at = millis();
    talk = pct < 0 ? -1 : pct > 100 ? 100 : pct;  // no redraw here: the next tick picks it up
    return talk;
}

int set_level(int pct) {  // spine fill during LISTEN: the scream meter, or the riddle countdown
    quiet_at = millis();
    if (safe) return -2;
    level = pct < 0 ? 0 : pct > 100 ? 100 : pct;  // no redraw here: the meter tick in loop() chases it
    return level;
}

int set_fog(int on_ms) {  // one burst; 0 stops it
    quiet_at = millis();
    if (safe) return -2;
    if (on_ms <= 0) {
        if (fog_on) fog_off();
        return 0;
    }
    if (cur_mode == 1) return -3;  // never while listening
    if (fog_on || (int32_t)(millis() - fog_ready) < 0) return -1;
    if (on_ms > (int)FOG_MAX_MS) on_ms = FOG_MAX_MS;
    fog_until = millis() + on_ms;
    fog_on = true;
    digitalWrite(FOG_PIN, HIGH);
    return on_ms;
}

int dispense() {
    quiet_at = millis();
    if (safe || phase != REST) return -1;
    target = PADDLE_DUMP;
    phase = TIPPED;
    return 0;
}

int led_stress(int ms) {
    stress_ms = ms > 0 ? ms : 0;
    return ms;
}

void setup() {
    pinMode(FOG_PIN, OUTPUT);
    digitalWrite(FOG_PIN, LOW);
    px.begin();
    spine.begin();
    pinMode(DROP_PIN, INPUT_PULLUP);
    paddle.attach(PADDLE_PIN);
    paddle.write(PADDLE_LOAD);
    matrix.begin();
    Bridge.begin();
    Bridge.provide("heartbeat", heartbeat);
    Bridge.provide("set_mode", set_mode);
    Bridge.provide("set_level", set_level);
    Bridge.provide("set_talk", set_talk);
    Bridge.provide("set_fog", set_fog);
    Bridge.provide("dispense", dispense);
    Bridge.provide("led_stress", led_stress);
    last_beat = millis();
    show(0);
}

void loop() {
    static uint32_t last = 0, n = 0;
    uint32_t now = millis();

    if (!safe && now - last_beat > BEAT_MS) enter_safe();
    if (fog_on && (int32_t)(now - fog_until) >= 0) fog_off();
    static uint32_t glow_at = 0;
    if (!safe && now - glow_at >= TICK_MS) {  // the safe state stays still
        glow_at = now;
        step();
        dirty = true;  // draw() skips px.show() when the step changed nothing
    }
    static uint32_t meter_at = 0;
    static int fall = 0;
    if (!safe && cur_mode == 1 && now - meter_at >= METER_MS) {  // listening: the spine chases the level on its own fast tick
        meter_at = now;
        int want = (level * PLATES + 50) / 100;  // whole plates, so the 8th lights from level 94
        if (want > meter) { meter++; fall = 0; dirty = true; }
        else if (want < meter && ++fall >= FALL_TICKS) { meter--; fall = 0; dirty = true; }
    }
    uint32_t q = quiet_at, since = millis() - q;  // quiet_at first: a call landing in between only makes since too big, never wraps it
    static uint32_t flushed_at = 0;
    if (since > HUNG_MS && now - flushed_at > HUNG_MS) {  // harmless when the line is idle, and it also clears boot noise that wedged it before the first call
        flushed_at = now;
        flush_bridge();
    }
    if (dirty && (since < QUIET_MS || since > BEAT_MS)) {  // write the pixels only just after a Bridge call (or when Python is silent): px.show() blocks interrupts and damages a packet arriving meanwhile, which can leave the MCU side of the Bridge dead until a reset
        dirty = false;
        draw();
    }

    static int angle = PADDLE_LOAD;
    static uint32_t step_at = 0;
    if (angle != target && now - step_at >= SWEEP_MS) {
        step_at = now;
        angle += angle < target ? 1 : -1;
        paddle.write(angle);
        if (angle == target) arrived = now;
    }
    static bool seen = false;  // the beam broke while the pocket was tipped
    bool beam = digitalRead(DROP_PIN) == LOW;
    if (phase == TIPPED && angle == PADDLE_DUMP) seen |= beam;  // before the pocket is over the chute nothing can fall, so a noisy beam there cannot abort the dump
    if (phase == TIPPED && angle == PADDLE_DUMP && now - arrived >= PADDLE_MS) {
        target = PADDLE_LOAD;  // back under the tube: the next sweet drops into the pocket
        phase = WAITING;
        wait_start = now;
        if (seen) beam = true;  // it fell during the tip: confirm below
        seen = false;
    }
    if (phase == WAITING && beam) {  // the IR module saw a sweet
        phase = REST;
        target = PADDLE_LOAD;
        fails = 0;
        send_drop = true;
    } else if (phase == WAITING && now - wait_start > DROP_WAIT_MS) {
        phase = REST;
        if (++fails >= 2) {  // two misses in a row: stop and say so
            send_jam = true;
            enter_safe();
        }
    }
    if (send_drop) { send_drop = false; Bridge.notify("drop_confirmed"); }
    if (send_jam) { send_jam = false; Bridge.notify("jam"); }

    uint32_t ms = stress_ms;
    if (ms && now - last >= ms) {
        last = now;
        matrix.loadFrame(FRAMES[2 + (n++ & 1)]);
    }
    delay(1);
}
