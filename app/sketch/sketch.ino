#include <Arduino_LED_Matrix.h>
#include <Adafruit_NeoPixel.h>
#include <Servo.h>
#include "Arduino_RouterBridge.h"

// Pins and numbers marked CAL are placeholders: set them to the real wiring and measure on the build.
const int PADDLE_PIN = 9;       // CAL paddle servo signal
const int LED_PIN = 5;          // CAL data pin of the 30-pixel chain
const int FOG_PIN = 4;          // CAL mist board switch, HIGH = on (low-side MOSFET with a pulldown)
const int DROP_PIN = 2;         // CAL LM393 IR module OUT, LOW while a sweet is in front of it
const int PADDLE_LOAD = 170;    // CAL degrees: rotor pocket facing up the sweet tube, takes one sweet
const int PADDLE_DUMP = 25;     // CAL degrees: pocket facing down the chute, 145 from LOAD over the top (hardware/cad/dispenser); swap the two if the servo turns the other way
const uint32_t PADDLE_MS = 500;        // CAL how long the pocket stays tipped, counted from when it gets there
const uint32_t SWEEP_MS = 3;           // CAL ms per degree: 160 degrees in about 0.5 s, no slam and no flung sweet
const uint32_t DROP_WAIT_MS = 2500;    // how long after the paddle is back to wait for the beam
const uint32_t BEAT_MS = 1000;         // no heartbeat for this long means the safe state
const int PLATES = 8, PLATE_PX = 2;  // CAL eight spine plates, tail to head, and the pixels under each
const int EYES = 14, SPINE = PLATES * PLATE_PX, NPIX = EYES + SPINE;  // chain order: eye L (7), eye R (7), spine tail to head
const uint8_t EYE_MAX = 51, SPINE_MAX = 128;           // colour caps, about 20 and 50 percent
const uint32_t TICK_MS = 200;         // CAL personality step. draw() only calls px.show() when a pixel changed, so a still tick costs nothing on the Bridge
const int BREATH_STEPS = 20;           // listen breath cycle in ticks (4 s)
const uint32_t FOG_MAX_MS = 3000;      // CAL longest burst
const uint32_t FOG_REST_MS = 6000;     // CAL pause after a burst so the disc and the water cup can settle

Arduino_LED_Matrix matrix;
Adafruit_NeoPixel px(NPIX, LED_PIN, NEO_GRB + NEO_KHZ800);
Servo paddle;

// One 8x13 frame per mode: idle, listen, win, fail.
static const uint32_t FRAMES[4][4] = {
    {0x00000000, 0x00600600, 0x00000000, 0x00000000},
    {0x0F00F000, 0x0F00F000, 0x00000000, 0x00000000},
    {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x00000000},
    {0xAAAAAAAA, 0x55555555, 0xAAAAAAAA, 0x00000000},
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
volatile uint32_t tick = 0;            // ticks since the last mode change; win and fail play out from 0
volatile int eye_l = 40, eye_r = 40;   // percent of the eye colour cap, per eye, so one eye can glance or flicker alone
volatile int pulse = -1;               // spine plate (0 tail to 7 head) lit by the idle pulse, -1 for none
volatile bool dirty = true;            // handlers only set this; loop() does the slow pixel write
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
    static const uint8_t EYE[4][3] = {{255, 70, 0}, {255, 140, 0}, {255, 190, 40}, {255, 0, 0}};  // warm only, the orange iris swallows green and blue: idle ember, listen amber, win gold, fail red
    static const uint8_t SPN[4][3] = {{120, 0, 255}, {255, 110, 0}, {0, 255, 0}, {255, 0, 0}};
    int m = cur_mode, t = tick, lit = (level * PLATES + 50) / 100;  // whole plates, so the 8th plate lights from level 94
    bool changed = false;
    for (int i = 0; i < NPIX; i++) {
        int plate = (i - EYES) / PLATE_PX, pct;
        if (i < EYES) pct = i < 7 ? eye_l : eye_r;
        else if (m == 0) pct = plate == pulse ? 60 : 15;
        else if (m == 1) pct = plate < lit ? 100 : 6; // unlit plates keep a faint ember
        else if (m == 2) pct = plate < t ? 100 : 6;   // fills tail to head, one plate per tick
        else pct = plate < PLATES - t ? 60 : 15;      // drains head to tail, one plate per tick
        uint32_t c = i < EYES ? rgb(EYE[m], EYE_MAX, pct) : rgb(SPN[m], SPINE_MAX, pct);
        if (c != px.getPixelColor(i)) {
            px.setPixelColor(i, c);
            changed = true;
        }
    }
    if (changed) px.show();
}

