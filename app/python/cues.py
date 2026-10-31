"""Which sound goes with which line, and when. Pure logic: the caller plays the files.

CUES maps a line category to (group, "before" or "after"). Groups hold file stems that rotate,
never the same file twice in a row.
The files are the limited (louder) clips from scripts/sound_clips.py --limit 6, all in one folder. Categories with no entry (announce_*) get no sound, because
the mic listens right after the line.
"""
import random

GROUPS = {
    "stone_door": ["stone_door_0"],
    "long_laugh": ["eviljest_gargoyle_0", "qubodupevillaughter_gargoyle_0"],
    "short_laugh": ["evil_laugh3_gargoyle_0", "laugh-evil-1_0_gargoyle_0", "evil_laugh3-filtered_gargoyle_0"],
    "growl": ["growl_0_0"],
    "creak": ["creaky_door_hinge_0", "creaky_door_hinge_1"],
}
CUES = {
    "greet": ("stone_door", "before"), "win": ("long_laugh", "after"),
    "wrong_answer": ("short_laugh", "after"), "goodbye": ("short_laugh", "after"),
    "too_quiet": ("growl", "after"), "timeout": ("growl", "after"), "jam": ("growl", "after"),
    "wrong_sound": ("creak", "after"),
}
COSTUMES = ("witch", "ghost", "skeleton", "zombie", "pirate", "princess", "spider-man", "batman", "superman",
            "captain-america")  # the 10 costume categories of the line bank
CUES.update({c: ("creak", "before") for c in COSTUMES})

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
    assert pick("greet") == ("stone_door_0", "before")
    for _ in range(50):
        a = pick("wrong_answer")[0]
        assert a != _last.get("prev"), a
        _last["prev"] = a
    assert pick("win")[1] == "after" and pick("witch")[1] == "before"
    print("cues ok")
