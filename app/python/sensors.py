"""Real sensors for the Runner: bricks in, game events out. Same poll() and listen() as runner.Stub.

Two App Lab bricks feed it, each with its own Edge Impulse model, plus a plain loudness meter:
  detector  VideoImageClassification, visitor gate classifier, labels empty and visitor
  words     KeywordSpotting, the six riddle words (noise and unknown are ignored)
  meter     Meter below, arecord on the scream mic; no model, the scream challenge is won on loudness alone
The keyword brick calls back with no arguments, so its confidence is the threshold given to the brick.
Brick callbacks must be plain functions (not bound methods) and run on the brick threads, so they only
append to deques; poll() on the game thread does the rest. costume() -> (label, confidence) is optional,
it grabs its own frame (the classifier brick hands none over) and runs at most once a second while a
visitor is there. A visitor score over GATE holds for SEEN_S, the 1 s minimum hold from the R7 video test.
"""
import array, collections, math, subprocess, threading, time

VISITOR = "visitor"
WORDS = ("shadow", "pumpkin", "mirror", "candle", "spider", "scarecrow")
SEEN_S, COSTUME_EVERY_S = 1.0, 1.0  # a detection older than this counts as gone
GATE = 0.5  # P(visitor) over this counts as a detection, as in the Studio test
TAIL_S = 1.0  # the keyword brick scores a rolling 1 s window, so for this long after listen() it still holds the gargoyle's own voice
FLOOR_DB, TOP_DB = -50.0, -12.0  # CAL dBFS of the 0.2 s RMS for an empty and a full spine, set from peaks measured on the board at the fixed mic gain
CHUNK_S, METER_S = 0.2, 10  # one reading per 0.2 s (the MCU redraws at most once per 0.2 s tick anyway); arecord stops itself after METER_S


def loudness(chunk):
    """16-bit mono PCM -> 0 to 100 on the spine, linear in dB between FLOOR_DB and TOP_DB."""
    a = array.array("h", chunk)
    rms = math.sqrt(sum(x * x for x in a) / len(a)) if a else 0
    db = 20 * math.log10(max(rms, 1) / 32768)
    return max(0, min(100, round(100 * (db - FLOOR_DB) / (TOP_DB - FLOOR_DB))))


class Meter:
    """Records only while a scream challenge listens. take() returns the newest reading once, or None."""
    def __init__(self, device="plughw:0,0", rate=16000):
        self.cmd = ["arecord", "-q", "-D", device, "-f", "S16_LE", "-r", str(rate), "-c", "1", "-t", "raw", "-d", str(METER_S)]
        self.n, self.p, self.v = int(rate * CHUNK_S) * 2, None, None

    def start(self):
        if self.p:
            self.p.kill()
        self.v, self.p = None, subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
        threading.Thread(target=self._read, args=(self.p,), daemon=True).start()

    def _read(self, p):
        p.stdout.read(self.n)  # the first chunk can still hold the end of our own line
        while p is self.p and len(c := p.stdout.read(self.n)) == self.n:
            self.v = loudness(c)
        p.wait()  # no zombie arecord once it stops or is killed

    def take(self):
        v, self.v = self.v, None
        return v


class Sensors:
    def __init__(self, detector, meter, words, costume=None, clock=time.monotonic):
        self.clock, self.costume, self.meter, self.heard = clock, costume, meter, collections.deque()
        self.conf, self.seen_at, self.label, self.label_conf, self.label_at = 0.0, -1e9, None, 0.0, -1e9
        self.want = self.answer = None  # set by listen(); None means the mics are ignored
        self.t_listen = 0.0
        detector.on_detect_all(self._detect())
        for w in WORDS:
            words.on_detect(w, self._hear(w))

    def _detect(self):
        def cb(scores):  # {"label": confidence} for the labels over the brick threshold, once per frame
            now, p = self.clock(), scores.get(VISITOR, 0.0)
            if p <= GATE:
                return
            self.conf, self.seen_at = p, now
            if self.costume and now - self.label_at >= COSTUME_EVERY_S:
                self.label_at = now
                try:
                    self.label, self.label_conf = self.costume()
                except Exception:
                    self.label, self.label_conf = None, 0.0
        return cb

    def _hear(self, name):
        # words count only during a riddle, and not while the window holds the tail of our own speech
        return lambda: self.want == "riddle" and self.clock() - self.t_listen >= TAIL_S and self.heard.append(name)

    def listen(self, challenge, answer=None):
        self.heard.clear()
        self.want, self.answer, self.t_listen = challenge, answer, self.clock()
        if challenge == "scream":
            self.meter.start()

    def poll(self):
        now = self.clock()
        here = now - self.seen_at < SEEN_S
        costume = self.label if here and now - self.label_at < 3 * COSTUME_EVERY_S else None
        out = [("visitor", self.conf if here else 0.0, costume, self.label_conf if costume else 0.0)]
        if self.want == "scream":
            v = self.meter.take()
            if v is not None:
                out.append(("loud", v))  # the game decides; readings after the verdict are ignored there
        elif self.want and self.heard:
            out.append(("heard", "win" if self.heard.popleft() == self.answer else "wrong_answer"))
            self.want = None  # one verdict per listen
        return out


def demo():
    class Brick:  # records the callbacks the way the real bricks keep them
        def __init__(self): self.cbs = {}
        def on_detect(self, name, cb): self.cbs[name] = cb
        def on_detect_all(self, cb): self.cbs["all"] = cb

    class FakeMeter:
        v, started = None, 0
        def start(self): self.started += 1
        def take(self): v, self.v = self.v, None; return v

    d, m, w, t = Brick(), FakeMeter(), Brick(), [0.0]
    sn = Sensors(d, m, w, costume=lambda: ("witch", 0.8), clock=lambda: t[0])
    assert sn.poll() == [("visitor", 0.0, None, 0.0)]  # nothing seen yet
    d.cbs["all"]({VISITOR: 0.9})
    assert sn.poll() == [("visitor", 0.9, "witch", 0.8)]
    t[0] += 0.5; d.cbs["all"]({"empty": 0.7})
    assert sn.poll() == [("visitor", 0.9, "witch", 0.8)]  # one empty frame inside the hold changes nothing
    t[0] += 2
    assert sn.poll() == [("visitor", 0.0, None, 0.0)]  # the detection went stale
    sn.listen("scream"); assert m.started == 1 and sn.poll()[1:] == []
    m.v = 73; assert sn.poll()[1:] == [("loud", 73)] and sn.poll()[1:] == []  # each reading once
    t[0] += 1; w.cbs["mirror"](); assert sn.poll()[1:] == []  # words do not count in a scream challenge
    sn.listen("riddle", "mirror"); w.cbs["shadow"](); assert sn.poll()[1:] == []  # still the tail of our own voice
    t[0] += 1; w.cbs["shadow"](); assert sn.poll()[1:] == [("heard", "wrong_answer")]
    w.cbs["mirror"](); assert sn.poll()[1:] == []  # one verdict per listen
    sn.listen("riddle", "mirror"); t[0] += 1; w.cbs["mirror"](); assert sn.poll()[1:] == [("heard", "win")]
    assert m.started == 1  # a riddle does not open the meter
    full = array.array("h", [20000, -20000] * 1600).tobytes()
    assert loudness(bytes(6400)) == 0 and loudness(full) == 100 and loudness(b"") == 0
    print("sensors ok")


if __name__ == "__main__":
    demo()
