"""Module 1 - Teff variety trial: 60 varieties x 5 locations x 3 years.

Run:  python run.py
It (1) designs and randomises the field for every location and year,
(2) writes printable field books, (3) creates a teaching dataset (simulated,
realistic), (4) analyses it site by site and combined, (5) runs AMMI, GGE
and stability, and (6) builds the decision table and all figures.

To use YOUR data: fill the yield column of the field books, save them as one
CSV with the same columns as data/teff_met_simulated.csv, and set DATA_FILE.
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from b2b import met, plots  # noqa: E402

# ---------------- settings you can change ----------------
N_TEST = 58                                    # candidate lines
CHECKS = ["Check-Quncho", "Check-Tsedey"]      # standard checks (high-potential and low-moisture)
BLOCK_SIZE, REPS = 6, 3                        # alpha-lattice: 10 blocks of 6 plots per replicate
LOCATIONS = {  # code: (name, location effect t/ha, moisture stress 0-1) -- teaching values
    "DZ": ("Debre Zeit", 0.30, 0.35), "HO": ("Holetta", 0.10, 0.15), "AD": ("Adet", 0.05, 0.45),
    "AT": ("Alem Tena", -0.65, 0.95), "DM": ("Debre Markos", 0.20, 0.10)}
YEARS = {2024: (0.00, 0.00), 2025: (-0.25, 0.25), 2026: (0.15, -0.10)}  # year effect, extra stress
PLOT_M2 = 4.0                                  # 2 m x 2 m plots
SEED_G_PER_PLOT = 12                           # 30 kg/ha broadcast
PRICE_BIRR_PER_KG = 120                        # example teff grain price: replace with your market price
DATA_FILE = None                               # e.g. "data/my_trial.csv" to analyse your own data
# ---------------------------------------------------------

out = lambda *p: os.path.join(HERE, *p)
for d in ["fieldbooks", "data", "tables", "figures"]:
    os.makedirs(out(d), exist_ok=True)

genos = [f"TF{i:02d}" for i in range(1, N_TEST + 1)] + CHECKS
env = pd.DataFrame([dict(location=n, loc_code=c, year=y, env=f"{c}{str(y)[2:]}", loc_effect=le,
                         year_effect=ye, stress=float(np.clip(st + ys, 0, 1)))
                    for y, (ye, ys) in YEARS.items() for c, (n, le, st) in LOCATIONS.items()])

# 1-2. design and field books (new randomisation for every location and year)
fbs = {}
for i, e in env.iterrows():
    fb = met.alpha_design(genos, BLOCK_SIZE, REPS, seed=1000 + i)
    assert met.concurrence_check(fb) == 1
    fbs[e.env] = fb
    sheet = fb.assign(location=e.location, year=e.year, env=e.env, yield_t_ha="", days_to_maturity="",
                      plant_height_cm="", lodging_pct="", notes="")
    sheet.to_csv(out("fieldbooks", f"fieldbook_{e.env}.csv"), index=False)
fb0 = fbs[env.env[0]]
field = dict(width_m=float(fb0.x_m.max() + 2), length_m=float(fb0.y_m.max() + 2))
field["area_ha"] = field["width_m"] * field["length_m"] / 10000
field["plots_per_site"] = len(fb0)
field["seed_g_per_variety_per_site"] = SEED_G_PER_PLOT * REPS
field["seed_kg_per_site"] = SEED_G_PER_PLOT * len(fb0) / 1000

# 3. data
if DATA_FILE:
    d = pd.read_csv(out(DATA_FILE))
else:
    d = met.simulate_met(fbs, genos, env)
    d.to_csv(out("data", "teff_met_simulated.csv"), index=False)

# 4. single-site analyses
S, M, site_tabs = [], [], {}
for e, g in d.groupby("env", sort=False):
    tab, adj, s = met.site_analysis(g)
    s.update(location=g.location.iloc[0], year=int(g.year.iloc[0]))
    S.append(s); site_tabs[e] = tab
    M.append(pd.DataFrame({"entry": adj.index, "mean": adj.values, "env": e,
                           "location": g.location.iloc[0], "year": g.year.iloc[0]}))
S = pd.DataFrame(S); M = pd.concat(M, ignore_index=True)
S.round(4).to_csv(out("tables", "site_summary.csv"), index=False)
first = env.env[0]
site_tabs[first].round(4).to_csv(out("tables", f"anova_site_{first}.csv"), index=False)
M.round(4).to_csv(out("tables", "adjusted_means_long.csv"), index=False)

# 5. combined analysis
comb, vc, dims = met.combined_anova(M, S, REPS)
comb.round(4).to_csv(out("tables", "anova_combined.csv"), index=False)
plan = pd.DataFrame([dict(locations=L, years=Y, H2=met.heritability(vc, L, Y, REPS))
                     for Y in range(1, 6) for L in range(1, 11)])
plan.round(4).to_csv(out("tables", "heritability_planning.csv"), index=False)

GE = met.ge_table(M)
GE = GE[env.env.tolist()]
GE.round(3).to_csv(out("tables", "genotype_by_environment_means.csv"))
amm_t, amm_g, amm_e, _ = met.ammi(GE, REPS, float(S.mse.mean()), int(S.df_e.sum()))
amm_t.round(4).to_csv(out("tables", "ammi_ipca.csv"), index=False)
gge_g, gge_e, gge_expl, winners = met.gge(GE)
stab = met.stability(GE)
maturity = d.groupby("entry").days_to_maturity.mean()
dec, best_check = met.decision_table(GE, CHECKS, amm_g, stab, maturity, PRICE_BIRR_PER_KG)
dec.round(3).to_csv(out("tables", "decision_table.csv"))

# mega-environments from GGE winners, and best entry per location over years
by_loc = M.groupby(["location", "entry"])["mean"].mean().unstack()
loc_best = by_loc.idxmax(1)

# 6. figures
plots.field_map(fb0, CHECKS, out("figures", "01_field_layout.png"), f"Field layout, {env.location[0]} {env.year[0]}")
plots.env_box(d, env, out("figures", "02_environment_means.png"))
plots.ss_share(comb, out("figures", "03_variance_sources.png"))
plots.h2_plan(plan, out("figures", "04_heritability_planning.png"))
plots.ammi1(GE, amm_g, amm_e, CHECKS, dec.drop(CHECKS).index[:5], out("figures", "05_ammi1_biplot.png"))
plots.gge_www(gge_g, gge_e, gge_expl, CHECKS, out("figures", "06_gge_which_won_where.png"))
plots.fw_lines(GE, stab, list(dec.drop(CHECKS).index[:4]) + CHECKS, out("figures", "07_finlay_wilkinson.png"))
plots.decision(dec, CHECKS, out("figures", "08_decision_map.png"))
plots.rank_heat(GE, dec.index[:15], out("figures", "09_rank_heatmap.png"))

# key numbers for the guide page
top = dec.drop(CHECKS, errors="ignore").head(3)
facts = dict(field=field, n_env=len(env), n_plots=len(d), best_check=best_check,
             site=S[["env", "mean", "cv_pct", "h2", "efficiency_vs_rcbd_pct"]].round(3).to_dict("records"),
             combined=comb.round(4).to_dict("records"), vc={k: round(v, 5) for k, v in vc.items()},
             h2_5x1=round(met.heritability(vc, 5, 1, REPS), 3), h2_5x3=round(met.heritability(vc, 5, 3, REPS), 3),
             h2_3x2=round(met.heritability(vc, 3, 2, REPS), 3), ammi=amm_t.round(4).to_dict("records"),
             gge_expl=[round(float(x), 1) for x in gge_expl], winners=winners.to_dict(), loc_best=loc_best.to_dict(),
             top=top.round(3).reset_index().to_dict("records"))
json.dump(facts, open(out("tables", "key_results.json"), "w"), indent=1, default=float)
print(json.dumps({k: facts[k] for k in ["field", "best_check", "h2_5x1", "h2_5x3", "gge_expl", "winners", "loc_best"]}, indent=1, default=float))
print(comb.round(3).to_string())
print(top.round(2).to_string())


# 7. write the guide (README.md) from the template with this run's numbers
def md_table(df, fmt="{:.3f}"):
    df = df.copy()
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)):
                cells.append("" if np.isnan(v) else ("<0.001" if c == "p" and v < 0.001 else fmt.format(v)))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)

at_envs = [e for e in GE.columns if e.startswith("AT")]
hp_envs = [e for e in GE.columns if not e.startswith("AT")]
names = dict(zip(env.env, env.location + " " + env.year.astype(str)))
tf48_envs = [names[e] for e, w in winners.items() if w == "TF48"]
site_cols = S[["env", "mean", "cv_pct", "lsd5", "h2", "efficiency_vs_rcbd_pct"]].rename(columns={
    "env": "Env", "mean": "Mean t/ha", "cv_pct": "CV %", "lsd5": "LSD 5%", "h2": "H²", "efficiency_vs_rcbd_pct": "Efficiency vs RCBD %"})
site_cols = site_cols.assign(**{c: site_cols[c].round(2) for c in site_cols.columns[1:]})
comb_md = comb.copy(); comb_md["% of SS"] = comb_md["% of SS"].round(1)
dec_md = dec.head(8)[["mean_t_ha", "vs_best_check_pct", "wins_vs_check_pct", "worst_env_t_ha", "b_FW", "ASV", "maturity_days", "rank_sum"]].reset_index()
dec_md.columns = ["Entry", "Mean t/ha", "% vs best check", "% envs beating check", "Worst env t/ha", "b (FW)", "ASV", "Maturity days", "Yield-stability index"]
pct = dict(zip(comb.Source, comb["% of SS"]))
vals = dict(width=f"{field['width_m']:.1f}", length=f"{field['length_m']:.1f}", area=f"{field['area_ha']:.2f}",
            plots=field["plots_per_site"], seed_var=field["seed_g_per_variety_per_site"], seed_site=f"{field['seed_kg_per_site']:.2f}",
            n_env=len(env), site_anova=md_table(site_tabs[first]), site_summary=md_table(site_cols, "{:.2f}"),
            combined_anova=md_table(comb_md, "{:.3f}"), gl_pct=f"{pct['G x L']:.1f}", gy_pct=f"{pct['G x Y']:.1f}",
            vc_g=f"{vc['g']:.4f}", vc_gl=f"{vc['gl']:.4f}", vc_gy=f"{vc['gy']:.4f}", vc_gly=f"{vc['gly']:.4f}", vc_e=f"{vc['error']:.4f}",
            h2_5x1=facts["h2_5x1"], h2_5x3=facts["h2_5x3"], ammi_table=md_table(amm_t, "{:.3f}"),
            pc1=facts["gge_expl"][0], pc2=facts["gge_expl"][1], tf48_envs=", ".join(tf48_envs),
            tf48_at=f"{GE.loc['TF48', at_envs].mean():.2f}", tsedey_at=f"{GE.loc['Check-Tsedey', at_envs].mean():.2f}",
            quncho_at=f"{GE.loc['Check-Quncho', at_envs].mean():.2f}", tf47_hp=f"{GE.loc['TF47', hp_envs].mean():.2f}",
            quncho_hp=f"{GE.loc['Check-Quncho', hp_envs].mean():.2f}",
            tf47_earlier=f"{maturity['Check-Quncho'] - maturity['TF47']:.0f}", tsedey_b=f"{stab.loc['Check-Tsedey', 'b_FW']:.2f}",
            decision_table=md_table(dec_md, "{:.2f}"), tf47_wins=f"{dec.loc['TF47', 'wins_vs_check_pct']:.0f}",
            price=PRICE_BIRR_PER_KG, per_01=f"{0.1 * 1000 * PRICE_BIRR_PER_KG:,.0f}",
            tf48_gain_t=f"{GE.loc['TF48', at_envs].mean() - GE.loc['Check-Quncho', at_envs].mean():.2f}",
            tf48_gain_birr=f"{(GE.loc['TF48', at_envs].mean() - GE.loc['Check-Quncho', at_envs].mean()) * 1000 * PRICE_BIRR_PER_KG:,.0f}")
tpl = open(out("guide_template.md"), encoding="utf-8").read()
for k, v in vals.items():
    tpl = tpl.replace("{" + k + "}", str(v))
assert "{" not in tpl.replace("{:", ""), [l for l in tpl.splitlines() if "{" in l][:3]
open(out("README.md"), "w", encoding="utf-8").write(tpl)
print("README.md written")
