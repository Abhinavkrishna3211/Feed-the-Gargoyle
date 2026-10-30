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
    subprocess.run(["aplay", "-q", "-D", DEVICE, str(path)], check=True)


class Voice:
    def __init__(self, bank_dir, sound_dir, play=aplay, rng=random):
        self.sound_dir, self.play, self.rng, self.last = Path(sound_dir), play, rng, {}
        self.lines = defaultdict(list)
        for f in sorted(Path(bank_dir).glob("*.wav")):
            self.lines[re.sub(r"_\d+$", "", f.stem)].append(f)

    def say(self, category):
        files = self.lines.get(category)
        if not files:
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
    print("voice ok")
