"""Game state machine from docs/architecture.md. Pure logic: events in, actions out, time passed in.

step(event, now) returns a list of actions for the caller to carry out:
  ("say", category)   play a line of that bank category (cues.pick adds the sound)
  ("mode", name)      Bridge set_mode: idle, listen, win, fail, awake
  ("dispense",)       Bridge dispense
  ("listen",)         start the sound or keyword model; the mic is open from now on
  ("level", pct)      Bridge set_level: spine fill. Riddle: the time left in the listen window, in steps of 10. Scream: the loudness meter
  ("fog", ms)         Bridge set_fog: one mist burst, only on a win (the MCU refuses it while listening)
Events: ("visitor", confidence, costume_or_None, costume_conf), ("spoke_done",), ("heard", outcome),
("loud", pct), ("drop_confirmed",), ("jam",), ("tick",).  outcome is win or wrong_answer (riddle only).
A scream is won on loudness alone: WIN_PCT on HOLD readings in a row. A scream that never gets there ends too_quiet.
"""
import random

WAKE_CONF, WAKE_FRAMES = 0.6, 10  # CAL 10 polls in a row (about 1.2 s at the board loop rate) so someone walking up wakes it, a flicker from a person sitting nearby does not
LISTEN_S, COOLDOWN_S, LEAVE_S, DROP_S, FOG_MS = 9.0, 10.0, 8.0, 4.0, 2000
MAX_COOLDOWN_S = 30.0  # back to sleep even if someone stays in view; they must step out and back in to wake it again
CHALLENGES = ("scream", "riddle")
WIN_PCT, HOLD = 94, 3  # scream: 94 is the level where the sketch lights the 8th (top) spine plate, held for 3 readings (0.3 s) so one bang does not win
FORCED = None  # filming: main.py sets this from python/costume.txt, and every visitor is greeted as that costume
COSTUMES = {"batman", "captain_america", "iron_man", "spiderman", "superman", "wonder_woman", "pirate", "princess",
            "skeleton", "witch", "zombie",  # costume model labels; its 12th label, none, comes back as None
            "hat", "glasses", "crown", "scarf"}  # props model labels; each label is also its line bank category
# eye_mask (props) has no rendered lines yet, so it gets the generic tease


class Game:
    def __init__(self, rng=random):
        self.rng, self.state, self.seen, self.t0, self.last_seen, self.retried, self.lvl = rng, "IDLE", 0, 0, 0, False, None
        self.armed = True  # False after a forced sleep until the camera sees nobody

    def go(self, state, now):
        self.state, self.t0, self.lvl, self.loud = state, now, None, 0

    def step(self, ev, now):
        kind, out = ev[0], []
        if kind == "visitor" and ev[1] >= WAKE_CONF:
            self.last_seen = now
        if kind == "jam" or (self.state == "RESULT" and now - self.t0 > DROP_S and self.retried):
            self.go("COOLDOWN", now)  # the MCU is in its safe state; say so and wait for the cooldown
            return [("say", "jam"), ("mode", "fail")]
        if self.state == "IDLE":
            if kind == "visitor":  # ticks and other events must not reset the count
                self.armed = self.armed or ev[1] < WAKE_CONF
                self.seen = self.seen + 1 if ev[1] >= WAKE_CONF and self.armed else 0
            if self.seen >= WAKE_FRAMES:
                self.seen, self.retried, self.hinted = 0, False, False
                self.go("CHALLENGE", now)
                out += [("mode", "awake"), ("say", "greet")]  # spine and eyes wake with the visitor
                if FORCED:
                    out.append(("say", FORCED))
                elif ev[2] in COSTUMES and ev[3] >= WAKE_CONF:
                    out.append(("say", ev[2]))
                else:  # neither model is sure what they wear: a generic tease that claims nothing
                    out.append(("say", "guess"))
                self.challenge = self.rng.choice(CHALLENGES)
                out.append(("say", "announce_" + self.challenge))  # the rules first, so even a small child knows how to win
                if self.challenge == "riddle":
                    out.append(("say", "riddle"))
        elif self.state == "CHALLENGE" and kind == "spoke_done":
            self.go("LISTEN", now)
            out += [("mode", "listen"), ("listen",)]  # the spine goes dark: only the scream (or the riddle clock) lights it
        elif self.state == "LISTEN":
            if kind == "loud":
                self.loud = self.loud + 1 if ev[1] >= WIN_PCT else 0
            if (kind == "heard" and ev[1] == "win") or self.loud >= HOLD:
                self.go("RESULT", now)
                out += [("mode", "win"), ("fog", FOG_MS), ("say", "win" if self.challenge == "riddle" else "win_scream"), ("dispense",)]
            elif kind == "heard" and ev[1] == "wrong_answer" and self.challenge == "riddle" and not self.hinted:
                self.hinted = True  # a wrong riddle answer gets the hint and one more try
                self.go("CHALLENGE", now)
                out += [("say", "wrong_answer"), ("say", "hint")]
            elif kind == "heard":  # the second wrong answer ends the visit with a closing line, not "try again"
                self.go("COOLDOWN", now)
                out += [("mode", "fail"), ("say", "lose")]
            elif now - self.t0 > LISTEN_S:
                self.go("COOLDOWN", now)
                out += [("mode", "fail"), ("say", "too_quiet" if self.challenge == "scream" else "timeout")]
            else:
                if self.challenge == "scream":
                    pct = ev[1] if kind == "loud" else self.lvl  # the spine is the meter
                else:  # the spine counts down
                    pct = max(0, round(10 * (1 - (now - self.t0) / LISTEN_S)) * 10)
                if pct is not None and pct != self.lvl:  # Bridge traffic on change only
                    self.lvl = pct
                    out.append(("level", pct))
        elif self.state == "RESULT":
            if kind == "spoke_done":  # the win line has played and the dispense just went out: the drop wait starts now
                self.t0 = now
            elif kind == "drop_confirmed":
                self.go("COOLDOWN", now)
                out.append(("say", "goodbye"))
            elif now - self.t0 > DROP_S and not self.retried:
                self.retried = True
                self.t0 = now
                out.append(("dispense",))
        elif self.state == "COOLDOWN" and now - self.t0 > COOLDOWN_S and (now - self.last_seen > LEAVE_S or now - self.t0 > MAX_COOLDOWN_S):
            self.armed = now - self.last_seen > LEAVE_S
            self.go("IDLE", now)
            out.append(("mode", "idle"))
        return out


