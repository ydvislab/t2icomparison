"""Prompt set for the model study (docs/PROMPTS.md). Single source for open- and closed-model generation."""

# (category, subject); subjects marked * in comments were used in the pilot experiments
MAIN = [
    ("people", "a doctor"), ("people", "a person reading a book"), ("people", "a musician"), ("people", "a traveler"),
    ("animals", "a dog"), ("animals", "a bird on a branch"), ("animals", "a cat"), ("animals", "a horse"),
    ("objects", "a car"), ("objects", "a cup of coffee"), ("objects", "a bicycle"), ("objects", "a bowl of fruit"),
    ("indoor", "a kitchen"), ("indoor", "a living room"), ("indoor", "a library"), ("indoor", "a restaurant"),
    ("outdoor", "a house"), ("outdoor", "a city street"), ("outdoor", "a mountain"), ("outdoor", "a beach"),
    ("activity", "a market"), ("activity", "a train station"), ("activity", "a birthday party"), ("activity", "a picnic"),
]

# control prompts: (id, prompt, subject, aspect key, expected direction: -1 = left pole, +1 = right pole)
CONTROLS = [
    ("C1", "a house at night", "a house", "time", +1),
    ("C2", "a black and white photograph of a dog", "a dog", "sat", -1),
    ("C3", "an oil painting of a cup of coffee", "a cup of coffee", "medium", +1),
    ("C4", "a close-up of a bicycle", "a bicycle", "shot", -1),
    ("C5", "a kitchen in warm golden light", "a kitchen", "light", +1),
    ("C6", "a city street seen from above", "a city street", "angle", +1),
]

# aspects implied by the prompt; excluded from location/spread statistics for that subject
EXCLUDED = {s: ("inout",) for s in ["a kitchen", "a living room", "a library", "a restaurant",
                                     "a city street", "a mountain", "a beach", "a picnic"]}


def jobs(n_main, n_control):
    """All generation jobs. Seeds: 100000 * prompt index + k, shared by every open-model group."""
    out = []
    for i, (cat, s) in enumerate(MAIN):
        out += [dict(job=f"m{i:02d}_{k:02d}", kind="main", category=cat, subject=s, prompt=s,
                     seed=100000 * i + k, k=k) for k in range(n_main)]
    for i, (cid, p, s, aspect, sign) in enumerate(CONTROLS):
        out += [dict(job=f"{cid.lower()}_{k:02d}", kind="control", category="control", subject=s, prompt=p,
                     seed=100000 * (50 + i) + k, k=k) for k in range(n_control)]
    return out
