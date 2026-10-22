"""Statistical figures of the manuscript, drawn from the committed result files (no images, no server data).

  fig_q1_guidance   Q1: per-subject shift and spread ratio for guidance 1 -> 4 in klein-base 4B and Qwen-Image-2512,
                    with the frozen margins, the pooled estimate and its 90% interval from results/q1/primary.csv
  fig_validation    Human validation of the language-defined aspects, rounds 1-3 (Table 1 as a figure)
  fig_vlm           Q5: VLM answers against the audit, and the null control

Usage: python3 make_figures.py   (writes PNG and PDF next to this script)
Colours: A/B-neutral ink for the study figures; the two VLMs use validated categorical slots (aqua #1baf7a,
violet #6250d6; dataviz validator: CVD and normal-vision separation pass, contrast warn -> every series is direct-labelled
and also differs by marker shape).
"""
import json, math, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.join(REPO, "results")
INK, INK2, MUTED, FAINT, BAND = "#1f2328", "#4b5260", "#8a909a", "#c9cdd4", "#eef0f3"
QWEN, MISTRAL = "#1baf7a", "#6250d6"
ASP = ["sat", "medium", "shot", "tone", "bg"]
NAME = {"sat": "saturation", "medium": "medium", "shot": "shot", "tone": "tone", "bg": "background", "mood": "mood",
        "inout": "indoor/outdoor", "light": "lighting", "angle": "viewpoint", "time": "time of day", "clean": "clutter",
        "dof": "depth of field", "center": "composition", "quality": "quality", "style": "style",
        "cand_detail": "VLM: level of detail", "cand_texture": "VLM: surface texture", "cand_contrast": "VLM: contrast",
        "cand_ideal": "VLM: natural vs idealized", "cand_sharp": "VLM: sharpness", "cand_lightdrama": "VLM: lighting character"}
POLES = {"sat": ("muted", "vivid"), "medium": ("photo", "painting"), "shot": ("close-up", "wide"),
         "tone": ("modern", "vintage"), "bg": ("plain", "busy")}
M_LOC, M_LR = 0.5, math.log(1.5)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": FAINT, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white", "axes.facecolor": "white", "savefig.dpi": 300})


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(HERE, f"{name}.{ext}"), bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def fig_q1():
    P = pd.read_csv(f"{RES}/q1/primary.csv")
    S = pd.read_csv(f"{RES}/q1/per_subject.csv")
    fams = list(P.family.unique())
    # aspects validated for each family's configurations (annotation rounds 1-2): Qwen-Image is a round-2 configuration
    validated = {fams[0]: set(ASP), fams[1]: {"sat", "medium", "shot"}}
    xm = max(2.0, float(S.delta.abs().max()) * 1.08)
    ym = max(math.log(2.5), float(S.lr.abs().max()) * 1.08)
    fig, axs = plt.subplots(len(fams), len(ASP), figsize=(7.2, 3.3), sharex=True, sharey=True)
    for i, fam in enumerate(fams):
        for j, a in enumerate(ASP):
            ax = axs[i, j]
            ok = a in validated[fam]
            ax.axvspan(-M_LOC, M_LOC, color=BAND, lw=0, zorder=0)
            ax.axhspan(-M_LR, M_LR, color=BAND, lw=0, zorder=0)
            ax.axvline(0, color=FAINT, lw=.6, zorder=1); ax.axhline(0, color=FAINT, lw=.6, zorder=1)
            s = S[(S.family == fam) & (S.aspect == a)]
            ax.scatter(s.delta, s.lr, s=9, color=INK2 if ok else FAINT, alpha=.55, lw=0, zorder=2)
            loc = P[(P.family == fam) & (P.aspect == a) & (P.effect == "location")].iloc[0]
            spr = P[(P.family == fam) & (P.aspect == a) & (P.effect == "spread")].iloc[0]
            col = INK if ok else MUTED
            ax.plot([loc.lo90, loc.hi90], [spr.estimate] * 2, color=col, lw=1.2, zorder=3)
            ax.plot([loc.estimate] * 2, [spr.lo90, spr.hi90], color=col, lw=1.2, zorder=3)
            ax.scatter([loc.estimate], [spr.estimate], marker="D", s=26, color="white", edgecolor=col, lw=1.2, zorder=4)
            txt = f"{loc.estimate:+.2f} [{loc.lo90:+.2f}, {loc.hi90:+.2f}]\n×{math.exp(spr.estimate):.2f} [{math.exp(spr.lo90):.2f}, {math.exp(spr.hi90):.2f}]"
            ax.text(.03, .97, txt, transform=ax.transAxes, va="top", ha="left", fontsize=6.3, color=col)
            verdicts = [v for v in (loc.verdict, spr.verdict) if v in ("displaced", "concentrated", "widened")]
            ax.text(.97, .03, " · ".join(verdicts) if ok else "not validated", transform=ax.transAxes, va="bottom", ha="right",
                    fontsize=6.5, color=INK if ok and verdicts else MUTED, fontweight="bold" if ok and verdicts else "normal")
            ax.set_xlim(-xm, xm); ax.set_ylim(-ym, ym)
            yt = [math.log(v) for v in (1 / 2, 1 / 1.5, 1, 1.5, 2)]
            ax.set_yticks(yt); ax.set_yticklabels(["×0.5", "×0.67", "×1", "×1.5", "×2"])
            if i == 0:
                ax.set_title(NAME[a], fontsize=8.5, color=INK, pad=4)
            if i == len(fams) - 1:
                ax.set_xlabel(f"shift\n{POLES[a][0]} ← → {POLES[a][1]}", fontsize=7)
            if j == 0:
                ax.set_ylabel(f"{fam}\nspread ratio B / A", fontsize=7)
    fig.suptitle("Raising guidance from 1 to 4: per-subject shift (scale units) and spread ratio; shaded = frozen margins; "
                 "diamond = median over subjects with its 90% interval", fontsize=7.5, color=INK2, y=1.02)
    fig.tight_layout(w_pad=.4, h_pad=.6)
    save(fig, "fig_q1_guidance")


