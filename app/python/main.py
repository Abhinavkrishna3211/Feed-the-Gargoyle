import os
import statistics
import time
import json

from arduino.app_utils import *

import subprocess
import costume, game, runner, sensors, voice

# Create python/bench.on to run the Bridge latency check once instead of the heartbeat.
HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.exists(os.path.join(HERE, "bench.on"))
WARMUP, N = 10, 200
# Create python/dispense.on to run the dispenser bench test instead: DROPS dispenses EVERY_S apart, stops on a jam.
DISPENSE = os.path.exists(os.path.join(HERE, "dispense.on"))
DROPS, EVERY_S = 50, 4.0
tally = {"sent": 0, "drop_confirmed": 0, "jam": 0}
next_drop = 0.0
MODELS = [os.path.join(HERE, "models", n) for n in ("costume.tflite", "props.eim")]  # either may be missing; the game only reacts to labels it has a line for

# Write one challenge name (scream or riddle) to python/challenge.txt to play only that one, for testing.
CHOSEN = os.path.join(HERE, "challenge.txt")
if os.path.exists(CHOSEN):
    game.CHALLENGES = (open(CHOSEN).read().strip(),)
# Write one costume label (batman) to python/costume.txt to greet every visitor as that costume, for filming.
FORCED = os.path.join(HERE, "costume.txt")
if os.path.exists(FORCED):
    game.FORCED = open(FORCED).read().strip() or None
# Write one look (idle, awake, listen, win, fail) to python/hold.txt to freeze the LEDs in it for filming; the game pauses.
HOLD = os.path.join(HERE, "hold.txt")
LOOP_S = 8  # CAL seconds per look when hold.txt lists several
held = None
GAP_S = 0.02  # after each Bridge reply the MCU redraws the LEDs with interrupts off; the next packet must not land in that


def call(name, *args, timeout=10):
    """Bridge.call, then a short gap so the next call never arrives during px.show() (that left the MCU Bridge dead before)."""
    try:
        return Bridge.call(name, *args, timeout=timeout)
    finally:
        time.sleep(GAP_S)


done = False
armed = False  # the MCU may already be in its safe state when the app starts; only set_mode(0) after a fresh heartbeat clears it


def arm():
    global armed
    try:
        armed = call("set_mode", 0, timeout=1.0) == 0
    except Exception:
        pass


def beat():
    """One heartbeat. A call lost on the Bridge must not stall the next one: the MCU watchdog is 1 s."""
    try:
        call("heartbeat", timeout=0.25)
    except Exception:
        pass


LEAD_S = 0.1  # CAL send each loudness value this early, for the MCU tick and slew; aplay takes about 0.13 s to sound (latency-budget.md)


def play(path):
    """aplay, with the eyes following the voice: set_talk every 0.2 s is also the heartbeat for the 1 s MCU watchdog."""
    try:
        env = voice.envelope(path)
    except Exception:
        env = []
    p = subprocess.Popen(["aplay", "-q", "-D", voice.DEVICE, str(path)])
    t0 = time.monotonic()
    while p.poll() is None:
        i = int((time.monotonic() - t0 - 0.13 + LEAD_S) / voice.TALK_S)
        try:
            call("set_talk", env[i] if 0 <= i < len(env) else 0, timeout=0.25)
        except Exception:
            pass
        time.sleep(voice.TALK_S)
    try:
        call("set_talk", -1, timeout=0.25)  # back to the mode's own eyes
    except Exception:
        pass


Bridge.provide("drop_confirmed", lambda: game_loop.push(("drop_confirmed",)))  # MCU notices
Bridge.provide("jam", lambda: game_loop.push(("jam",)))
subprocess.run(voice.SPEAKER_MIXER)  # the card comes up at half level


