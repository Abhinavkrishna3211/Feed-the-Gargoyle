"""Play a line of a bank category with its sound cue. Blocks until the audio has finished.

Voice(bank_dir, sound_dir).say("win") picks a rendered line (never the same one twice in a row),
looks up its cue in cues.py and plays cue, line, cue in the right order. The caller opens the mic
only after say() returns, so the mic never hears the gargoyle (docs/architecture.md, LISTEN).
Returns False when the category has no rendered line, so the caller can use its fallback set.
bank_dir holds <category>_<n>.wav as written by scripts/render_bank.py.
"""
import random, re, subprocess
from collections import defaultdict
from pathlib import Path

import cues

DEVICE = "plughw:1,0"  # USB sound card, ALSA card 1 on the board
SPEAKER_MIXER = ["amixer", "-q", "-c", "1", "sset", "Speaker", "30"]  # full level; cues and lines were tuned for it


def aplay(path):
    subprocess.run(SPEAKER_MIXER, check=False)  # the card came up at half level (15) on the board; set it every time
    subprocess.run(["aplay", "-q", "-D", DEVICE, str(path)], check=True)


class Voice:
    def __init__(self, bank_dir, sound_dir, play=aplay, rng=random):
        self.sound_dir, self.play, self.rng, self.last = Path(sound_dir), play, rng, {}
        self.lines, self.riddles, self.answer = defaultdict(list), {}, None
        for f in sorted(Path(bank_dir).glob("*.wav")):
            m = re.fullmatch(r"(riddle|hint)_([a-z]+)", f.stem)  # riddle_<answer>.wav, hint_<answer>.wav
            if m:
                self.riddles[m.group(1), m.group(2)] = f
            else:
                self.lines[re.sub(r"_\d+$", "", f.stem)].append(f)

    def say(self, category):
        """riddle picks a riddle and remembers its answer word; hint plays that riddle's hint."""
        if category == "riddle":
            words = sorted(w for k, w in self.riddles if k == "riddle")
            if not words:
                return False
            self.answer = self.rng.choice([w for w in words if w != self.answer] or words)
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
        choice = [f for f in files if f != self.last.get(category)] or files
        line = self.last[category] = self.rng.choice(choice)
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
    assert Voice(d, "snd", play=log.append).say("hint") is False  # no riddle asked yet
    print("voice ok")
