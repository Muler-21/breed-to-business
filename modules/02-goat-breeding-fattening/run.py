"""Module 2 - Goats: community-based breeding and a fattening business trial.

Part A: on-farm records from a community-based breeding programme (CBBP):
        correct for non-genetic effects, estimate heritability, rank bucks by
        breeding value (BLUP), check buck x village (G x E), and project gain.
Part B: a 90-day fattening trial in randomised blocks by initial weight:
        ANOVA, ANCOVA, Tukey test, growth curves and partial budget.
Run:  python run.py
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from b2b import livestock as L, plots  # noqa: E402

# ---------------- settings you can change ----------------
SD_A, SD_P = 1.45, 2.74            # six-month weight: additive and phenotypic SD (kg), published CBBP values
BUCKS_KEPT_PROP = 0.25             # keep the best quarter of young bucks
KIDS_SOLD_PER_YEAR = 500           # a cooperative of about 60 households
PRICE_LIVE_BIRR_PER_KG = 330       # example price: replace with your market
RATIONS = ["T1: browsing only", "T2: + cowpea hay", "T3: + 75% conc. + 25% hay", "T4: + concentrate"]
ADG_TRUE = dict(zip(RATIONS, [32, 50, 66, 70]))     # g/day used to simulate the teaching data
FEED = {RATIONS[0]: {}, RATIONS[1]: {"hay": 0.40},
        RATIONS[2]: {"concentrate": 0.30, "hay": 0.10}, RATIONS[3]: {"concentrate": 0.40}}   # kg/goat/day
PRICES = dict(buy_birr_per_kg=330, sell_birr_per_kg=350, concentrate_birr_per_kg=45, hay_birr_per_kg=12)
DAYS = 90
# ---------------------------------------------------------

out = lambda *p: os.path.join(HERE, *p)
for d_ in ["data", "tables", "figures", "fieldbooks"]:
    os.makedirs(out(d_), exist_ok=True)

# ---------- A. community-based breeding ----------
d, true_ebv = L.simulate_cbbp(sd_a=SD_A, sd_p=SD_P)
d.to_csv(out("data", "cbbp_six_month_weights_simulated.csv"), index=False)
pd.DataFrame(columns=["kid_id", "dam_id", "sire", "village", "household", "birth_date", "sex", "birth_type",
                      "dam_parity", "weight_3m_kg", "date_3m", "weight_6m_kg", "date_6m", "notes"]
             ).to_csv(out("fieldbooks", "cbbp_recording_sheet.csv"), index=False)
tab, vc = L.sire_model(d)
tab.round(4).to_csv(out("tables", "anova_sire_model.csv"), index=False)
ebv = L.sire_blup(d, vc["var_sire"], vc["var_e"])
ebv.round(3).to_csv(out("tables", "buck_breeding_values.csv"))
sv = L.sire_by_village(d)
sv.round(4).to_csv(out("tables", "anova_buck_by_village.csv"), index=False)
gg = L.genetic_gain(SD_A, vc["h2"], BUCKS_KEPT_PROP)
n_keep = 6
plots.cbbp_factors(d, out("figures", "01_non_genetic_effects.png"))
plots.ebv_caterpillar(ebv, n_keep, out("figures", "02_buck_breeding_values.png"))
plots.reaction_norms(d, ebv, out("figures", "03_buck_by_village.png"))
plots.gain_projection(gg, KIDS_SOLD_PER_YEAR, PRICE_LIVE_BIRR_PER_KG, out("figures", "04_genetic_gain.png"))

# ---------- B. fattening trial ----------
rng = np.random.default_rng(21)
init = pd.Series(np.round(rng.normal(28.2, 3.0, 36), 1), index=[f"G{i:02d}" for i in range(1, 37)])
alloc = L.rcbd_by_weight(init, RATIONS)
alloc.to_csv(out("fieldbooks", "fattening_allocation.csv"), index=False)
w = L.simulate_fattening(alloc, ADG_TRUE, days=DAYS)
w.to_csv(out("data", "fattening_weights_simulated.csv"), index=False)
a, rcbd, ancova, summ, hsd = L.fattening_analysis(w, DAYS, RATIONS)
rcbd.round(4).to_csv(out("tables", "anova_fattening_rcbd.csv"), index=False)
ancova.round(4).to_csv(out("tables", "ancova_fattening.csv"), index=False)
summ.round(2).to_csv(out("tables", "fattening_means.csv"))
pb = L.partial_budget(summ, DAYS, FEED, PRICES, RATIONS)
pb.round(1).to_csv(out("tables", "partial_budget.csv"))
plots.growth_curves(w, RATIONS, out("figures", "05_growth_curves.png"))
plots.adg_bars(summ, hsd, out("figures", "06_daily_gain.png"))
plots.budget_bars(pb, out("figures", "07_partial_budget.png"))

facts = dict(n_kids=len(d), n_bucks=d.sire.nunique(), vc={k: float(v) for k, v in vc.items()},
             ebv_true_corr=float(np.corrcoef(ebv.EBV_kg, true_ebv.reindex(ebv.index))[0, 1]),
             top_bucks=ebv.head(n_keep).round(2).reset_index().to_dict("records"),
             sv_p=float(sv.loc[sv.Source == "Sire x village", "p"].iloc[0]), gain=gg["gain_per_year"], i_male=gg["i_male"])
json.dump(facts, open(out("tables", "key_results.json"), "w"), indent=1, default=float)
print(tab.round(3).to_string()); print(vc); print(ebv.head(8).round(2)); print(sv.round(3).tail(3))
print(rcbd.round(3)); print(ancova.round(3)); print(summ.round(2)); print(pb.round(1).to_string()); print(gg["gain_per_year"])

# ---------- guide ----------
def md_table(df, fmt="{:.2f}"):
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (bool, np.bool_)):
                cells.append("yes" if v else "no")
            elif isinstance(v, (float, np.floating)):
                cells.append("" if np.isnan(v) else ("<0.001" if c == "p" and v < 0.001 else fmt.format(v)))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)

t2 = pb.loc[RATIONS[1]]; t4 = pb.loc[RATIONS[3]]
be_conc = (t4.gross_margin - t2.net_return) / (FEED[RATIONS[3]]["concentrate"] * DAYS)
ebv_md = ebv.head(8).reset_index().rename(columns={"index": "Buck", "EBV_kg": "EBV (kg)", "accuracy": "Accuracy", "progeny": "Kids", "SE_EBV": "SE"})
fat_md = summ.reset_index().rename(columns={"treatment": "Ration", "initial_kg": "Start kg", "final_kg": "Final kg", "adg_g": "ADG g/day", "sd_adg": "SD", "tukey": "Tukey"})
pb_md = pb.reset_index()[["ration", "purchase", "sale", "feed_cost", "net_return", "dominated", "MRR_pct"]]
pb_md.columns = ["Ration", "Purchase", "Sale", "Supplement cost", "Net return", "Dominated", "MRR %"]
vals = dict(n_kids=len(d), sire_anova=md_table(tab, "{:.3f}"), var_s=f"{vc['var_sire']:.3f}", var_e=f"{vc['var_e']:.3f}",
            h2=f"{vc['h2']:.2f}", se_h2=f"{vc['se_h2']:.2f}", ebv_table=md_table(ebv_md, "{:.2f}"),
            acc=f"{ebv.accuracy.mean():.2f}", corr=f"{facts['ebv_true_corr']:.2f}", sv_anova=md_table(sv.tail(3), "{:.3f}"),
            sv_p=f"{facts['sv_p']:.2f}", kept=int(BUCKS_KEPT_PROP * 100), i_m=f"{gg['i_male']:.2f}", sqrt_h2=f"{np.sqrt(vc['h2']):.2f}",
            sd_a=SD_A, gain=f"{gg['gain_per_year']:.2f}", gain10=f"{gg['cumulative'][10]:.1f}", kids=KIDS_SOLD_PER_YEAR,
            price=PRICE_LIVE_BIRR_PER_KG, value10=f"{gg['cumulative'][10] * KIDS_SOLD_PER_YEAR * PRICE_LIVE_BIRR_PER_KG:,.0f}",
            rcbd=md_table(rcbd, "{:.2f}"), ancova=md_table(ancova, "{:.2f}"),
            cov_p=f"{ancova.loc[ancova.Source.str.startswith('Initial'), 'p'].iloc[0]:.2f}", fat_means=md_table(fat_md, "{:.1f}"),
            buy=PRICES["buy_birr_per_kg"], sell=PRICES["sell_birr_per_kg"], conc=PRICES["concentrate_birr_per_kg"], hay=PRICES["hay_birr_per_kg"],
            budget=md_table(pb_md, "{:,.0f}"), mrr=f"{t2.MRR_pct:.0f}", be_conc=f"{be_conc:.0f}",
            annual=f"{t2.net_return * 20 * 3:,.0f}")
tpl = open(out("guide_template.md"), encoding="utf-8").read()
for k, v in vals.items():
    tpl = tpl.replace("{" + k + "}", str(v))
left = [l for l in tpl.splitlines() if "{" in l and "}" in l]
assert not left, left[:3]
open(out("README.md"), "w", encoding="utf-8").write(tpl)
print("README written; break-even concentrate price", round(be_conc, 1))
