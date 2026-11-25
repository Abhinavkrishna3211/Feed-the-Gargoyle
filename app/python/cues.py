"""Which sound goes with which line, and when. Pure logic: the caller plays the files.

CUES maps a line category to (group, "before" or "after"). Groups hold file stems that rotate,
never the same file twice in a row.
The files are the limited (louder) clips from scripts/sound_clips.py --limit 6, all in one folder.
Nothing may play after a line the mic listens right after (announce_scream, riddle, hint): those get a cue before or none.
The laughs carry the mood: a sly chuckle after the riddle rules (the riddle follows), one before the scream rules,
a gloating laugh when time runs out or a guess is wrong, a big laugh when the visitor wins.
"""
import random

from game import COSTUMES

GROUPS = {
    "stone_door": ["stone_door_0"],
    "long_laugh": ["eviljest_gargoyle_0", "qubodupevillaughter_gargoyle_0"],
    "short_laugh": ["evil_laugh3_gargoyle_0", "laugh-evil-1_0_gargoyle_0", "evil_laugh3-filtered_gargoyle_0"],
    "growl": ["growl_0_0"],
    "creak": ["creaky_door_hinge_0", "creaky_door_hinge_1"],
}
CUES = {
    "greet": ("stone_door", "before"), "win": ("long_laugh", "after"), "win_scream": ("long_laugh", "after"),
    "wrong_answer": ("short_laugh", "after"), "lose": ("long_laugh", "after"), "goodbye": ("short_laugh", "after"),
    "too_quiet": ("growl", "after"), "timeout": ("short_laugh", "after"), "jam": ("growl", "after"),
    "announce_riddle": ("short_laugh", "after"), "announce_scream": ("short_laugh", "before"),
}
CUES.update({c: ("creak", "before") for c in COSTUMES})  # every costume and props line

_last = {}


def pick(category):
    """Return (file stem, "before" or "after") or None."""
    if category not in CUES:
        return None
    group, when = CUES[category]
    files = [f for f in GROUPS[group] if f != _last.get(group)] or GROUPS[group]
    _last[group] = random.choice(files)
    return _last[group], when


if __name__ == "__main__":
    assert pick("announce_clap") is None
    assert pick("announce_riddle")[1] == "after" and pick("announce_scream")[1] == "before" and pick("riddle") is None
    assert pick("greet") == ("stone_door_0", "before")
    for _ in range(50):
        a = pick("wrong_answer")[0]
        assert a != _last.get("prev"), a
        _last["prev"] = a
    assert pick("win")[1] == "after" and pick("witch")[1] == "before"
    print("cues ok")
