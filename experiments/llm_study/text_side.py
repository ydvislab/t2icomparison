"""Q4 text side (exploratory, PREREG.md): what does the rewriting LLM add, and does it predict the image-side shift?
Usage: python text_side.py   (needs rewrites_*.csv; image-side per-subject deltas from results/q4/per_subject.csv if present)
- Word families: share of rewrites containing at least one word of each pre-specified family (case-insensitive,
  word-stem prefix match; multi-word phrases matched as substrings).
- Text score: CLIP ViT-L/14 text-encoder score of each rewrite and of the original prompt on the 5 frozen aspects
  (cosine to the right pole minus cosine to the left pole; CLIP truncates text to 77 tokens). Per subject, the text
  shift is the median rewrite score minus the original prompt's score, divided by the across-subject SD of the
  original prompts' text scores (a text-side unit; the image scale does not apply to text).
- Spearman correlation over the 24 subjects between the text shift and the image-side Delta of the matching contrast.
Writes results/q4/text_words.csv, text_scores.csv, text_vs_image.csv."""
import os, re, sys
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, pandas as pd, torch
from scipy.stats import spearmanr
from transformers import CLIPModel, CLIPProcessor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model_study", "analysis"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "aspects"))
import q1_primary as q1  # noqa: E402
from aspects import ASPECTS  # noqa: E402

FAMILIES = {
    "lighting": ["light", "lit", "glow", "sunlight", "shadow"],
    "time of day": ["morning", "afternoon", "evening", "sunset", "golden hour", "dusk", "dawn", "night"],
    "cinematic / photographic": ["cinematic", "photograph", "photorealistic", "realistic", "lens",
                                 "depth of field", "bokeh", "mm"],
    "colour": ["warm", "vibrant", "muted", "saturated", "pastel", "color", "colour"],
    "background": ["background", "surrounded", "scene", "environment"],
    "style": ["painting", "illustration", "watercolor", "render", "style"],
}
LLM = f"{q1.DATA}/llm_study"
OUT = os.path.join(q1.REPO, "results", "q4")
IMAGE_CONTRAST = {"mistral": ["P1 klein 4B: original -> FLUX.2 rewrite", "P2 FLUX.2 dev: original -> FLUX.2 rewrite"],
                  "qwen": ["D1 klein 4B: original -> Qwen rewrite"]}


def has(text, words):
    t = text.lower()
    for w in words:
        if " " in w:
            if w in t:
                return True
        elif re.search(r"\b" + re.escape(w), t):
            return True
    return False


@torch.no_grad()
def main():
    os.makedirs(OUT, exist_ok=True)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    path = os.path.join(q1.DATA, "models", "clip-vit-large-patch14")
    model, proc = CLIPModel.from_pretrained(path).to(dev).eval(), CLIPProcessor.from_pretrained(path)
    keep = [x for x in ASPECTS if x["key"] in q1.ASPECTS]

    def emb(texts):
        e = []
        for i in range(0, len(texts), 64):
            f = model.get_text_features(**proc(text=texts[i:i + 64], return_tensors="pt", padding=True,
                                                truncation=True, max_length=77).to(dev))
            e.append(torch.nn.functional.normalize(getattr(f, "pooler_output", f), dim=-1).cpu().numpy())
        return np.concatenate(e)

    L, R = emb([x["left"] for x in keep]), emb([x["right"] for x in keep])
    words, scores, rel = [], [], []
    subjects = None
    for llm in ("mistral", "qwen"):
        p = f"{LLM}/rewrites_{llm}.csv"
        if not os.path.exists(p):
            continue
        W = pd.read_csv(p)
        subjects = list(dict.fromkeys(W.subject))
        for fam, ws in FAMILIES.items():
            words.append(dict(llm=llm, family=fam, share=np.mean([has(t, ws) for t in W.rewrite])))
        words.append(dict(llm=llm, family="median words per rewrite", share=float(W.rewrite.str.split().str.len().median())))
        E, O = emb(list(W.rewrite)), emb(subjects)
        S = pd.DataFrame(E @ R.T - E @ L.T, columns=q1.ASPECTS).assign(subject=W.subject.values, llm=llm)
        S0 = pd.DataFrame(O @ R.T - O @ L.T, columns=q1.ASPECTS, index=subjects)
        unit = S0.std(ddof=1)
        med = S.groupby("subject")[q1.ASPECTS].median().loc[subjects]
        shift = (med - S0) / unit
        scores.append(shift.reset_index(names="subject").assign(llm=llm))
        ps = f"{OUT}/per_subject.csv"
        if os.path.exists(ps):
            P = pd.read_csv(ps)
            for c in IMAGE_CONTRAST[llm]:
                for asp in q1.ASPECTS:
                    x = P[(P.contrast == c) & (P.aspect == asp)].set_index("subject").delta.reindex(subjects)
                    if x.notna().all():
                        r, pv = spearmanr(shift[asp], x)
                        rel.append(dict(llm=llm, contrast=c, aspect=asp, text_shift_median=float(shift[asp].median()),
                                        image_delta_median=float(x.median()), spearman=r, p=pv))
    pd.DataFrame(words).to_csv(f"{OUT}/text_words.csv", index=False, float_format="%.3f")
    pd.concat(scores).to_csv(f"{OUT}/text_scores.csv", index=False, float_format="%.4f")
    pd.DataFrame(rel).to_csv(f"{OUT}/text_vs_image.csv", index=False, float_format="%.3f")
    print(pd.DataFrame(words).to_string(index=False))
    if rel:
        print(pd.DataFrame(rel).to_string(index=False))


if __name__ == "__main__":
    main()
