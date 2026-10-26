"""Data figure of the PacificVis paper: Fig. 3, the evidence for the three failure modes (Sec. 4).
Usage: python make_data_figures.py   (reads results/q5/truth.csv, results/encoder_check/verdicts.csv,
results/q5/grid_check_items.csv; writes figures/fig3_failures.png and .pdf)
(a) F1b: per-subject saturation shift of SDXL -> SDXL-Turbo around a pooled shift inside the margin.
(b) F1c: klein-base 4B guidance 1 -> 4, pooled shift and spread ratio per aspect under CLIP (filled) and SigLIP 2 (hollow).
(c) F2/F3: on the same 48 grid pairs, null pairs reported as different and real shifts read correctly, VLMs vs people.
Colours are the audit tool's (poles teal/ochre, ink); encoders differ by marker fill, not by hue."""
import csv, math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "figures")
INK, INK2, MUTED, GRID, BAND = "#0b1220", "#3d4a5c", "#8792a6", "#e8edf4", "#eef3fb"
LEFT, RIGHT = "#0d9488", "#a16207"   # pole colours of the tool: muted (teal) <-> vivid (ochre)
NAME = {"sat": "saturation", "medium": "medium", "shot": "shot", "tone": "tone", "bg": "background"}
plt.rcParams.update({"font.family": "Arial", "font.size": 7, "axes.edgecolor": MUTED, "axes.linewidth": .6,
                     "xtick.color": INK2, "ytick.color": INK2, "xtick.major.width": .6, "ytick.major.width": .6,
                     "axes.labelcolor": INK2, "axes.titlesize": 7.5, "axes.titleweight": "bold", "axes.titlecolor": INK})


