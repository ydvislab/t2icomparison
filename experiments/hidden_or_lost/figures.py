"""Summary figure for the Hidden-or-Lost pilot (3 panels, validated categorical slots 1-3)."""
import os, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../results/hidden_or_lost")
M = ["sd15", "sdxl_turbo", "klein4b"]
LAB = {"sd15": "SD1.5 (2022)", "sdxl_turbo": "SDXL-Turbo (2023)", "klein4b": "FLUX.2 klein 4B (2026)"}
COL = {"sd15": "#2a78d6", "sdxl_turbo": "#eb6834", "klein4b": "#1baf7a"}
MK = {"sd15": "o", "sdxl_turbo": "s", "klein4b": "^"}
INK, MUTED, GRID, BG = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.color": GRID, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": BG, "axes.facecolor": BG,
                     "legend.frameon": False, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})
div = pd.read_csv(f"{OUT}/vendi_by_subject.csv", index_col=0)[M]
dims = pd.read_csv(f"{OUT}/dimensions.csv")
R = pd.read_csv(f"{OUT}/reach_ci.csv")
fig, ax = plt.subplots(1, 3, figsize=(12, 3.9))
# (a) default diversity per subject
x = np.arange(len(M))
for s, row in div.iterrows():
    ax[0].plot(x, row.values, color=MUTED, alpha=0.35, lw=1)
for i, m in enumerate(M):
    ax[0].scatter([i] * len(div), div[m], color=COL[m], marker=MK[m], s=26, zorder=3, edgecolor=BG, lw=0.8)
    ax[0].plot([i - 0.18, i + 0.18], [div[m].mean()] * 2, color=INK, lw=2.2, zorder=4)
ax[0].set_xticks(x, [LAB[m].replace(" (", "\n(") for m in M]); ax[0].set_ylabel("Vendi score (DINOv2), 16 seeds")
ax[0].set_title("(a) Default diversity, 12 minimal prompts\n(thick bar = mean, grey = one subject)", color=INK)
# (b) default entropy by dimension
order = ["quality", "color", "framing", "medium", "lighting"]
w = 0.26
for i, m in enumerate(M):
    v = dims[dims.model == m].set_index("dim").loc[order, "entropy"]
    ax[1].bar(np.arange(len(order)) + (i - 1) * w, v.values, width=w - 0.03, color=COL[m], label=LAB[m])
ax[1].set_xticks(np.arange(len(order)), order); ax[1].set_ylabel("Normalised entropy (VLM-labelled)")
ax[1].set_title("(b) What the model decides for you:\nentropy of unspecified dimensions", color=INK); ax[1].legend(fontsize=7.5, loc="upper right")
# (c) reachability when explicitly asked
for i, m in enumerate(M):
    for j, typ in enumerate(["typical", "atypical"]):
        r = R[(R.model == m) & (R.typ == typ)].iloc[0]
        xx = j + (i - 1) * 0.18
        ax[2].errorbar(xx, r.rate, yerr=[[r.rate - r.lo], [r.hi - r.rate]], fmt=MK[m], color=COL[m], ms=7,
                       mec=BG, mew=0.8, capsize=3, lw=1.5, label=LAB[m] if j == 0 else None)
ax[2].set_xticks([0, 1], ["typical requests\n(night, b/w, oil, wide...)", "atypical requests\n(crayon, amateur, ugly, low-q)"])
ax[2].set_ylim(0.5, 1.0); ax[2].set_ylabel("Compliance when explicitly asked (95% CI)")
ax[2].set_title("(c) Reachability: can it still do it when asked?", color=INK)
fig.tight_layout(); fig.savefig(f"{OUT}/hidden_or_lost_summary.png", dpi=170)
print("saved")