def real_sensors():
    """Bricks with our own models; they need the .eim files from the Edge Impulse projects (python/sensors.on)."""
    from arduino.app_peripherals.microphone import Microphone
    from arduino.app_peripherals.camera import Camera
    from arduino.app_bricks.video_imageclassification import VideoImageClassification
    from arduino.app_utils.image.adjustments import compress_to_jpeg
    from arduino.app_bricks.keyword_spotting import KeywordSpotting
    cam, last = Camera(), [None]
    read = cam.capture

    def capture():  # the brick reads every frame; keep the latest for the costume models, so the camera has one reader
        last[0] = read()
        return last[0]
    cam.capture = capture
    mic = Microphone(device="plughw:CARD=Device,DEV=0")  # the Boya, by name: card numbers swap between boots
    pick = costume.best(*[costume.make(p) for p in MODELS if os.path.exists(p)])
    return sensors.Sensors(VideoImageClassification(camera=cam, confidence=0.3), sensors.Tap(mic),  # one Boya stream feeds the keywords and the scream meter
                           KeywordSpotting(mic=mic, confidence=0.5, debounce_sec=0.0),
                           costume=lambda: pick(compress_to_jpeg(last[0]).tobytes()))


# Lines and clips are copied next to this file; Stub stands in until python/sensors.on says the models are installed.
BANK = os.path.join(HERE, "bank_demo")  # filming: a copy of the bank with one chosen line per moment, so every take says the same thing
game_loop = runner.Runner(game.Game(), voice.Voice(BANK if os.path.isdir(BANK) else os.path.join(HERE, "bank"), os.path.join(HERE, "sounds"), play=play),
                          call, real_sensors() if os.path.exists(os.path.join(HERE, "sensors.on")) else runner.Stub())


def rtt_ms(n):
    out, fails = [], 0
    for _ in range(n):
        t = time.monotonic()
        try:
            Bridge.call("heartbeat")
            out.append((time.monotonic() - t) * 1000)
        except Exception:
            fails += 1
        time.sleep(0.05)
    return out, fails


def bench():
    for cond, ms in (("led_on_change_only", 0), ("redraw_500ms", 500), ("redraw_100ms", 100), ("redraw_40ms", 40)):
        Bridge.call("led_stress", ms)
        Bridge.call("set_mode", 0)
        rtt_ms(WARMUP)
        xs, fails = rtt_ms(N)
        xs_s = sorted(xs)
        row = {"cond": cond, "n": len(xs), "fails": fails}
        if xs:
            row.update(min=round(xs_s[0], 1), median=round(statistics.median(xs), 1),
                       p95=round(xs_s[int(0.95 * (len(xs) - 1))], 1), max=round(xs_s[-1], 1))
        print("SUMMARY " + json.dumps(row), flush=True)
        print("RAW " + json.dumps({"cond": cond, "rtt_ms": [round(x, 2) for x in xs]}), flush=True)
    Bridge.call("led_stress", 0)
    Bridge.call("set_mode", 0)


def dispense_test():
    global next_drop, done, armed
    beat()
    if not armed:
        arm()
    for ev in game_loop.inbox:
        tally[ev[0]] += 1
    game_loop.inbox = []
    if tally["jam"] or tally["sent"] >= DROPS:
        if not done and time.monotonic() >= next_drop:  # the last notice can land up to 3 s after the call
            print("DISPENSE " + json.dumps(tally), flush=True)
            done = True
        return
    if armed and time.monotonic() >= next_drop:
        next_drop = time.monotonic() + EVERY_S
        r = game_loop.bridge("dispense")
        tally["sent"] += r == 0
        armed = r == 0  # -1: the watchdog tripped, set_mode(0) again before the next one
        print(f"dispense {tally['sent']} -> {r} {tally}", flush=True)


def loop():
    global done
    if DISPENSE:
        dispense_test()
        time.sleep(0.1)
        return
    if BENCH:
        if not done:
            bench()
            done = True
        time.sleep(1)
        return
    global armed
    beat()
    if game_loop.safe:  # the MCU refused a command: it went safe (watchdog or jam), clear it with set_mode(0)
        game_loop.safe, armed = False, False
    if not armed:
        arm()
    global held
    want = (open(HOLD).read().split() if os.path.exists(HOLD) else None) or None  # an empty file counts as no hold
    if want:  # several looks ("idle awake") loop, LOOP_S each, so a shot can be filmed again and again unattended
        want = want[int(time.monotonic() / LOOP_S) % len(want)]
    if want != held:  # filming: hold one look; removing the file hands the LEDs back to the game in its idle look
        held = want
        game_loop.bridge("set_mode", runner.MODES.get(want, 0))
    if not held:
        game_loop.tick()
    time.sleep(0.1)


App.run(user_loop=loop)