def rows(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def subjects():
    import importlib.util
    spec = importlib.util.spec_from_file_location("prompts", os.path.join(REPO, "experiments", "model_study", "prompts.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return [s for _, s in m.MAIN]


def clean(ax, grid_x=True):
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    if grid_x:
        ax.grid(axis="x", color=GRID, lw=.6); ax.set_axisbelow(True)


def main():
    subj = subjects()
    fig = plt.figure(figsize=(7.0, 2.4))
    # columns: (a), spacer for (b)'s aspect labels, (b) shift, (b) spread, spacer for (c)'s labels, (c)
    G6 = fig.add_gridspec(1, 6, width_ratios=[1.3, .3, 1, .8, .5, .85], wspace=.08, left=.02, right=.93, top=.8, bottom=.17)
    gs = [G6[0], G6[2], G6[3], G6[5]]

    # (a) hidden reversals
    ax = fig.add_subplot(gs[0])
    T = [r for r in rows("results/q5/truth.csv") if r["contrast"] == "sdxl_turbo" and r["aspect"] == "sat"]
    per = sorted((float(r["delta"]), subj[int(r["unit"][1:])], r["shift"]) for r in T if r["level"] == "subject")
    pooled = next(float(r["delta"]) for r in T if r["level"] == "pooled")
    ax.axvspan(-.5, .5, color=BAND, lw=0)
    ax.axvline(0, color=MUTED, lw=.6)
    for i, (d, s, sh) in enumerate(per):
        c = RIGHT if d >= .5 else LEFT if d <= -.5 else MUTED   # beyond the margin, as the tool's reversal badge
        ax.plot([0, d], [i, i], color=c, lw=1.0, solid_capstyle="round")
        ax.plot(d, i, "o", ms=3.2, color=c, mec="white", mew=.5)
    for i, (d, s, sh) in enumerate(per):
        if s in ("a horse", "a bird on a branch", "a cup of coffee", "a car"):
            ax.text(d + .12 if d > 0 else .35, i, s.replace("a ", "", 1), va="center", ha="left", fontsize=6, color=INK2)
    ax.axvline(pooled, color=INK, lw=1.0, ls=(0, (3, 2)))
    ax.text(pooled, len(per) + .3, f"pooled {pooled:+.2f}", ha="center", va="bottom", fontsize=6, color=INK)
    n_up, n_dn = sum(d >= .5 for d, _, _ in per), sum(d <= -.5 for d, _, _ in per)
    ax.text(.02, .97, f"beyond the margin:\n{n_up} more vivid\n{n_dn} more muted", transform=ax.transAxes, ha="left", va="top", fontsize=6, color=INK2)
    ax.set_yticks([]); ax.set_ylim(-1, len(per) + 1.6); ax.set_xlim(-3.9, 3.4)
    ax.set_xlabel("saturation shift per subject (scale units)")
    ax.set_title("(a) F1b: a pooled shift hides reversals\nSDXL → SDXL-Turbo, saturation", loc="left")
    clean(ax)
    ax.spines["left"].set_visible(False)

    # (b) encoder dependence, klein-base 4B guidance 1 -> 4
    V = [r for r in rows("results/encoder_check/verdicts.csv") if r["family"] == "Q1" and r["contrast"] == "klein-base 4B"]
    asp = ["sat", "medium", "shot", "tone", "bg"]
    for k, (eff, lab, xf, band) in enumerate([("location", "pooled shift", lambda v: v, (-.5, .5)),
                                               ("spread", "spread ratio (log scale)", math.exp, (1 / 1.5, 1.5))]):
        ax = fig.add_subplot(gs[1 + k])
        ax.axvspan(*band, color=BAND, lw=0)
        ax.axvline(0 if eff == "location" else 1, color=MUTED, lw=.6)
        for j, a in enumerate(asp):
            r = next(x for x in V if x["aspect"] == a and x["effect"] == eff)
            for enc, dy, fill in (("clip", -.13, INK), ("siglip", .13, "white")):
                e, lo, hi = (xf(float(r[f"{q}_{enc}"])) for q in ("estimate", "lo90", "hi90"))
                ax.plot([lo, hi], [j + dy] * 2, color=INK, lw=.9)
                ax.plot(e, j + dy, "o", ms=3.6, mfc=fill, mec=INK, mew=.8)
        ax.set_yticks(range(len(asp))); ax.set_yticklabels([NAME[a] for a in asp] if k == 0 else [])
        ax.invert_yaxis(); ax.tick_params(axis="y", length=0)
        if eff == "spread":
            ax.set_xscale("log"); ax.set_xticks([.4, .67, 1, 1.5]); ax.set_xticklabels(["×0.4", "×0.67", "×1", "×1.5"]); ax.minorticks_off()
        ax.set_xlabel(lab)
        clean(ax)
        if k == 0:
            ax.set_title("(b) F1c: what moves depends on the encoder\nklein-base 4B, guidance 1 → 4", loc="left")
        else:
            ax.plot([], [], "o", ms=3.6, mfc=INK, mec=INK, label="CLIP"); ax.plot([], [], "o", ms=3.6, mfc="white", mec=INK, label="SigLIP 2")
            ax.legend(loc="lower right", frameon=False, fontsize=6, handletextpad=.2, borderaxespad=.1)

    # (c) language alone and eyes alone, on the same 48 grid pairs
    ax = fig.add_subplot(gs[3])
    G = rows("results/q5/grid_check_items.csv")
    nul = [r for r in G if r["contrast"].startswith("null_")]
    real = [r for r in G if not r["contrast"].startswith("null_") and r["question"] == "shift" and r["truth32"] in ("left", "right")]
    who = [("qwen", "Qwen3.5-4B"), ("mistral", "Mistral-24B"), ("people", "people (majority)")]
    for k, (title, data, ok) in enumerate([("null pairs: difference reported", nul, lambda r, w: r[w] not in ("none", "same", "")),
                                            ("real shifts: direction correct", real, lambda r, w: r[w] == r["truth32"])]):
        for j, (w, lab) in enumerate(who):
            v = sum(ok(r, w) for r in data) / len(data)
            y = k * 4 + j
            ax.barh(y, v, height=.62, color=INK if w != "people" else MUTED, lw=0)
            ax.text(v + .02, y, f"{sum(ok(r, w) for r in data)}/{len(data)}", va="center", fontsize=6, color=INK2)
        ax.text(0, k * 4 - .85, title, fontsize=6.3, color=INK, fontweight="bold")
    ax.set_xlim(0, 1.25); ax.set_ylim(7, -1.4)
    ax.set_yticks([0, 1, 2, 4, 5, 6]); ax.set_yticklabels([l for _, l in who] * 2, fontsize=6); ax.tick_params(axis="y", length=0)
    ax.set_xticks([0, .5, 1]); ax.set_xticklabels(["0", "50%", "100%"])
    ax.set_title("(c) F2, F3: VLMs vs people\nsame 48 grid pairs", loc="left")
    clean(ax); ax.spines["left"].set_visible(False)

    os.makedirs(OUT, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"fig3_failures.{ext}"), dpi=400)
    print("fig3_failures written")


if __name__ == "__main__":
    main()