void step() {  // one tick of eye and spine personality, never in the safe state
    static int ev = -1, ev_t = 0, side = 0, wait = 30, blink = 25;
    static const int8_t STIR[] = {55, 75, 90, 75, 55};
    static const int8_t LEN[] = {5, 4, 3, PLATES};  // ticks per idle event: stir, glance, flicker, pulse
    int t = ++tick, m = cur_mode;
    pulse = -1;
    if (m == 0) {  // idle: it mostly sleeps; every 4 to 12 s it stirs, glances to one side, flickers one eye or sends a pulse up the spine
        eye_l = eye_r = 40;
        if (ev < 0 && --wait <= 0) {
            ev = random(4);
            ev_t = 0;
            side = random(2);
        }
        if (ev < 0) return;
        volatile int &look = side ? eye_r : eye_l, &away = side ? eye_l : eye_r;
        if (ev == 0) eye_l = eye_r = STIR[ev_t];
        else if (ev == 1) { look = 85; away = 15; }
        else if (ev == 2) look = ev_t == 1 ? 40 : 10;
        else pulse = ev_t;
        if (++ev_t >= LEN[ev]) {
            ev = -1;
            wait = random(20, 61);
        }
    } else if (m == 1) {  // listen: breathes, blinks at uneven gaps, and widens with level (the scream meter, or the time left in a riddle)
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
    level = 0;
    tick = 0;
    eye_l = eye_r = 40;  // the safe state holds a still idle glow
    pulse = -1;
    dirty = true;
    phase = REST;
    target = PADDLE_LOAD;
    show(0);
}

int heartbeat() {
    last_beat = millis();
    return (int)last_beat;
}

int set_mode(int mode) {
    if (mode < 0 || mode > 3) return -1;
    if (safe) {  // only a fresh heartbeat plus an explicit idle clears it
        if (mode != 0 || millis() - last_beat > BEAT_MS) return -2;
        safe = false;
        fails = 0;
    }
    show(mode);
    cur_mode = mode;
    tick = 0;
    if (mode != 1) level = 0;
    if (mode == 1 && fog_on) fog_off();  // the fan and the mist hiss must not reach the mic
    dirty = true;
    return mode;
}

int set_level(int pct) {  // spine fill during LISTEN: the scream meter, or the riddle countdown
    if (safe) return -2;
    level = pct < 0 ? 0 : pct > 100 ? 100 : pct;  // no redraw here: the 0.2 s tick draws it, so the meter cannot push redraws past 5 a second
    return level;
}

int set_fog(int on_ms) {  // one burst; 0 stops it
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
    pinMode(DROP_PIN, INPUT_PULLUP);
    paddle.attach(PADDLE_PIN);
    paddle.write(PADDLE_LOAD);
    matrix.begin();
    Bridge.begin();
    Bridge.provide("heartbeat", heartbeat);
    Bridge.provide("set_mode", set_mode);
    Bridge.provide("set_level", set_level);
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
    if (dirty) {
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
    if (phase == TIPPED && angle == PADDLE_DUMP && now - arrived >= PADDLE_MS) {
        target = PADDLE_LOAD;  // back under the tube: the next sweet drops into the pocket
        phase = WAITING;
        wait_start = now;
    }
    if (phase != REST && digitalRead(DROP_PIN) == LOW) {  // the IR module saw a sweet
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
