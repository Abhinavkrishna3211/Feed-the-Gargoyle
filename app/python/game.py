"""Game state machine from docs/architecture.md. Pure logic: events in, actions out, time passed in.

step(event, now) returns a list of actions for the caller to carry out:
  ("say", category)   play a line of that bank category (cues.pick adds the sound)
  ("mode", name)      Bridge set_mode: idle, listen, win, fail
  ("dispense",)       Bridge dispense
  ("listen",)         start the sound or keyword model; the mic is open from now on
  ("level", pct)      Bridge set_level: spine fill, the time left in the listen window, in steps of 10
  ("fog", ms)         Bridge set_fog: one mist burst, only on a win (the MCU refuses it while listening)
Events: ("visitor", confidence, costume_or_None, costume_conf), ("spoke_done",), ("heard", outcome),
("drop_confirmed",), ("jam",), ("tick",).  outcome is win, too_quiet, wrong_sound or wrong_answer.
"""
import random

WAKE_CONF, WAKE_FRAMES = 0.6, 3
LISTEN_S, COOLDOWN_S, LEAVE_S, DROP_S, FOG_MS = 9.0, 10.0, 5.0, 4.0, 2000
CHALLENGES = ("scream", "clap", "whistle", "riddle")
COSTUMES = {"witch", "ghost", "skeleton", "zombie", "pirate", "princess", "spider-man", "batman",
            "superman", "captain-america"}


class Game:
    def __init__(self, rng=random):
        self.rng, self.state, self.seen, self.t0, self.last_seen, self.retried, self.lvl = rng, "IDLE", 0, 0, 0, False, None

    def go(self, state, now):
        self.state, self.t0, self.lvl = state, now, None

    def step(self, ev, now):
        kind, out = ev[0], []
        if kind == "visitor" and ev[1] >= WAKE_CONF:
            self.last_seen = now
        if kind == "jam" or (self.state == "RESULT" and now - self.t0 > DROP_S and self.retried):
            self.go("COOLDOWN", now)  # the MCU is in its safe state; say so and wait for the cooldown
            return [("say", "jam"), ("mode", "fail")]
        if self.state == "IDLE":
            if kind == "visitor":  # ticks and other events must not reset the count
                self.seen = self.seen + 1 if ev[1] >= WAKE_CONF else 0
            if self.seen >= WAKE_FRAMES:
                self.seen, self.retried, self.hinted = 0, False, False
                self.go("CHALLENGE", now)
                out += [("mode", "listen"), ("say", "greet")]
                if ev[2] in COSTUMES and ev[3] >= WAKE_CONF:
                    out.append(("say", ev[2]))
                self.challenge = self.rng.choice(CHALLENGES)
                out.append(("say", "announce_" + self.challenge) if self.challenge != "riddle" else ("say", "riddle"))
        elif self.state == "CHALLENGE" and kind == "spoke_done":
            self.go("LISTEN", now)
            out.append(("listen",))
        elif self.state == "LISTEN":
            if kind == "heard" and ev[1] == "win":
                self.go("RESULT", now)
                out += [("mode", "win"), ("fog", FOG_MS), ("say", "win"), ("dispense",)]
            elif kind == "heard" and ev[1] == "wrong_answer" and self.challenge == "riddle" and not self.hinted:
                self.hinted = True  # a wrong riddle answer gets the hint and one more try
                self.go("CHALLENGE", now)
                out += [("say", "wrong_answer"), ("say", "hint")]
            elif kind == "heard":
                self.go("COOLDOWN", now)
                out += [("mode", "fail"), ("say", ev[1])]
            elif now - self.t0 > LISTEN_S:
                self.go("COOLDOWN", now)
                out += [("mode", "fail"), ("say", "timeout")]
            else:
                pct = max(0, round(10 * (1 - (now - self.t0) / LISTEN_S)) * 10)
                if pct != self.lvl:  # Bridge traffic on change only
                    self.lvl = pct
                    out.append(("level", pct))
        elif self.state == "RESULT":
            if kind == "drop_confirmed":
                self.go("COOLDOWN", now)
                out.append(("say", "goodbye"))
            elif now - self.t0 > DROP_S and not self.retried:
                self.retried = True
                self.t0 = now
                out.append(("dispense",))
        elif self.state == "COOLDOWN" and now - self.t0 > COOLDOWN_S and now - self.last_seen > LEAVE_S:
            self.go("IDLE", now)
            out.append(("mode", "idle"))
        return out


def demo():
    g, t = Game(random.Random(1)), 0.0
    see = lambda c=0.9, lab="witch", lc=0.8: ("visitor", c, lab, lc)
    for _ in range(2):  # two frames are not enough to wake
        assert g.step(see(), t) == []; t += .5
    acts = g.step(see(), t)
    assert g.state == "CHALLENGE" and acts[:3] == [("mode", "listen"), ("say", "greet"), ("say", "witch")], acts
    assert ("listen",) in g.step(("spoke_done",), t + 4) and g.state == "LISTEN"
    assert g.step(("tick",), t + 4) == [("level", 100)] and g.step(("tick",), t + 4.1) == []  # level on change only
    assert g.step(("tick",), t + 4 + LISTEN_S / 2) == [("level", 50)]
    acts = g.step(("heard", "win"), t + 6)  # win path
    assert g.state == "RESULT" and ("dispense",) in acts and ("fog", 2000) in acts
    assert g.step(("drop_confirmed",), t + 7) == [("say", "goodbye")]
    assert g.step(see(), t + 12) == [] and g.state == "COOLDOWN"  # still there: stay
    assert g.step(("tick",), t + 40) == [("mode", "idle")] and g.state == "IDLE"
    # wrong answer, unsure costume (no costume line), then timeout path
    g = Game(random.Random(1)); [g.step(see(lc=0.3), i) for i in range(3)]
    assert ("say", "witch") not in g.step(("tick",), 3) and g.state == "CHALLENGE"
    g.step(("spoke_done",), 4)
    assert g.step(("heard", "too_quiet"), 5) == [("mode", "fail"), ("say", "too_quiet")]
    g = Game(random.Random(1)); [g.step(see(), i) for i in range(3)]; g.step(("spoke_done",), 4)
    assert g.step(("tick",), 4 + LISTEN_S + 1) == [("mode", "fail"), ("say", "timeout")]
    # no drop: retry once, then jam
    g = Game(random.Random(1)); [g.step(see(), i) for i in range(3)]; g.step(("spoke_done",), 4); g.step(("heard", "win"), 5)
    assert g.step(("tick",), 5 + DROP_S + 1) == [("dispense",)]
    assert g.step(("tick",), 5 + 2 * DROP_S + 2) == [("say", "jam"), ("mode", "fail")]
    # riddle: wrong answer gives the hint and one more try, the second wrong answer ends the visit
    class R:
        choice = lambda self, x: "riddle"
    g = Game(R()); [g.step(see(), i) for i in range(3)]; g.step(("spoke_done",), 4)
    assert g.step(("heard", "wrong_answer"), 5) == [("say", "wrong_answer"), ("say", "hint")] and g.state == "CHALLENGE"
    assert g.step(("spoke_done",), 12) == [("listen",)]
    assert g.step(("heard", "wrong_answer"), 14) == [("mode", "fail"), ("say", "wrong_answer")]
    print("game ok")


if __name__ == "__main__":
    demo()