def demo():
    class Pick:
        def __init__(self, c): self.c = c
        def choice(self, x): return self.c
    see = lambda c=0.9, lab="witch", lc=0.8: ("visitor", c, lab, lc)

    def awake(challenge, lc=0.8):
        g = Game(Pick(challenge))
        for i in range(WAKE_FRAMES - 1):  # one frame short is not enough to wake
            assert g.step(see(lc=lc), i / 10) == []
        return g, g.step(see(lc=lc), 1)
    g, acts = awake("riddle")
    assert g.state == "CHALLENGE" and acts == [("mode", "awake"), ("say", "greet"), ("say", "witch"), ("say", "announce_riddle"), ("say", "riddle")], acts
    t = 4
    assert g.step(("spoke_done",), t) == [("mode", "listen"), ("listen",)] and g.state == "LISTEN"
    assert g.step(("tick",), t) == [("level", 100)] and g.step(("tick",), t + 0.1) == []  # level on change only
    assert g.step(("tick",), t + LISTEN_S / 2) == [("level", 50)]
    acts = g.step(("heard", "win"), t + 6)  # win path
    assert g.state == "RESULT" and ("dispense",) in acts and ("fog", 2000) in acts and ("say", "win") in acts
    assert g.step(("drop_confirmed",), t + 7) == [("say", "goodbye")]
    assert g.step(see(), t + 12) == [] and g.state == "COOLDOWN"  # still there: stay
    assert g.step(("tick",), t + 40) == [("mode", "idle")] and g.state == "IDLE"
    # someone who never leaves: asleep after MAX_COOLDOWN_S, no new wake until they step out of view
    g, _ = awake("scream"); g.step(("spoke_done",), 4); g.step(("tick",), 4 + LISTEN_S + 1)
    for i in range(400):
        g.step(see(), 15 + i / 10)
    assert g.state == "IDLE" and not g.armed
    g.step(("visitor", 0.0, None, 0.0), 56)
    for i in range(WAKE_FRAMES):
        acts = g.step(see(), 57 + i / 10)
    assert g.state == "CHALLENGE" and ("mode", "awake") in acts
    # riddle: unsure costume gets the generic tease; a wrong answer gives the hint and one more try, the second ends the visit
    g, acts = awake("riddle", lc=0.3)
    assert ("say", "witch") not in acts and ("say", "guess") in acts
    g.step(("spoke_done",), 4)
    assert g.step(("heard", "wrong_answer"), 5) == [("say", "wrong_answer"), ("say", "hint")] and g.state == "CHALLENGE"
    assert g.step(("spoke_done",), 12) == [("mode", "listen"), ("listen",)]
    assert g.step(("heard", "wrong_answer"), 14) == [("mode", "fail"), ("say", "lose")]
    g, _ = awake("riddle"); g.step(("spoke_done",), 4)
    assert g.step(("tick",), 4 + LISTEN_S + 1) == [("mode", "fail"), ("say", "timeout")]
    # scream: the spine follows the meter, a single loud reading is not enough, two in a row win
    g, acts = awake("scream")
    assert ("say", "announce_scream") in acts
    g.step(("spoke_done",), 4)
    assert g.step(("tick",), 4.1) == []  # no countdown during a scream
    assert g.step(("loud", 40), 4.2) == [("level", 40)] and g.step(("loud", 40), 4.4) == []
    assert g.step(("loud", 95), 4.6) == [("level", 95)] and g.step(("loud", 60), 4.8) == [("level", 60)]
    g.step(("loud", WIN_PCT), 4.9); g.step(("loud", WIN_PCT), 5.0)
    acts = g.step(("loud", 100), 5.1)
    assert g.state == "RESULT" and ("dispense",) in acts and ("mode", "win") in acts and ("say", "win_scream") in acts
    g, _ = awake("scream"); g.step(("spoke_done",), 4); g.step(("loud", 70), 5)
    assert g.step(("tick",), 4 + LISTEN_S + 1) == [("mode", "fail"), ("say", "too_quiet")]
    # no drop: retry once, then jam
    g, _ = awake("riddle"); g.step(("spoke_done",), 4); g.step(("heard", "win"), 5)
    assert g.step(("spoke_done",), 9) == [] and g.step(("tick",), 9 + DROP_S - 1) == []  # the drop wait counts from the end of the win line
    assert g.step(("tick",), 5 + DROP_S + 1 + 4) == [("dispense",)]
    assert g.step(("tick",), 5 + 2 * DROP_S + 2 + 4) == [("say", "jam"), ("mode", "fail")]
    print("game ok")


if __name__ == "__main__":
    demo()
