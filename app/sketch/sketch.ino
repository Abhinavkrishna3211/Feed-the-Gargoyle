#include <Arduino_LED_Matrix.h>
#include <Servo.h>
#include "Arduino_RouterBridge.h"

// Pins and numbers marked CAL are placeholders: set them to the real wiring and measure on the build.
const int JAW_PIN = 9;          // CAL jaw servo signal
const int STEP_PIN = 6;         // CAL wheel driver STEP
const int DIR_PIN = 7;          // CAL wheel driver DIR
const int EN_PIN = 8;           // CAL wheel driver EN, LOW = on
const int DROP_PIN = 2;         // CAL break-beam output, LOW when a sweet breaks the beam
const int JAW_CLOSED = 10;      // CAL servo degrees
const int JAW_OPEN = 70;        // CAL servo degrees
const uint32_t STEPS_PER_SWEET = 400;  // CAL steps for one wheel pocket
const uint32_t STEP_US = 1500;         // CAL time between steps
const uint32_t DROP_WAIT_MS = 2500;    // how long after the wheel stops to wait for the beam
const uint32_t BEAT_MS = 1000;         // no heartbeat for this long means the safe state

Arduino_LED_Matrix matrix;
Servo jaw;

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

enum Dispense { REST, RUNNING, WAITING };
volatile Dispense phase = REST;
volatile bool safe = false;
volatile uint32_t last_beat = 0;
volatile uint32_t steps_left = 0, wait_start = 0;
volatile int fails = 0;
volatile bool send_drop = false, send_jam = false;  // Bridge notices are sent from loop(), never from a handler

void show(int mode) {
    matrix.loadFrame(FRAMES[mode]);  // called on a change only
}

void enter_safe() {  // jaw closed, wheel stopped, idle glow
    safe = true;
    phase = REST;
    steps_left = 0;
    digitalWrite(EN_PIN, HIGH);
    jaw.write(JAW_CLOSED);
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
    return mode;
}

int dispense() {
    if (safe || phase != REST) return -1;
    jaw.write(JAW_OPEN);
    digitalWrite(EN_PIN, LOW);
    steps_left = STEPS_PER_SWEET;
    phase = RUNNING;
    return 0;
}

int led_stress(int ms) {
    stress_ms = ms > 0 ? ms : 0;
    return ms;
}

void setup() {
    pinMode(STEP_PIN, OUTPUT);
    pinMode(DIR_PIN, OUTPUT);
    pinMode(EN_PIN, OUTPUT);
    pinMode(DROP_PIN, INPUT_PULLUP);
    digitalWrite(EN_PIN, HIGH);
    digitalWrite(DIR_PIN, HIGH);
    jaw.attach(JAW_PIN);
    jaw.write(JAW_CLOSED);
    matrix.begin();
    Bridge.begin();
    Bridge.provide("heartbeat", heartbeat);
    Bridge.provide("set_mode", set_mode);
    Bridge.provide("dispense", dispense);
    Bridge.provide("led_stress", led_stress);
    last_beat = millis();
    show(0);
}

void loop() {
    static uint32_t last = 0, n = 0, step_at = 0;
    uint32_t now = millis(), us = micros();

    if (!safe && now - last_beat > BEAT_MS) enter_safe();

    if (phase == RUNNING && us - step_at >= STEP_US) {
        step_at = us;
        digitalWrite(STEP_PIN, HIGH);
        delayMicroseconds(5);
        digitalWrite(STEP_PIN, LOW);
        if (--steps_left == 0) {
            phase = WAITING;
            wait_start = now;
        }
    }
    if (phase != REST && digitalRead(DROP_PIN) == LOW) {  // a sweet broke the beam
        phase = REST;
        digitalWrite(EN_PIN, HIGH);
        jaw.write(JAW_CLOSED);
        fails = 0;
        send_drop = true;
    } else if (phase == WAITING && now - wait_start > DROP_WAIT_MS) {
        phase = REST;
        digitalWrite(EN_PIN, HIGH);
        jaw.write(JAW_CLOSED);
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
    if (phase != RUNNING) delay(1);
}
