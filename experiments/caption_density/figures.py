"""Figures for the caption-density / guidance / distillation study (run with system python3: needs matplotlib + PIL)."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
DATA_ROOT = os.environ.get("T2IC_DATA", os.path.expanduser("~/va4ext"))  # external data drive (images, models)

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "../../results/caption_density")
DATA = os.environ.get("HOL_DATA", os.path.join(DATA_ROOT, "caption_density"))
P = pd.read_csv(f"{RES}/per_subject.csv")

ORDER = [  # (condition, label, group)
    ("sd15_cfg1_min", "SD1.5\nCFG 1", "sd"), ("sd15_cfg75_min", "SD1.5\nCFG 7.5", "sd"),
    ("sd15_cfg75_dense", "SD1.5 7.5\ncaption", "sd"), ("sd15_cfg75_open", "SD1.5 7.5\n'any style'", "sd"),
    ("kbase_cfg1_min", "base\nCFG 1", "kb"), ("kbase_cfg1_dense", "base 1\ncaption", "kb"),
    ("kbase_cfg4_min", "base\nCFG 4", "kb"),
    ("klein_min", "klein\n(distilled)", "k"), ("klein_dense", "klein\ncaption", "k"), ("klein_open", "klein\n'any style'", "k"),
]
COL = {"sd": "#7a8796", "kb": "#3b6fb6", "k": "#c8553d"}

fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
for ax, metric, title in [(axes[0], "vendi", "Default diversity (DINOv2 Vendi)"),
                          (axes[1], "dim_entropy", "VLM dimension entropy (5 generic dims)")]:
    for i, (c, lab, g) in enumerate(ORDER):
        v = P[P.condition == c][metric]
        ax.bar(i, v.mean(), color=COL[g], width=0.7, alpha=0.85)
        ax.scatter([i] * len(v), v, s=10, color="black", alpha=0.5, zorder=3)
    ax.set_xticks(range(len(ORDER)))
    ax.set_xticklabels([o[1] for o in ORDER], fontsize=7.5)
    ax.set_title(title, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
fig.suptitle("6 minimal subjects x 8 seeds per condition (bars = mean, dots = subjects; base = FLUX.2 klein-base 4B, undistilled)", fontsize=9)
fig.tight_layout()
fig.savefig(f"{RES}/caption_density_summary.png", dpi=150)

# example grid: "a doctor" (subject index 0), 8 seeds, four conditions
rows = [("sd15_cfg1_min", "SD1.5, CFG 1"), ("kbase_cfg1_min", "klein-base, CFG 1"),
        ("kbase_cfg4_min", "klein-base, CFG 4"), ("klein_min", "klein (distilled)")]
T = 128
W = Image.new("RGB", (T * 8, T * len(rows)), "white")
for r, (c, _) in enumerate(rows):
    for k in range(8):
        im = Image.open(f"{DATA}/{c}/s00_{k:02d}.png").convert("RGB").resize((T, T))
        W.paste(im, (k * T, r * T))
fig2, ax2 = plt.subplots(figsize=(10, 5.4))
ax2.imshow(W); ax2.set_xticks([])
ax2.set_yticks([T * r + T / 2 for r in range(len(rows))]); ax2.set_yticklabels([l for _, l in rows], fontsize=9)
ax2.set_title('"a doctor", 8 seeds per row', fontsize=10)
fig2.tight_layout()
fig2.savefig(f"{RES}/examples_doctor.jpg", dpi=130)
print("saved")
