#include <Arduino_LED_Matrix.h>
#include <Adafruit_NeoPixel.h>
#include <Servo.h>
#include "Arduino_RouterBridge.h"

// Pins and numbers marked CAL are placeholders: set them to the real wiring and measure on the build.
const int PADDLE_PIN = 9;       // CAL paddle servo signal
const int LED_PIN = 5;          // CAL data pin of the 29-pixel chain
const int FOG_PIN = 4;          // CAL mist board switch, HIGH = on (low-side MOSFET with a pulldown)
const int DROP_PIN = 2;         // CAL break-beam output, LOW when a sweet breaks the beam
const int PADDLE_LOAD = 10;     // CAL degrees: pocket under the sweet tube, holds the stack back
const int PADDLE_DUMP = 80;     // CAL degrees: pocket tipped over the chute, one sweet falls
const uint32_t PADDLE_MS = 500;        // CAL how long the pocket stays tipped
const uint32_t DROP_WAIT_MS = 2500;    // how long after the paddle is back to wait for the beam
const uint32_t BEAT_MS = 1000;         // no heartbeat for this long means the safe state
const int EYES = 14, SPINE = 15, NPIX = EYES + SPINE;  // chain order: eye L (7), eye R (7), spine tail to head
const uint8_t EYE_MAX = 51, SPINE_MAX = 128;           // colour caps, about 20 and 50 percent
const uint32_t GLOW_MS = 200;         // CAL eye breathing redraw period; each redraw can cost a Bridge packet, raise it if calls are lost
const int BREATH_STEPS = 20, BLINK_EVERY = 33;  // breath cycle in steps (4 s), blink every 33 steps (6.6 s, drifts against the breath)
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
volatile uint32_t tip_start = 0, wait_start = 0;
volatile int fails = 0;
volatile int cur_mode = 0, level = 0;  // level is the spine fill, 0 to 100
volatile int idle_pct = 60, eye_open = 100;  // listen-mode eye breathing level and blink (100 open, 50 half, 0 shut)
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

void draw() {  // px.show() blocks interrupts for about 1 ms, so it runs on a change only (docs/benchmarks/heartbeat-under-load.md)
    static const uint8_t EYE[4][3] = {{255, 140, 0}, {160, 255, 210}, {0, 255, 0}, {255, 0, 0}};   // idle amber, listen mint, win green, fail red
    static const uint8_t SPN[4][3] = {{120, 0, 255}, {255, 110, 0}, {0, 255, 0}, {255, 0, 0}};
    int m = cur_mode, lit = (level * SPINE + 50) / 100, breath = m == 0 ? 60 : m == 1 ? idle_pct : 100;
    for (int i = 0; i < EYES; i++) px.setPixelColor(i, rgb(EYE[m], EYE_MAX, m == 1 ? breath * eye_open / 100 : breath));
    for (int i = 0; i < SPINE; i++) {
        int pct = m == 0 ? breath / 4 : m == 1 ? (i < lit ? 100 : 0) : m == 2 ? 100 : 15;
        px.setPixelColor(EYES + i, rgb(SPN[m], SPINE_MAX, pct));
    }
    px.show();
}

void enter_safe() {  // paddle back at load, fog off, idle glow
    safe = true;
    fog_off();
    cur_mode = 0;
    level = 0;
    dirty = true;
    phase = REST;
    paddle.write(PADDLE_LOAD);
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
    if (mode != 1) level = 0;
    if (mode == 1 && fog_on) fog_off();  // the fan and the mist hiss must not reach the mic
    dirty = true;
    return mode;
}

int set_level(int pct) {  // spine fill during LISTEN
    if (safe) return -2;
    level = pct < 0 ? 0 : pct > 100 ? 100 : pct;
    dirty = true;
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
    paddle.write(PADDLE_DUMP);
    tip_start = millis();
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
    static uint32_t glow_at = 0, c = 0;
    if (cur_mode == 1 && !safe && now - glow_at >= GLOW_MS) {  // the eyes breathe and blink only while a visitor is there (listen mode); idle and the safe state stay static
        glow_at = now;
        c++;
        int k = c % BREATH_STEPS, up = k < BREATH_STEPS / 2 ? k : BREATH_STEPS - k;
        idle_pct = 30 + 60 * up * 2 / BREATH_STEPS;
        eye_open = c % BLINK_EVERY == 0 ? 0 : c % BLINK_EVERY == 1 ? 50 : 100;
        dirty = true;
    }
    if (dirty) {
        dirty = false;
        draw();
    }

    if (phase == TIPPED && now - tip_start >= PADDLE_MS) {
        paddle.write(PADDLE_LOAD);  // back under the tube: the next sweet drops into the pocket
        phase = WAITING;
        wait_start = now;
    }
    if (phase != REST && digitalRead(DROP_PIN) == LOW) {  // a sweet broke the beam
        phase = REST;
        paddle.write(PADDLE_LOAD);
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
