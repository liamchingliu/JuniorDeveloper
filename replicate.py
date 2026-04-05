#!/usr/bin/env python3
"""
replicate.py — Full replication script for:
"Generative AI and early suggestive evidence of hollowing out
 in the nonmanagerial technical layer"

This script:
  1. Loads the cleaned analysis-ready panels.
  2. Runs the intercept-only weighted regressions with HC1 robust SE.
  3. Computes regime-consistent annual totals for Figs. 1-2.
  4. Computes quadrant-decomposition shares for Figs. 3-6.
  5. Generates Figs. 1-2 (dual-axis employment and ratio charts).
  6. Writes all output CSVs and prints verification checks.

Requirements:
  pip install pandas numpy statsmodels matplotlib

Usage:
  python replicate.py
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

PRE_WINDOWS = ["2015-2016", "2016-2017", "2017-2018"]
POST_WINDOWS = ["2021-2022", "2022-2023", "2023-2024"]
ALL_WINDOWS = PRE_WINDOWS + POST_WINDOWS
ROLE_MAP = {
    "2015-2016": "Pre-gAI", "2016-2017": "Pre-gAI", "2017-2018": "Pre-gAI",
    "2021-2022": "Pre-gAI recovery period (Supplementary)",
    "2022-2023": "Early gAI diffusion", "2023-2024": "Broader gAI diffusion",
}

# ── STEP 1: Load panels ──
print("=" * 60)
print("STEP 1: Loading analysis-ready panels")
print("=" * 60)
sd = pd.read_csv("softwaredev_cismanager_panel.csv")
pr = pd.read_csv("programmer_cismanager_panel.csv")
print(f"  Software-developer panel: {len(sd):,} metro-window obs")
print(f"  Programmer panel:         {len(pr):,} metro-window obs")

# ── STEP 2: WLS regressions ──
def run_intercept_wls(df, depvar="dln_nonmgr_mgr_emp_ratio"):
    y = df[depvar].astype(float)
    w = df["weight"].astype(float)
    valid = y.notna() & w.notna() & (w > 0)
    y, w = y[valid], w[valid]
    X = sm.add_constant(pd.Series(np.ones(len(y)), index=y.index, name="const"))
    model = sm.WLS(y, X, weights=w).fit(cov_type="HC1")
    coef, se = model.params["const"], model.bse["const"]
    t, p = model.tvalues["const"], model.pvalues["const"]
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
    return {"n_msas": int(valid.sum()), "alpha_coef": coef, "se_hc1": se,
            "t_stat": t, "p_value": p, "sig": sig,
            "pct_change_approx": (np.exp(coef) - 1) * 100}

print("\n" + "=" * 60)
print("STEP 2: Running intercept-only WLS regressions")
print("=" * 60)

cols_out = ["window", "role", "n_msas", "alpha_coef", "se_hc1",
            "t_stat", "p_value", "sig", "pct_change_approx"]

print("\nTable 1 - Software Developer-to-Manager Employment Ratio:")
t1_rows = []
for w in ALL_WINDOWS:
    res = run_intercept_wls(sd[sd["window"] == w])
    res["window"], res["role"] = w, ROLE_MAP[w]
    t1_rows.append(res)
    print(f"  {w}: a={res['alpha_coef']:+.4f}, SE={res['se_hc1']:.4f}, "
          f"t={res['t_stat']:+.2f}, p={res['p_value']:.4f} {res['sig']}")
t1 = pd.DataFrame(t1_rows)[cols_out]
t1.to_csv(OUTPUT / "table1_softwaredev_emp_regression.csv", index=False)

print("\nTable 2 - Computer Programmer-to-Manager Employment Ratio:")
t2_rows = []
for w in ALL_WINDOWS:
    res = run_intercept_wls(pr[pr["window"] == w])
    res["window"], res["role"] = w, ROLE_MAP[w]
    t2_rows.append(res)
    print(f"  {w}: a={res['alpha_coef']:+.4f}, SE={res['se_hc1']:.4f}, "
          f"t={res['t_stat']:+.2f}, p={res['p_value']:.4f} {res['sig']}")
t2 = pd.DataFrame(t2_rows)[cols_out]
t2.to_csv(OUTPUT / "table2_programmer_emp_regression.csv", index=False)

# ── STEP 3: Figure 1-2 source data ──
print("\n" + "=" * 60)
print("STEP 3: Computing figure source data")
print("=" * 60)

def get_regime_totals(panel, windows):
    msa_sets = [set(panel[panel["window"] == w]["area_code"].astype(str)) for w in windows]
    common = msa_sets[0]
    for s in msa_sets[1:]:
        common = common & s
    rows = []
    for w in windows:
        sub = panel[(panel["window"] == w) & (panel["area_code"].astype(str).isin(common))]
        yr_a, yr_b = int(sub["start_year"].iloc[0]), int(sub["end_year"].iloc[0])
        rows.append({"year": yr_a, "total_nonmgr": int(sub["nonmgr_emp_t"].sum()),
                     "total_mgr": int(sub["mgr_emp_t"].sum()), "n_msas": len(common)})
        if w == windows[-1]:
            rows.append({"year": yr_b, "total_nonmgr": int(sub["nonmgr_emp_t1"].sum()),
                         "total_mgr": int(sub["mgr_emp_t1"].sum()), "n_msas": len(common)})
    df = pd.DataFrame(rows)
    df["nonmgr_mgr_ratio"] = df["total_nonmgr"] / df["total_mgr"]
    return df

sd_pre, sd_post = get_regime_totals(sd, PRE_WINDOWS), get_regime_totals(sd, POST_WINDOWS)
pd.concat([sd_pre, sd_post]).to_csv(OUTPUT / "figure1_softwaredev_annual_summary.csv", index=False)
pr_pre, pr_post = get_regime_totals(pr, PRE_WINDOWS), get_regime_totals(pr, POST_WINDOWS)
pd.concat([pr_pre, pr_post]).to_csv(OUTPUT / "figure2_programmer_annual_summary.csv", index=False)
print("  Figs. 1-2 source data written")

# ── STEP 4: Quadrant decomposition ──
def quadrant_shares(panel):
    rows = []
    for w in panel["window"].unique():
        sub = panel[panel["window"] == w].copy()
        sub["nm_up"] = sub["nonmgr_emp_t1"].astype(float) > sub["nonmgr_emp_t"].astype(float)
        sub["mg_up"] = sub["mgr_emp_t1"].astype(float) > sub["mgr_emp_t"].astype(float)
        total = sub["weight"].sum()
        pg = sub[(sub["nm_up"]) & (sub["mg_up"])]
        rc = sub[(~sub["nm_up"]) & (sub["mg_up"])]
        re = sub[(sub["nm_up"]) & (~sub["mg_up"])]
        pc = sub[(~sub["nm_up"]) & (~sub["mg_up"])]
        rows.append({"window": w, "role": sub["role"].iloc[0], "n": len(sub),
                     "parallel_growth_share": pg["weight"].sum() / total,
                     "ratio_compression_share": rc["weight"].sum() / total,
                     "ratio_expansion_share": re["weight"].sum() / total,
                     "parallel_contraction_share": pc["weight"].sum() / total,
                     "n_parallel_growth": len(pg), "n_ratio_compression": len(rc),
                     "n_ratio_expansion": len(re), "n_parallel_contraction": len(pc)})
    return pd.DataFrame(rows)

quadrant_shares(sd).to_csv(OUTPUT / "figure3_4_softwaredev_quadrant_shares.csv", index=False)
quadrant_shares(pr).to_csv(OUTPUT / "figure5_6_programmer_quadrant_shares.csv", index=False)
print("  Figs. 3-6 quadrant source data written")

# ── STEP 5: Generate Figs. 1-2 ──
print("\n" + "=" * 60)
print("STEP 5: Generating Figs. 1-2")
print("=" * 60)
try:
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    def make_fig(d_pre, d_post, title, nm_lab, mg_lab, fname, ymax, rr):
        fig, ax1 = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor("white")
        ax1.set_xlim(2014.5, 2024.5)
        ax1.set_xticks(range(2015, 2025))
        ax1.tick_params(labelsize=13)
        c1, c2, c3 = "#C0392B", "#7D8C2E", "#6A0DAD"
        for d in [d_pre, d_post]:
            ax1.plot(d["year"], d["total_nonmgr"], "-o", color=c1, lw=2, ms=5, zorder=5)
            ax1.plot(d["year"], d["total_mgr"], "-o", color=c2, lw=2, ms=5, zorder=5)
        ax1.set_ylim(0, ymax)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{int(x):,}"))
        ax1.tick_params(axis="y", labelsize=12); ax1.grid(axis="y", alpha=0.3)
        ax2 = ax1.twinx()
        for d in [d_pre, d_post]:
            ax2.plot(d["year"], d["nonmgr_mgr_ratio"], "--o", color=c3, lw=2, ms=5, zorder=4)
        ax2.set_ylim(rr); ax2.tick_params(axis="y", labelsize=12)
        ax1.set_title(title, fontsize=15, fontweight="bold", pad=15)
        legend = [
            Line2D([0],[0], color=c1, marker="o", lw=2, ms=5,
                   label=f"{nm_lab} (Left Axis)\n(Nonmanagerial)"),
            Line2D([0],[0], color=c2, marker="o", lw=2, ms=5,
                   label=f"{mg_lab} (Left Axis)\n(Managerial)"),
            Line2D([0],[0], color=c3, marker="o", lw=2, ms=5, ls="--",
                   label="Nonmgr/Mgr Ratio (Right Axis)")]
        ax1.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.5,-0.18),
                   ncol=3, fontsize=11, frameon=True, edgecolor="#CCC")
        plt.tight_layout(); plt.subplots_adjust(bottom=0.18)
        plt.savefig(fname, dpi=300, facecolor="white", bbox_inches="tight", pad_inches=0.2)
        plt.close(); print(f"  Saved {fname}")

    make_fig(sd_pre, sd_post,
             "Software Developer and CIS Manager Employment with\n"
             "Nonmanagerial-to-Managerial Ratio, 2015\u20132018 & 2021\u20132024",
             "Software Developers", "CIS Managers",
             OUTPUT / "Figure_1.png", 1_500_000, (0.0, 4.0))
    make_fig(pr_pre, pr_post,
             "Computer Programmer and CIS Manager Employment with\n"
             "Nonmanagerial-to-Managerial Ratio, 2015\u20132018 & 2021\u20132024",
             "Computer Programmer", "CIS Managers",
             OUTPUT / "Figure_2.png", 450_000, (0.0, 0.9))
except ImportError:
    print("  matplotlib not installed - skipping figure generation")

# ── STEP 6: Verification ──
print("\n" + "=" * 60)
print("STEP 6: Verification summary")
print("=" * 60)
t1c = t1[t1["window"] == "2023-2024"].iloc[0]
print(f"\n  Table 1, 2023-2024: a={t1c['alpha_coef']:.4f} (ms: -0.0878), "
      f"p={t1c['p_value']:.6f}, N={t1c['n_msas']} (ms: 332)")
t2c = t2[t2["window"] == "2015-2016"].iloc[0]
print(f"  Table 2, 2015-2016: a={t2c['alpha_coef']:.4f} (ms: -0.1061), "
      f"p={t2c['p_value']:.6f}, N={t2c['n_msas']} (ms: 272)")
print("\n" + "=" * 60)
print("DONE - All outputs written to ./output/")
print("=" * 60)
