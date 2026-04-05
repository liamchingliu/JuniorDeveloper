# JuniorDeveloper
Research, data files and code for the paper "Generative AI and Early Evidence of Hollowing Out in the Entry-Level Technology Career Ladder" by Brandon Wu and Larry Liu

REPLICATION PACKAGE


Generative AI and early suggestive evidence of hollowing out
in the nonmanagerial technical layer

Overview
This package contains the data, code, and documentation needed to reproduce all tables and figures in the manuscript. The analysis uses U.S. Bureau of Labor Statistics Occupational Employment and Wage Statistics (OEWS) data from May 2015, 2016, 2017, 2018, 2021, 2022, 2023, and 2024. Years 2019 and 2020 are excluded because of the SOC reclassification transition and pandemic-period comparability break.
SOC code mapping
Occupation
2010 SOC
2018 SOC
Software Developers (nonmanagerial, primary)
15-1132 + 15-1133
15-1252
Computer Programmers (nonmanagerial, secondary)
15-1131
15-1251
CIS Managers (managerial, both specs)
11-3021
11-3021


Analysis-ready panel data
These are the primary inputs for replication. Each file contains one row per metropolitan area per one-year window, with all variables used in the regressions.
softwaredev_cismanager_panel.csv — Primary specification. Software developers vs. CIS managers. 1,625 observations across 6 windows.
programmer_cismanager_panel.csv — Secondary specification. Computer programmers vs. CIS managers. 1,325 observations across 6 windows.
Column definitions
Column
Description
window
Year pair (e.g. 2015-2016)
start_year / end_year
Base year (t) and end year (t+1)
role
Period label (Pre-gAI, Early gAI diffusion, Broader gAI diffusion)
area_code / area_name
OEWS metropolitan area FIPS-based code and name
nonmgr_occ_code
SOC code for the nonmanagerial occupation
mgr_occ_code
SOC code for the managerial occupation (always 11-3021)
nonmgr_emp_t / nonmgr_emp_t1
Nonmanagerial employment at time t and t+1
mgr_emp_t / mgr_emp_t1
Managerial employment at time t and t+1
dln_nonmgr_mgr_emp_ratio
Δ ln(Nonmgr Emp / Mgr Emp) = ln(nonmgr_t1/mgr_t1) − ln(nonmgr_t/mgr_t)
weight
Base-year total employment = nonmgr_emp_t + mgr_emp_t


The panel files also retain wage columns (nonmgr_wage_t, mgr_wage_t, and dln_nonmgr_mgr_wage_ratio) for completeness. No wage-based results are reported in the manuscript and those variables are not required to reproduce any table or figure.
Panel construction
Filter raw OEWS data to metropolitan statistical areas (AREA_TYPE = 4) for the relevant SOC codes.
For each one-year window, retain only MSAs present in both years for both the nonmanagerial and managerial occupation.
Drop MSAs where OEWS employment estimates are suppressed or flagged as unreliable.
The resulting set constitutes the window-specific balanced analytic sample.
Figure source data
File
Fig.
Description
figure1_softwaredev_annual_summary.csv
1
Regime-consistent total employment and nonmgr/mgr ratio for software developers and CIS managers
figure2_programmer_annual_summary.csv
2
Same for computer programmers
figure3_4_softwaredev_quadrant_shares.csv
3–4
Employment-weighted quadrant decomposition for software developers
figure5_6_programmer_quadrant_shares.csv
5–6
Same for computer programmers


Figs. 1–2 use regime-consistent MSA sets: for each SOC coding regime, only MSAs present in all windows within that regime are included, ensuring comparable employment totals across years. Employment values are sums across all common MSAs. The nonmanagerial-to-managerial ratio is computed from these totals.
Figs. 3–6 quadrant labels: Parallel Growth (both ↑), Ratio Compression (nonmgr ↓ mgr ↑), Ratio Expansion (nonmgr ↑ mgr ↓), Parallel Contraction (both ↓). Shares are employment-weighted.
Output tables
File
Table
Description
table1_softwaredev_emp_regression.csv
1
WLS intercept-only: Δln(nonmgr/mgr employment ratio), software developers
table2_programmer_emp_regression.csv
2
Same for computer programmers

Replication code
replicate.py
A single self-contained Python script that reproduces all tables and figures:
Loads the two panel CSVs.
Runs intercept-only WLS regressions of Δln(nonmgr/mgr employment ratio) on a constant, using base-year employment weights and HC1 robust standard errors.
Computes regime-consistent annual employment totals for Figs. 1–2.
Computes quadrant-decomposition shares for Figs. 3–6.
Generates Figs. 1–2 as PNG files.
Writes all output CSVs to ./output/ and prints verification checks against manuscript values.
Requirements
pip install pandas numpy statsmodels matplotlib
Usage
python replicate.py
All outputs are written to ./output/.
Raw data sources
All raw data come from the OEWS program, publicly available from the BLS at https://www.bls.gov/oes/tables.htm. For each release year (May 2015–2018, 2021–2024), the metropolitan-level file was downloaded and filtered to the relevant SOC codes.
File inventory
File
Purpose
README.docx
This file
replicate.py
Replication code
softwaredev_cismanager_panel.csv
Primary analysis panel
programmer_cismanager_panel.csv
Secondary analysis panel
figure1_softwaredev_annual_summary.csv
Fig. 1 source data
figure2_programmer_annual_summary.csv
Fig. 2 source data
figure3_4_softwaredev_quadrant_shares.csv
Figs. 3–4 source data
figure5_6_programmer_quadrant_shares.csv
Figs. 5–6 source data
table1_softwaredev_emp_regression.csv
Table 1 output
table2_programmer_emp_regression.csv
Table 2 output



