"""Reference-prompt calibration (anchors), docs/RESEARCH_PROPOSAL.md §4.2.

For one subject and one aspect, the anchor prompts explicitly request each pole of the aspect. A reference model's
median aspect score on left-pole requests (L) and right-pole requests (R) defines the calibrated scale
x = (median - L) / (R - L) for that subject and aspect.

The pilot tests 2 aspects x 6 subjects x 2 poles x 3 phrasings per pole, so that the phrasing used in the full anchor set
is chosen on evidence (separation, side effects on other aspects, agreement between reference models) rather than by
taste. Phrasing 0 of each pole repeats the CLIP pole text from aspects/aspects.py; phrasings 1 and 2 use other words,
so a phrasing that works only because it echoes the scorer's text can be detected.
"""

# aspect key -> pole ("left"/"right") -> phrasings; {s} is the subject from prompts.MAIN
PILOT_TEMPLATES = {
    "light": {
        "left": ["{s}, in cool blue light", "{s}, lit by cold bluish light", "{s}, with a cool blue color cast"],
        "right": ["{s}, in warm golden light", "{s}, lit by warm amber light", "{s}, with a warm golden color cast"],
    },
    "shot": {
        "left": ["an extreme close-up of {s}", "{s}, seen from very close up", "{s}, filling the whole frame"],
        "right": ["a wide shot of {s} from far away", "{s}, seen from a great distance", "{s}, small in a wide view"],
    },
}

# one subject per category of prompts.MAIN
PILOT_SUBJECTS = ["a doctor", "a dog", "a cup of coffee", "a kitchen", "a city street", "a market"]
PILOT_SEEDS = 8


def pilot_jobs(n_seeds=PILOT_SEEDS):
    """Anchor pilot jobs. Seeds are paired within a subject: every aspect, pole and phrasing of one subject uses the
    same seed list (100000 * subject index + 90000 + k), which is disjoint from the study's main and control seeds."""
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from prompts import MAIN  # noqa: E402
    index = {s: i for i, (_, s) in enumerate(MAIN)}
    cat = dict((s, c) for c, s in MAIN)
    out = []
    for s in PILOT_SUBJECTS:
        i = index[s]
        for aspect, poles in PILOT_TEMPLATES.items():
            for pole, phrasings in poles.items():
                for v, tpl in enumerate(phrasings):
                    out += [dict(job=f"a{i:02d}_{aspect}_{pole[0]}{v}_{k:02d}", kind="anchor", category=cat[s], subject=s,
                                 prompt=tpl.format(s=s), aspect=aspect, pole=pole, phrasing=v,
                                 seed=100000 * i + 90000 + k, k=k) for k in range(n_seeds)]
    return out


if __name__ == "__main__":
    J = pilot_jobs()
    print(len(J), "jobs;", len({j["prompt"] for j in J}), "prompts")
    for j in J[:3] + J[-3:]:
        print(j)
