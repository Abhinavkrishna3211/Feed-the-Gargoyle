"""Real sensors for the Runner: bricks in, game events out. Same poll() and listen() as runner.Stub.

Three App Lab bricks feed it, each with its own Edge Impulse model:
  detector  VideoObjectDetection, FOMO visitor gate, label VISITOR
  sound     AudioClassification, classes scream, clap, whistle (other is ignored)
  words     KeywordSpotting, the six riddle words (noise and unknown are ignored)
The audio bricks call back with no arguments, so their confidence is the threshold given to the brick.
Brick callbacks must be plain functions (not bound methods) and run on the brick threads, so they only
append to deques; poll() on the game thread does the rest. costume(frame_jpeg) -> (label, confidence)
is optional, it runs at most once a second on the frame that comes with a detection.
"""
import collections, time

VISITOR = "visitor"
SOUNDS = ("scream", "clap", "whistle")
WORDS = ("shadow", "pumpkin", "mirror", "candle", "spider", "scarecrow")
SEEN_S, COSTUME_EVERY_S = 1.0, 1.0  # a detection older than this counts as gone


class Sensors:
    def __init__(self, detector, sound, words, costume=None, clock=time.monotonic):
        self.clock, self.costume, self.heard = clock, costume, collections.deque()
        self.conf, self.seen_at, self.label, self.label_conf, self.label_at = 0.0, -1e9, None, 0.0, -1e9
        self.want = self.answer = None  # set by listen(); None means the mics are ignored
        detector.on_detect_all(self._detect())
        for s in SOUNDS:
            sound.on_detect(s, self._hear(s))
        for w in WORDS:
            words.on_detect(w, self._hear(w))

    def _detect(self):
        def cb(dets, frame=None):
            now = self.clock()
            self.conf, self.seen_at = max([d["confidence"] for d in dets.get(VISITOR, [])] or [0.0]), now
            if self.costume and frame and now - self.label_at >= COSTUME_EVERY_S:
                self.label_at = now
                try:
                    self.label, self.label_conf = self.costume(frame)
                except Exception:
                    self.label, self.label_conf = None, 0.0
        return cb

    def _hear(self, name):
        return lambda: self.want and self.heard.append(name)

    def listen(self, challenge, answer=None):
        self.heard.clear()
        self.want, self.answer = challenge, answer

    def poll(self):
        now = self.clock()
        here = now - self.seen_at < SEEN_S
        costume = self.label if here and now - self.label_at < 3 * COSTUME_EVERY_S else None
        out = [("visitor", self.conf if here else 0.0, costume, self.label_conf if costume else 0.0)]
        if self.want and self.heard:
            got = self.heard.popleft()
            if self.want == "riddle":
                out.append(("heard", "win" if got == self.answer else "wrong_answer")) if got in WORDS else None
            elif got in SOUNDS:
                out.append(("heard", "win" if got == self.want else "wrong_sound"))
            if len(out) > 1:
                self.want = None  # one verdict per listen
        return out


def demo():
    class Brick:  # records the callbacks the way the real bricks keep them
        def __init__(self): self.cbs = {}
        def on_detect(self, name, cb): self.cbs[name] = cb
        def on_detect_all(self, cb): self.cbs["all"] = cb

    d, s, w, t = Brick(), Brick(), Brick(), [0.0]
    sn = Sensors(d, s, w, costume=lambda f: ("witch", 0.8), clock=lambda: t[0])
    assert sn.poll() == [("visitor", 0.0, None, 0.0)]  # nothing seen yet
    d.cbs["all"]({VISITOR: [{"confidence": 0.7}, {"confidence": 0.9}]}, b"jpg")
    assert sn.poll() == [("visitor", 0.9, "witch", 0.8)]
    t[0] += 2
    assert sn.poll() == [("visitor", 0.0, None, 0.0)]  # the detection went stale
    s.cbs["clap"]()
    sn.listen("clap")
    assert sn.poll()[1:] == []  # sounds before listen() were dropped
    s.cbs["scream"](); assert sn.poll()[1:] == [("heard", "wrong_sound")]
    s.cbs["clap"](); assert sn.poll()[1:] == []  # one verdict per listen
    sn.listen("clap"); s.cbs["clap"](); assert sn.poll()[1:] == [("heard", "win")]
    sn.listen("riddle", "mirror"); w.cbs["shadow"](); assert sn.poll()[1:] == [("heard", "wrong_answer")]
    sn.listen("riddle", "mirror"); s.cbs["clap"](); w.cbs["mirror"](); assert sn.poll()[1:] == [] and sn.poll()[1:] == [("heard", "win")]
    print("sensors ok")


if __name__ == "__main__":
    demo()
