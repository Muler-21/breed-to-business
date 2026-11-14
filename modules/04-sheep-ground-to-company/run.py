"""Module 4 · Sheep, from the ground to a company.

Builds the module guide from three kinds of input, each labelled in the output:
  * published  - numbers from cited Ethiopian studies (genetic parameters, trends, AI results, population)
  * real data  - the genomic analysis of public SNP genotypes (genomics/analyse.py, results/ folder)
  * assumption - planning values you must replace with your own (prices, phenotypic SD where not published)

Run:  python modules/04-sheep-ground-to-company/run.py
(run genomics/analyse.py first if genomics/results/ is empty)
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from b2b.plots import plt, _save, INK, MUTED, RULE, COPPER, TEAL, GOLD, BLUE, RED
from scipy.stats import norm

out = lambda *p: os.path.join(HERE, *p)
os.makedirs(out("figures"), exist_ok=True); os.makedirs(out("tables"), exist_ok=True)

# ------------------------------------------------------------ 1. published genetic parameters (6-month weight is the CBBP selection trait)
PAR = pd.DataFrame([
    # breed, trait, h2, source key, period / note
    ("Menz", "Birth weight", 0.29, "MENZ-GP", "CBBP 2009-2023"),
    ("Menz", "Weaning weight", 0.45, "MENZ-GP", "CBBP 2009-2023"),
    ("Menz", "6-month weight", 0.46, "MENZ-GP", "CBBP 2009-2023"),
    ("Menz", "Yearling weight", 0.42, "MENZ-GP", "CBBP 2009-2023"),
    ("Bonga", "Birth weight", 0.56, "BONGA-GP", "14 CBBPs 2012-2017"),
    ("Bonga", "Weaning weight", 0.36, "BONGA-GP", "14 CBBPs 2012-2017"),
    ("Bonga", "6-month weight", 0.22, "BONGA-GP", "14 CBBPs 2012-2017"),
    ("Bonga", "Yearling weight", 0.13, "BONGA-GP", "14 CBBPs 2012-2017"),
    ("Doyogena", "Birth weight", 0.33, "DOYO-GP", "CBBP 2013-2018"),
    ("Doyogena", "Weaning weight", 0.31, "DOYO-GP", "CBBP 2013-2018"),
    ("Doyogena", "6-month weight", 0.14, "DOYO-GP", "CBBP 2013-2018"),
    ("Doyogena", "Litter size", 0.28, "DOYO-GP", "CBBP 2013-2018"),
], columns=["Breed", "Trait", "h2", "Source", "Data"])
PAR.to_csv(out("tables", "published_heritabilities.csv"), index=False)
TREND = pd.DataFrame([("Bonga", 0.21, "CBBP-GAIN"), ("Horro", 0.18, "CBBP-GAIN"), ("Menz", 0.11, "CBBP-GAIN")],
                     columns=["Breed", "Genetic trend 6-month weight (kg/yr)", "Source"])
TREND.to_csv(out("tables", "published_genetic_trends.csv"), index=False)

# ------------------------------------------------------------ 2. predicted response for Bonga CBBP designs (breeder's equation, rams selected)
MEAN_6M = 24.7              # published: Bonga least-squares mean 6-month weight (BONGA-GP)
CV_P = 0.15                 # ASSUMPTION: phenotypic CV of 6-month weight in village flocks
H2 = 0.22                   # published (BONGA-GP)
sP = CV_P * MEAN_6M; sA = np.sqrt(H2) * sP
Lm, Lf = 2.0, 4.0           # ASSUMPTION: rams used ~1 year, born ~1.5-2 y before their lambs; ewes kept ~4 y
def i_of(prop): z = norm.ppf(1 - prop); return norm.pdf(z) / prop
SC = pd.DataFrame([
    ("A. Visual choice of rams (no records)", 0.30, 0.25, Lm),
    ("B. Top 10 % of rams on 6-month weight (one record)", 0.10, np.sqrt(H2), Lm),
    ("C. Top 10 % on BLUP EBV (pedigree + relatives)", 0.10, 0.65, Lm),
    ("D. C + AI with elite rams (top 3 %)", 0.03, 0.65, Lm),
    ("E. D + genomic EBV at weaning (rams used at 1 y)", 0.03, 0.60, 1.5),
], columns=["Design", "Proportion of rams kept", "Accuracy r", "Lm"])
SC["i"] = SC["Proportion of rams kept"].map(i_of)
SC["Gain kg/yr"] = SC.i * SC["Accuracy r"] * sA / (SC.Lm + Lf)
SC["Gain % of mean/yr"] = 100 * SC["Gain kg/yr"] / MEAN_6M
SC["6-month weight after 10 yr (kg)"] = MEAN_6M + 10 * SC["Gain kg/yr"]
SC.round(3).to_csv(out("tables", "bonga_design_scenarios.csv"), index=False)
fig, ax = plt.subplots(figsize=(10, 4.6))
cols = [MUTED, BLUE, TEAL, COPPER, GOLD]
ax.barh(range(len(SC))[::-1], SC["Gain kg/yr"], color=cols)
for k, r in SC.iterrows():
    ax.text(r["Gain kg/yr"] + 0.005, len(SC) - 1 - k, f"{r['Gain kg/yr']:.2f} kg/yr", va="center", fontsize=9)
ax.axvline(0.21, color=RED, ls="--", lw=1.2)
ax.text(0.212, len(SC) - 0.55, "observed Bonga CBBP trend\n0.21 kg/yr (Haile et al. 2020)", color=RED, fontsize=8.5, va="top")
ax.set_yticks(range(len(SC))[::-1]); ax.set_yticklabels(SC.Design, fontsize=9)
ax.set_xlabel("Predicted genetic gain in 6-month weight (kg per year)"); ax.set_xlim(0, SC["Gain kg/yr"].max() * 1.35)
ax.set_title("Bonga sheep: what each breeding design buys you (h² = 0.22, mean 24.7 kg)", loc="left")
_save(fig, out("figures", "01_design_scenarios.png"))

# ------------------------------------------------------------ 3. inbreeding control: rams per village
rams = np.arange(2, 31)
ewes = 300
dF = 100 * (1 / (8 * rams) + 1 / (8 * ewes))
INB = pd.DataFrame({"Breeding rams per generation": rams, "Ewes": ewes, "Inbreeding per generation %": dF.round(2),
                    "Effective size Ne": (4 * rams * ewes / (rams + ewes)).round(1)})
INB.to_csv(out("tables", "inbreeding_by_rams.csv"), index=False)
min_rams = int(rams[np.argmax(dF <= 1.0)])
fig, ax = plt.subplots(figsize=(8.5, 4.2))
ax.plot(rams, dF, "-o", color=TEAL, ms=4)
ax.axhline(1.0, color=RED, ls="--", lw=1); ax.text(30, 1.03, "1 % per generation: a common upper limit", ha="right", va="bottom", fontsize=8.5, color=RED)
ax.axvline(min_rams, color=MUTED, ls=":", lw=1); ax.text(min_rams + 0.3, dF.max() * 0.9, f"≥ {min_rams} rams", fontsize=9, color=INK)
ax.set_xlabel("Rams used per generation in the breeding group (300 ewes)"); ax.set_ylabel("Inbreeding added per generation (%)")
ax.set_title("Too few rams = fast inbreeding: ΔF = 1/(8·rams) + 1/(8·ewes)", loc="left")
_save(fig, out("figures", "02_inbreeding_rams.png"))

# ------------------------------------------------------------ 4. heritability and trends, published
fig, (a0, a1) = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw={"width_ratios": [2, 1]})
traits = ["Birth weight", "Weaning weight", "6-month weight", "Yearling weight", "Litter size"]
for k, (b, c) in enumerate(zip(["Menz", "Bonga", "Doyogena"], [BLUE, TEAL, GOLD])):
    d = PAR[PAR.Breed == b].set_index("Trait").reindex(traits)
    a0.scatter(np.arange(len(traits)) + (k - 1) * 0.18, d.h2, s=70, color=c, label=b, zorder=3)
a0.set_xticks(range(len(traits))); a0.set_xticklabels(traits, fontsize=9); a0.set_ylabel("Heritability (h²)")
a0.set_ylim(0, 0.65); a0.legend(frameon=False, fontsize=9); a0.set_title("Published heritabilities in Ethiopian CBBPs", loc="left")
a1.bar(TREND.Breed, TREND.iloc[:, 1], color=[TEAL, TEAL, BLUE])
for k, v in enumerate(TREND.iloc[:, 1]): a1.text(k, v + 0.005, f"{v:.2f}", ha="center", fontsize=9)
a1.set_ylabel("kg per year"); a1.set_title("Genetic trend, 6-month weight\n(2009-2018)", loc="left")
_save(fig, out("figures", "03_published_parameters.png"))

# ------------------------------------------------------------ 5. AI: pregnancies per 100 inseminated ewes (published) and rams' reach
AI = pd.DataFrame([("Two prostaglandin injections 11 days apart (PGF11)", 60.87), ("Single prostaglandin injection", 34.07)],
                  columns=["Synchronisation protocol (Menz ewes, fresh semen, fixed-time cervical AI)", "Conception rate %"])
AI.to_csv(out("tables", "ai_conception.csv"), index=False)

# ------------------------------------------------------------ 6. fattening enterprise (ASSUMPTION prices: replace with your market)
F = dict(rams=50, days=90, buy_kg=22.0, adg=0.10, buy_price_per_head=6000, sale_price_per_kg_lw=330,
         feed_kg_per_day=0.6, feed_price=25, hay_per_day=1.0, hay_price=6, vet_per_head=150, labour_per_cycle=9000, mortality=0.02)
def margin(adg, sale_price, f=F):
    n = f["rams"]; sold = n * (1 - f["mortality"])
    final = f["buy_kg"] + adg * f["days"]
    revenue = sold * final * sale_price
    cost = n * f["buy_price_per_head"] + n * f["days"] * (f["feed_kg_per_day"] * f["feed_price"] + f["hay_per_day"] * f["hay_price"]) \
        + n * f["vet_per_head"] + f["labour_per_cycle"]
    return revenue - cost, revenue, cost, final
base_m, base_r, base_c, base_final = margin(F["adg"], F["sale_price_per_kg_lw"])
adgs = np.array([0.05, 0.075, 0.10, 0.125, 0.15]); prices = np.array([280, 305, 330, 355, 380])
M = np.array([[margin(a, pr)[0] / 1000 for pr in prices] for a in adgs])
pd.DataFrame(M.round(1), index=[f"ADG {a:.3f} kg/d" for a in adgs], columns=[f"{p} birr/kg" for p in prices]).to_csv(out("tables", "fattening_margin_grid_thousand_birr.csv"))
fig, ax = plt.subplots(figsize=(8.5, 4.6))
im = ax.imshow(M, cmap="RdYlGn", aspect="auto", vmin=-abs(M).max(), vmax=abs(M).max())
for i in range(len(adgs)):
    for j in range(len(prices)):
        ax.text(j, i, f"{M[i, j]:,.0f}", ha="center", va="center", fontsize=9, color=INK)
ax.set_xticks(range(len(prices))); ax.set_xticklabels([f"{p}" for p in prices]); ax.set_xlabel("Sale price (birr per kg live weight) — assumption")
ax.set_yticks(range(len(adgs))); ax.set_yticklabels([f"{a:.3f}" for a in adgs]); ax.set_ylabel("Daily gain (kg/day)")
fig.colorbar(im, ax=ax, label="Margin per 90-day cycle, 50 rams (thousand birr)")
ax.set_title("Fattening 50 rams for 90 days: margin depends on gain and price", loc="left")
_save(fig, out("figures", "04_fattening_margin.png"))
FB = pd.DataFrame([
    ("Buy 50 young rams", F["rams"] * F["buy_price_per_head"]),
    ("Concentrate (0.6 kg/day)", F["rams"] * F["days"] * F["feed_kg_per_day"] * F["feed_price"]),
    ("Hay / crop residue (1 kg/day)", F["rams"] * F["days"] * F["hay_per_day"] * F["hay_price"]),
    ("Vaccination, deworming, vet", F["rams"] * F["vet_per_head"]),
    ("Labour", F["labour_per_cycle"]),
    ("Total cost", base_c), ("Revenue (49 rams sold)", base_r), ("Margin per cycle", base_m),
], columns=["Item", "Birr"])
FB.to_csv(out("tables", "fattening_budget_assumed.csv"), index=False)

# ------------------------------------------------------------ genomics results (real data)
GR = os.path.join(HERE, "genomics", "results")
S = json.load(open(os.path.join(GR, "summary.json")))
div = pd.read_csv(os.path.join(GR, "diversity_by_population.csv"))
roh = pd.read_csv(os.path.join(GR, "froh_ethiopian.csv"))
rel = pd.read_csv(os.path.join(GR, "genomic_relationships.csv"))
top = pd.read_csv(os.path.join(GR, "selection_scan_top_regions.csv"))
fst = pd.read_csv(os.path.join(GR, "fst_ethiopian_pairwise.csv"), index_col=0)


def md_table(df, fmt="{:.3f}"):
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)): cells.append(fmt.format(v))
            elif isinstance(v, (int, np.integer)): cells.append(f"{v:,}")
            else: cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


eth = div[div.Group != "Reference breed (outside Ethiopia)"]
topmd = top.copy()
topmd["Region (as in the source .bim)"] = topmd.apply(lambda r: f"chr{int(r.chr)}: {r.start_bp / 1e6:.0f}–{r.end_bp / 1e6:.0f} Mb", axis=1)
vals = dict(
    n_animals=S["animals_after_qc"], n_snps=f"{S['snps_after_qc']:,}", n_eth=S["ethiopian_animals"],
    div_table=md_table(eth[["Population", "Group", "n", "Ho", "He", "F (1-Ho/He)"]]),
    he_lo=f"{S['he_min'][0]} ({S['he_min'][1]:.3f})", he_hi=f"{S['he_max'][0]} ({S['he_max'][1]:.3f})",
    fst_mean=f"{S['fst_eth_mean']:.3f}", fst_max=f"{S['fst_eth_max']:.3f}", fst_pair=" and ".join(S["fst_max_pair"]),
    fst_menz=f"{fst.loc['Menz', 'Menz (600K set)']:.3f}", fst_sft_lft=f"{S['fst_sft_lft_genome']:.3f}",
    roh_table=md_table(roh[["Population", "Group", "n", "Mean F_ROH", "Max F_ROH"]]),
    roh_hi=f"{S['froh_highest'][0]} ({S['froh_highest'][1]:.3f})", roh_lo=f"{S['froh_lowest'][0]} ({S['froh_lowest'][1]:.3f})",
    top_table=md_table(topmd[["Region (as in the source .bim)", "max_window_fst"]].rename(columns={"max_window_fst": "Highest window FST"})),
    rel_table=md_table(rel),
    par_table=md_table(PAR.drop(columns=["Source"]), "{:.2f}"),
    sc_table=md_table(SC[["Design", "Proportion of rams kept", "i", "Accuracy r", "Lm", "Gain kg/yr", "6-month weight after 10 yr (kg)"]].rename(columns={"Lm": "Ram generation interval (yr)"}), "{:.2f}"),
    sP=f"{sP:.1f}", sA=f"{sA:.2f}", min_rams=min_rams,
    gain_b=f"{SC['Gain kg/yr'].iloc[1]:.2f}", gain_e=f"{SC['Gain kg/yr'].iloc[4]:.2f}",
    ai_table=md_table(AI, "{:.1f}"),
    fat_table=md_table(FB, "{:,.0f}"), fat_final=f"{base_final:.1f}", fat_margin=f"{base_m:,.0f}",
)
tpl = open(out("guide_template.md"), encoding="utf-8").read()
for k, v in vals.items():
    tpl = tpl.replace("{" + k + "}", str(v))
left = [l for l in tpl.splitlines() if "{" in l and "}" in l and not l.strip().startswith("I =")]
assert not left, left[:3]
open(out("README.md"), "w", encoding="utf-8").write(tpl)
json.dump({k: v for k, v in vals.items() if "|" not in str(v)}, open(out("tables", "key_results.json"), "w"), indent=1)
print(SC.round(3).to_string(index=False)); print("min rams", min_rams); print(FB.to_string(index=False)); print("final kg", base_final)
