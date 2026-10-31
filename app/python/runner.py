"""Game loop glue: sensors give events, Game decides, Voice and Bridge carry out the actions.

Runner(game, voice, call, sensors).tick(now) runs one pass. call(name, *args) is Bridge.call.
sensors.poll() returns a list of game events; sensors.listen() opens the sound or keyword model.
voice.say blocks until the audio has finished, so after the actions of CHALLENGE are done the
runner sends spoke_done itself and listening starts only then. Bridge errors are counted, not raised:
the MCU watchdog owns the safe state. Stub is a stand-in for the models until they are trained.
"""
import random, time

MODES = {"idle": 0, "listen": 1, "win": 2, "fail": 3}


class Runner:
    def __init__(self, game, voice, call, sensors, clock=time.monotonic):
        self.game, self.voice, self.call, self.sensors, self.clock, self.errors, self.inbox = game, voice, call, sensors, clock, 0, []

    def bridge(self, name, *args):
        try:
            return self.call(name, *args)
        except Exception:
            self.errors += 1

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
                self.sensors.listen(self.voice.answer)  # the keyword model gets the riddle's answer word, or None

    def push(self, ev):  # events from the MCU (drop_confirmed, jam) arrive here
        self.inbox.append(ev)

    def tick(self):
        evs, self.inbox = self.inbox + self.sensors.poll() + [("tick",)], []
        for ev in evs:
            self.act(self.game.step(ev, self.clock()))
            if self.game.state == "CHALLENGE":  # the say actions above have finished playing
                self.act(self.game.step(("spoke_done",), self.clock()))  # read after the audio, so the listen window starts now


class Stub:
    """A visitor appears every 'gap' seconds for 'stay' seconds; the answer after listening is random."""
    def __init__(self, rng=random, gap=20.0, stay=15.0):
        self.rng, self.gap, self.stay, self.t, self.on, self.pending = rng, gap, stay, 0.0, False, None

    def poll(self):
        self.t += 0.1
        self.on = self.t % (self.gap + self.stay) > self.gap
        out = [("visitor", 0.9 if self.on else 0.0, None, 0.0)]
        if self.pending is not None:
            self.pending -= 0.1
            if self.pending <= 0:
                out.append(("heard", self.rng.choice(("win", "win", "too_quiet", "wrong_sound", "wrong_answer"))))
                self.pending = None
        return out

    def listen(self, answer=None):
        self.pending = 2.0


def demo():
    import game as g

    class Voice:
        answer = "shadow"
        def __init__(self): self.said = []
        def say(self, c): self.said.append(c); return True

    calls = []
    def call(name, *a):
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
    assert v.said[0] == "greet" and (v.said[1].startswith("announce_") or v.said[1] == "riddle"), v.said
    assert ("set_mode", 1) in calls and ("set_mode", 2) in calls, calls
    assert any(c[0] == "set_level" for c in calls) and ("set_fog", 2000) in calls, calls
    assert any(x in v.said for x in ("win", "too_quiet", "wrong_sound", "wrong_answer")), v.said
    r.push(("drop_confirmed",)); assert ("drop_confirmed",) in r.inbox
    r.call = lambda *a: 1 / 0  # a failing Bridge is counted, the loop keeps going
    r.act([("mode", "win"), ("dispense",)])
    assert r.errors == 2
    print("runner ok")


if __name__ == "__main__":
    demo()
