"""Hidden opposite shifts counted on validated aspects only (derivation of the 38-of-60 figure in the manuscript).

Reads results/q2/hidden_opposite.csv (written by q2_q3.py) and keeps a configuration-pair x aspect comparison only if the
aspect is validated for both configurations (annotation rounds 1-2, results/annotation_study and results/annotation_round2):
sat, medium and shot hold on all 12 configurations; tone and bg only on the round-1 configurations. Of the 8 Q2
configurations, the round-1 set contains G01, G02, G06 and G08.
Writes results/q2/hidden_opposite_validated.csv (the kept rows) and prints the counts. No resampling: it only filters the
pre-registered output.
Usage: python q2_validated_counts.py
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "..", "..", "results", "q2")
ALL_SETS = {"sat", "medium", "shot"}
ROUND1 = {"G01_sd15", "G02_sdxl", "G06_klein_base4b_cfg4", "G08_klein4b"}

h = pd.read_csv(f"{RES}/hidden_opposite.csv")
keep = h.aspect.isin(ALL_SETS) | (h.A.isin(ROUND1) & h.B.isin(ROUND1))
v = h[keep].copy()
v["pooled_within_margin"] = v.pooled_delta.abs() < 0.5
v.to_csv(f"{RES}/hidden_opposite_validated.csv", index=False)
n_all, n_in, n_hide = len(v), int(v.pooled_within_margin.sum()), int(v.hides_opposite_shifts.sum())
print(f"validated comparisons: {n_all} of {len(h)}; pooled within the margin: {n_in}; hiding opposite shifts: {n_hide}")
print(v.groupby("aspect").agg(comparisons=("aspect", "size"), within=("pooled_within_margin", "sum"),
                              hide=("hides_opposite_shifts", "sum")).to_string())
