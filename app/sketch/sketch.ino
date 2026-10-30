#include <Arduino_LED_Matrix.h>
#include "Arduino_RouterBridge.h"

Arduino_LED_Matrix matrix;

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

int heartbeat() {
    return (int)millis();
}

// Draws once per call, never from loop().
int set_mode(int mode) {
    if (mode < 0 || mode > 3) return -1;
    matrix.loadFrame(FRAMES[mode]);
    return mode;
}

int led_stress(int ms) {
    stress_ms = ms > 0 ? ms : 0;
    return ms;
}

void setup() {
    matrix.begin();
    Bridge.begin();
    Bridge.provide("heartbeat", heartbeat);
    Bridge.provide("set_mode", set_mode);
    Bridge.provide("led_stress", led_stress);
    set_mode(0);
}

void loop() {
    static uint32_t last = 0, n = 0;
    uint32_t ms = stress_ms;
    if (ms && millis() - last >= ms) {
        last = millis();
        matrix.loadFrame(FRAMES[2 + (n++ & 1)]);
    }
    delay(1);
}