def fig_validation():
    rounds = [("Round 1: first six configurations", f"{RES}/annotation_study/aspect_check.csv"),
              ("Round 2: later six configurations", f"{RES}/annotation_round2/aspect_check.csv"),
              ("Round 3: rewritten images and VLM-proposed axes", f"{RES}/annotation_round3/aspect_check.csv")]
    frames = [(t, pd.read_csv(p)) for t, p in rounds if os.path.exists(p)]
    order = ["sat", "medium", "shot", "tone", "bg", "mood", "inout", "light", "angle", "time", "clean", "dof", "center", "quality", "style"]
    fig, axs = plt.subplots(1, len(frames), figsize=(7.4, 3.0), sharex=True)
    for ax, (title, f) in zip(np.atleast_1d(axs), frames):
        f = f.copy()
        f["rank"] = [order.index(a) if a in order else 100 + i for i, a in enumerate(f.aspect)]
        f = f.sort_values("rank").reset_index(drop=True)
        y = np.arange(len(f))[::-1]
        ax.axvline(.75, color=MUTED, lw=.7, ls=(0, (3, 2)), zorder=1)
        for yi, r in zip(y, f.itertuples()):
            ok = bool(r.reliable)
            ax.plot([r.agree_lo, r.agree_hi], [yi, yi], color=INK2 if ok else FAINT, lw=1.1, zorder=2)
            ax.scatter([r.agree_clip], [yi], s=22, color=INK if ok else "white", edgecolor=INK if ok else MUTED, lw=1, zorder=3)
            ax.text(1.02, yi, f"{r.cant_tell:.2f}", va="center", ha="left", fontsize=6.3, color=INK2 if r.cant_tell <= .4 else "#c0564b")
        lab = [NAME.get(a, a) for a in f.aspect]
        ax.set_yticks(y); ax.set_yticklabels(lab, fontsize=7)
        ax.set_xlim(0, 1); ax.set_xticks([0, .5, .75, 1]); ax.set_xticklabels(["0", "0.5", "", "1"])
        ax.set_title(title, fontsize=7.5, color=INK, loc="left")
        ax.set_xlabel("agreement with CLIP", fontsize=6.8)
    fig.suptitle("Human validation of the language-defined aspects on large-gap pairs: agreement with CLIP with its 95% interval; "
                 "numbers = share of \"can't tell\" (red above 0.40).\nFilled = passes the rule fixed before labelling "
                 "(agreement ≥ 0.75, dashed line; can't tell ≤ 0.40)", fontsize=7, color=INK2, y=1.06)
    fig.tight_layout(w_pad=3.5)
    save(fig, "fig_validation")


def fig_vlm():
    S = pd.read_csv(f"{RES}/q5/summary.csv")
    acc = [("subject", "shift", "per subject: shift"), ("subject", "variety", "per subject: variety"),
           ("pooled", "shift", "pooled: shift"), ("pooled", "variety", "pooled: variety")]
    null = [("subject", "null control: shift reported", "per subject: shift reported"),
            ("subject", "null control: variety reported", "per subject: variety reported"),
            ("pooled", "null control: shift reported", "pooled: shift reported"),
            ("pooled", "null control: variety reported", "pooled: variety reported")]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.0), sharey=False)
    for ax, rows, col, title in [(axs[0], acc, "accuracy", "Accuracy against the audit (validated aspects)"),
                                 (axs[1], null, "rate", "Null control: same configuration on both sides")]:
        y = np.arange(len(rows))[::-1]
        for yi, (lev, q, lab) in zip(y, rows):
            for vlm, c, mk, dy in [("qwen", QWEN, "o", .12), ("mistral", MISTRAL, "s", -.12)]:
                r = S[(S.vlm == vlm) & (S.level == lev) & (S.question == q)]
                if len(r):
                    v = float(r.iloc[0][col]); n = int(r.iloc[0]["n"])
                    ax.plot([0, v], [yi + dy] * 2, color=c, lw=1, alpha=.35)
                    ax.scatter([v], [yi + dy], marker=mk, s=22, color=c, zorder=3)
                    ax.text(v + .02, yi + dy, f"{v:.2f}", va="center", fontsize=6.2, color=INK2)
            ax.text(-.02, yi, lab, ha="right", va="center", fontsize=7, color=INK2)
        ax.set_yticks([]); ax.set_xlim(0, 1.12); ax.set_xticks([0, .25, .5, .75, 1])
        ax.spines["left"].set_visible(False)
        ax.set_title(title, fontsize=7.5, color=INK, loc="left", x=-.02 if ax is axs[0] else -.02)
    axs[0].set_xlabel("share of answers that match the audit", fontsize=6.8)
    axs[1].set_xlabel("share of answers that report a difference (truth: none)", fontsize=6.8)
    for ax in axs:
        ax.set_position(ax.get_position())
    from matplotlib.lines import Line2D
    hs = [Line2D([], [], marker="o", ls="", color=QWEN, label="Qwen3.5-4B"), Line2D([], [], marker="s", ls="", color=MISTRAL, label="Mistral-Small-3.2-24B")]
    fig.tight_layout(w_pad=9)
    fig.legend(handles=hs, loc="lower center", ncol=2, frameon=False, fontsize=7, bbox_to_anchor=(.5, -.12))
    save(fig, "fig_vlm")


if __name__ == "__main__":
    fig_q1()
    fig_validation()
    fig_vlm()
