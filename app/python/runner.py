"""Game loop glue: sensors give events, Game decides, Voice and Bridge carry out the actions.

Runner(game, voice, call, sensors).tick(now) runs one pass. call(name, *args) is Bridge.call.
sensors.poll() returns a list of game events; sensors.listen(challenge, answer) opens the loudness meter or the keyword model.
voice.say blocks until the audio has finished, so after the actions of CHALLENGE are done the
runner sends spoke_done itself and listening starts only then. Bridge errors are counted, not raised:
the MCU watchdog owns the safe state. Stub is a stand-in for the models until they are trained.
"""
import random, time

MODES = {"idle": 0, "listen": 1, "win": 2, "fail": 3, "awake": 4}
CALL_S = 1.0  # a Bridge call lost to a damaged packet must not hold the loop for the 10 s default
RETRY = {"set_mode", "set_level", "set_fog"}  # safe to send twice; dispense is not, a timeout does not say whether it ran


class Runner:
    def __init__(self, game, voice, call, sensors, clock=time.monotonic):
        self.game, self.voice, self.call, self.sensors, self.clock, self.errors, self.inbox, self.safe, self.seen = game, voice, call, sensors, clock, 0, [], False, None

    def bridge(self, name, *args):
        for _ in range(2 if name in RETRY else 1):
            try:
                r = self.call(name, *args, timeout=CALL_S)
                self.safe = self.safe or r == -2  # the MCU refused: it is in its safe state, the caller must re-arm it
                if r is None or r < 0:
                    print(f"BRIDGE {name}{args} -> {r}", flush=True)
                return r
            except Exception as e:
                self.errors += 1
                print(f"BRIDGE {name}{args} failed: {e!r}", flush=True)

    def act(self, actions):
        for a in actions:
            if a[0] == "say":
                self.voice.say(a[1])  # False means no rendered line; the hand-written set is still to do
            elif a[0] == "mode":
                self.bridge("set_mode", MODES[a[1]])
            elif a[0] in ("level", "fog"):
                self.bridge("set_" + a[0], a[1])
            elif a[0] == "dispense":
                self.bridge("dispense")
            elif a[0] == "listen":
                self.sensors.listen(self.game.challenge, self.voice.answer)  # the riddle's answer word is only meant for a riddle

    def push(self, ev):  # events from the MCU (drop_confirmed, jam) arrive here
        self.inbox.append(ev)

    def tick(self):
        evs, self.inbox = self.inbox + self.sensors.poll() + [("tick",)], []
        for ev in evs:
            acts = self.game.step(ev, self.clock())
            if ("mode", "awake") in acts:
                print(f"WAKE {ev}", flush=True)  # visitor confidence and costume label that woke it
            self.act(acts)
            if self.game.state == "CHALLENGE" or (self.game.state == "RESULT" and ("dispense",) in acts):  # the say actions above have finished playing (in RESULT, the dispense too)
                self.act(self.game.step(("spoke_done",), self.clock()))  # read after the audio, so the listen window starts now
        if self.game.state != self.seen:
            self.seen = self.game.state
            print(f"STATE {self.seen} t={self.clock():.1f} bridge_errors={self.errors}", flush=True)


class Stub:
    """A visitor appears every 'gap' seconds for 'stay' seconds; a scream gives random loudness, a riddle a random answer."""
    def __init__(self, rng=random, gap=20.0, stay=15.0):
        self.rng, self.gap, self.stay, self.t, self.on, self.pending, self.want = rng, gap, stay, 0.0, False, None, None

    def poll(self):
        self.t += 0.1
        self.on = self.t % (self.gap + self.stay) > self.gap
        out = [("visitor", 0.9 if self.on else 0.0, None, 0.0)]
        if self.want == "scream":
            self.v = min(self.cap, self.v + self.rng.randint(0, 15))  # a scream builds up; a quiet visitor tops out at 70
            out.append(("loud", self.v))
        elif self.pending is not None:
            self.pending -= 0.1
            if self.pending <= 0:
                out.append(("heard", self.rng.choice(("win", "wrong_answer"))))
                self.pending = None
        return out

    def listen(self, challenge=None, answer=None):
        self.want, self.pending, self.v, self.cap = challenge, 2.0, 0, self.rng.choice((100, 100, 70))


def demo():
    import game as g

    class Voice:
        answer = "shadow"
        def __init__(self): self.said = []
        def say(self, c): self.said.append(c); return True

    calls = []
    def call(name, *a, timeout=None):
        calls.append((name, *a))
        if name == "dispense":
            return None
        if name == "boom":
            raise RuntimeError
    v, s = Voice(), Stub(random.Random(3), gap=1.0, stay=30.0)
    t = [0.0]
    r = Runner(g.Game(random.Random(3)), v, call, s, clock=lambda: t[0])
    for _ in range(400):
        t[0] += 0.1
        r.tick()
    said = [x for x in v.said if x != "guess"]  # the generic tease follows greet when no costume or prop is sure
    assert said[0] == "greet" and (said[1].startswith("announce_") or said[1] == "riddle"), v.said
    assert ("set_mode", 1) in calls and ("set_mode", 2) in calls, calls
    assert any(c[0] == "set_level" for c in calls) and ("set_fog", 2000) in calls, calls
    assert any(x in v.said for x in ("win", "win_scream", "too_quiet", "wrong_answer", "timeout")), v.said
    r.push(("drop_confirmed",)); assert ("drop_confirmed",) in r.inbox
    r.call = lambda *a, **k: 1 / 0  # a failing Bridge is counted, the loop keeps going
    r.act([("mode", "win"), ("dispense",)])
    r.call = lambda *a, **k: -2; r.act([("level", 50)]); assert r.safe  # a refusal is flagged for re-arming
    r.call = lambda *a, **k: 1 / 0; r.errors = 0; r.act([("mode", "win"), ("dispense",)])
    assert r.errors == 3  # set_mode is tried twice, dispense once
    print("runner ok")


if __name__ == "__main__":
    demo()
