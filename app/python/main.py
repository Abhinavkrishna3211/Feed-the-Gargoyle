import os
import statistics
import time
import json

from arduino.app_utils import *

# Create python/bench.on to run the Bridge latency check once instead of the heartbeat.
HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.exists(os.path.join(HERE, "bench.on"))
WARMUP, N = 10, 200

done = False


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


def loop():
    global done
    if BENCH:
        if not done:
            bench()
            done = True
        time.sleep(1)
        return
    time.sleep(1)
    Bridge.call("heartbeat")


App.run(user_loop=loop)
