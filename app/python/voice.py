"""Play a line of a bank category with its sound cue. Blocks until the audio has finished.

Voice(bank_dir, sound_dir).say("win") picks a rendered line (every line of a category once before any repeats),
looks up its cue in cues.py and plays cue, line, cue in the right order. The caller opens the mic
only after say() returns, so the mic never hears the gargoyle (docs/architecture.md, LISTEN).
Returns False when the category has no rendered line, so the caller can use its fallback set.
bank_dir holds <category>_<n>.wav as written by scripts/render_bank.py.
"""
import random, re, subprocess
from collections import defaultdict
from pathlib import Path

import cues

DEVICE = "plughw:CARD=Device,DEV=0"  # USB sound card by name: the card number swaps with the camera between boots
SPEAKER_MIXER = ["amixer", "-q", "-c", "Device", "sset", "Speaker", "30"]  # full mixer; the clearer lines (LOUD 2.5) sit about 2.5 dB under the old ones, roughly 80 percent loudness. 80% of the range (24) cut 9 dB and was too quiet


TALK_S = 0.2  # one loudness value per MCU personality tick (TICK_MS in the sketch)


def envelope(path):
    """Loudness of a 16-bit wav in TALK_S frames, 0 to 100 in steps of 10, scaled to the file's own loud parts.
    The eyes follow this; the MCU slew-limits it, so pauses fade the eyes and a phrase swells them. [] if not 16-bit."""
    import array, math, wave
    with wave.open(str(path)) as w:
        if w.getsampwidth() != 2:
            return []
        n = int(w.getframerate() * TALK_S) * w.getnchannels()
        a = array.array("h", w.readframes(w.getnframes()))
    rms = [math.sqrt(sum(x * x for x in a[i:i + n]) / len(a[i:i + n])) for i in range(0, len(a), n)]
    ref = sorted(rms)[int(len(rms) * 0.9)] or 1  # the 90th percentile frame is full glow, so one shout does not dim the rest
    return [min(100, round(r / ref * 10) * 10) if r > ref * 0.08 else 0 for r in rms]  # under 8 percent is silence


def aplay(path):
    subprocess.run(SPEAKER_MIXER, check=False)  # the card came up at half level (15) on the board; set it every time
    subprocess.run(["aplay", "-q", "-D", DEVICE, str(path)], check=True)


class Voice:
    def __init__(self, bank_dir, sound_dir, play=aplay, rng=random):
        self.sound_dir, self.play, self.rng, self.last, self.decks = Path(sound_dir), play, rng, {}, {}
        self.lines, self.riddles, self.answer = defaultdict(list), {}, None
        for f in sorted(Path(bank_dir).glob("*.wav")):
            m = re.fullmatch(r"(riddle|hint)_([a-z]+)", f.stem)  # riddle_<answer>.wav, hint_<answer>.wav
            if m:
                self.riddles[m.group(1), m.group(2)] = f
            else:
                self.lines[re.sub(r"_\d+$", "", f.stem)].append(f)

    def deal(self, key, items):
        """Shuffled deck per category: every item once before any repeats, and a new deck never starts with the last one."""
        deck = self.decks.get(key)
        if not deck:
            deck = self.decks[key] = self.rng.sample(items, len(items))
            if len(deck) > 1 and deck[-1] == self.last.get(key):
                deck[0], deck[-1] = deck[-1], deck[0]
        self.last[key] = deck.pop()
        return self.last[key]

    def say(self, category):
        """riddle picks a riddle and remembers its answer word; hint plays that riddle's hint."""
        if category == "riddle":
            words = sorted(w for k, w in self.riddles if k == "riddle")
            if not words:
                return False
            self.answer = self.deal("riddle", words)
            self.play(self.riddles["riddle", self.answer])
            return True
        if category == "hint":
            f = self.riddles.get(("hint", self.answer))
            return bool(f and not self.play(f))
        files = self.lines.get(category)
        if not files:
            cue = cues.pick(category)  # nothing rendered for it: at least make the cue sound
            if cue:
                self.play(self.sound_dir / f"{cue[0]}.wav")
            return False
        line = self.deal(category, files)
        cue = cues.pick(category)
        before, after = (cue[0] if cue[1] == "before" else None, cue[0] if cue[1] == "after" else None) if cue else (None, None)
        for f in (before and self.sound_dir / f"{before}.wav", line, after and self.sound_dir / f"{after}.wav"):
            if f:
                self.play(f)
        return True


if __name__ == "__main__":
    import tempfile
    d = Path(tempfile.mkdtemp())
    for n in ("greet_0", "greet_1", "win_0", "announce_clap_0", "wrong_answer_0"):
        (d / f"{n}.wav").touch()
    log = []
    v = Voice(d, "snd", play=log.append, rng=random.Random(0))
    assert v.say("greet") and [p.stem for p in log] == ["stone_door_0", log[1].stem] and log[1].stem.startswith("greet_")
    log.clear(); v.say("win"); assert [p.stem for p in log][0] == "win_0" and log[1].stem.endswith("_0") and len(log) == 2
    log.clear(); v.say("announce_clap"); assert [p.stem for p in log] == ["announce_clap_0"]  # silent category
    log.clear(); v.say("greet"); v.say("greet")
    assert log[1].stem != log[3].stem  # same line never twice in a row
    assert v.say("nothing") is False
    for n in ("riddle_shadow", "riddle_mirror", "hint_shadow", "hint_mirror"):
        (d / f"{n}.wav").touch()
    v = Voice(d, "snd", play=log.append, rng=random.Random(0))
    log.clear(); assert v.say("riddle") and v.answer in ("shadow", "mirror") and log[0].stem == "riddle_" + v.answer
    first = v.answer; log.clear(); assert v.say("hint") and log[0].stem == "hint_" + first
    v.say("riddle"); assert v.answer != first  # never the same riddle twice in a row
    for n in ("riddle_candle", "riddle_spider"):
        (d / f"{n}.wav").touch()
    v = Voice(d, "snd", play=log.append, rng=random.Random(1))
    asked = []
    for _ in range(12):
        v.say("riddle"); asked.append(v.answer)
    assert all(sorted(asked[i:i + 4]) == ["candle", "mirror", "shadow", "spider"] for i in (0, 4, 8))  # all four before any repeat
    assert all(a != b for a, b in zip(asked, asked[1:]))  # and never twice in a row across decks
    import array, wave
    with wave.open(str(d / "env.wav"), "wb") as w:  # 0.4 s loud, 0.4 s silence, 0.2 s quiet, at 8 kHz
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
        w.writeframes(array.array("h", [8000, -8000] * 1600 + [0] * 3200 + [2000, -2000] * 800).tobytes())
    assert envelope(d / "env.wav") == [100, 100, 0, 0, 20], envelope(d / "env.wav")
    assert Voice(d, "snd", play=log.append).say("hint") is False  # no riddle asked yet
    print("voice ok")
