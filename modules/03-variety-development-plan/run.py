"""Module 3 · The variety development plan.

Figures and worked examples for planning a breeding programme in Ethiopia:
  1. the pipeline funnel (how many lines, sites, reps and years at each stage)
  2. timelines for self-pollinated, cross-pollinated (hybrid), clonal and perennial crops
  3. disease screening: disease progress and AUDPC against checks
  4. a selection index that balances yield, disease and maturity (simulated PYT, 200 lines)
  5. genetic gain per year under four programme designs (breeder's equation)
  6. seed multiplication: from breeder seed to certified seed

Run:  python modules/03-variety-development-plan/run.py
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from b2b.plots import plt, _save, INK, MUTED, RULE, COPPER, TEAL, GOLD, BLUE, RED
from matplotlib.patches import FancyBboxPatch

out = lambda *p: os.path.join(HERE, *p)
SEED = 11
rng = np.random.default_rng(SEED)

# --------------------------------------------------------------------- 1. pipeline
PIPE = pd.DataFrame([
    # stage, year, entries, sites, reps, design, select on
    ("Parents and crossing block", "1", 40, 1, 1, "Unreplicated crossing block", "Parents that carry the product-profile traits"),
    ("F1 to F5 (single-seed descent or bulk)", "2-4", 6000, 1, 1, "Bulk plots; 2 generations a year with an irrigated off-season", "Heritable traits only: height, maturity, seed colour, disease on spreader rows"),
    ("Observation nursery (F6 lines)", "5", 600, 1, 1, "Augmented design: unreplicated lines + repeated checks", "Disease at a hot-spot site, lodging, maturity, seed type"),
    ("Preliminary yield trial (PYT)", "6", 120, 2, 2, "Alpha-lattice, 2 reps", "Selection index: yield + disease + maturity"),
    ("Advanced / regional trial (AYT)", "7", 60, 5, 3, "Alpha-lattice, 3 reps (Module 1)", "Yield, stability, G x E, quality"),
    ("National variety trial (NVT)", "8-9", 12, 6, 3, "RCBD, 3-4 reps, 2 years, standard + local checks", "Yield advantage over the best check at most sites"),
    ("Variety verification trial (VVT)", "10", 2, 8, 1, "Large plots on station and farms with standard and local checks", "National Variety Release Committee field visit"),
    ("Release and breeder seed", "10-11", 1, 1, 1, "Registration; breeder seed plots", "Variety description, maintenance by the breeder"),
], columns=["Stage", "Year", "Entries", "Sites", "Reps", "Design", "Select on"])
PIPE["Plots"] = PIPE.Entries * PIPE.Sites * PIPE.Reps
PIPE.to_csv(out("tables", "pipeline_self_pollinated.csv"), index=False)

fig, ax = plt.subplots(figsize=(11, 6.2))
n = len(PIPE)
mx = np.log10(PIPE.Entries.max())
for i, r in PIPE.iterrows():
    y = n - 1 - i
    w = 0.25 + 0.75 * np.log10(r.Entries) / mx
    col = [TEAL, TEAL, TEAL, BLUE, BLUE, COPPER, COPPER, GOLD][i]
    ax.add_patch(FancyBboxPatch((0.5 - w / 2, y + 0.12), w, 0.76, boxstyle="round,pad=0,rounding_size=0.08", fc=col, ec="none", alpha=0.9))
    ax.text(0.5, y + 0.5, f"{r.Entries:,}", ha="center", va="center", color="white", fontsize=12, fontweight="bold")
    ax.text(-0.02, y + 0.62, r.Stage, ha="right", va="center", fontsize=10.5, color=INK, fontweight="bold")
    ax.text(-0.02, y + 0.3, f"year {r.Year} · {r.Sites} site{'s' if r.Sites > 1 else ''} · {r.Reps} rep{'s' if r.Reps > 1 else ''}",
            ha="right", va="center", fontsize=9, color=MUTED)
    ax.text(1.02, y + 0.5, r["Select on"], ha="left", va="center", fontsize=9, color=INK, wrap=True)
ax.set_xlim(-1.05, 2.25); ax.set_ylim(-0.1, n + 0.1); ax.axis("off")
ax.set_title("From 40 parents to one variety: entries at each stage (self-pollinated crop, e.g. teff, wheat, barley)", loc="left")
_save(fig, out("figures", "01_pipeline_funnel.png"))

# --------------------------------------------------------------------- 2. timelines
PLANS = {
    "Self-pollinated\n(teff, wheat, barley, pulses, sesame)": [
        ("Crosses", 1, 1, TEAL), ("F1-F5, 2 gens/yr", 2, 4, TEAL), ("Observation", 5, 5, BLUE), ("PYT", 6, 6, BLUE),
        ("AYT", 7, 7, BLUE), ("NVT 2 yrs", 8, 9, COPPER), ("VVT", 10, 10, COPPER), ("Release", 11, 11, GOLD)],
    "Hybrid / cross-pollinated\n(maize, onion, sunflower)": [
        ("Source populations", 1, 1, TEAL), ("Inbreeding S1-S6", 2, 4, TEAL), ("Testcrosses", 5, 6, BLUE), ("Hybrid trials", 7, 8, BLUE),
        ("NVT 2 yrs", 9, 10, COPPER), ("VVT", 11, 11, COPPER), ("Release + parent seed", 12, 12, GOLD)],
    "Clonal\n(potato, sweet potato, enset, ginger)": [
        ("Crosses / true seed", 1, 1, TEAL), ("Seedling tubers", 2, 2, TEAL), ("Clonal gen 1-3", 3, 5, BLUE),
        ("Multi-site", 6, 7, BLUE), ("NVT 2 yrs", 8, 9, COPPER), ("VVT", 10, 10, COPPER), ("Release + clean seed", 11, 11, GOLD)],
    "Perennial tree crops\n(coffee, avocado, mango)": [
        ("Collect elite mother trees", 1, 2, TEAL), ("Nursery + plant", 3, 4, TEAL), ("Juvenile years", 5, 7, MUTED),
        ("Yield records, 4-6 harvests", 8, 12, BLUE), ("Multi-site + quality", 13, 16, COPPER), ("Release + mother blocks", 17, 18, GOLD)],
}
fig, ax = plt.subplots(figsize=(12, 6.2))
for k, (name, bars) in enumerate(PLANS.items()):
    y = len(PLANS) - 1 - k
    up = True
    for lab, a, b, col in bars:
        ax.barh(y, b - a + 1, left=a - 0.5, height=0.42, color=col, alpha=0.88, edgecolor="white")
        if len(lab) * 0.13 < (b - a + 1) - 0.15:
            ax.text((a + b) / 2, y, lab, ha="center", va="center", fontsize=7.6, color="white", fontweight="bold")
        else:   # short stage: label above or below the bar, alternating
            ax.text((a + b) / 2, y + (0.3 if up else -0.3), lab, ha="center", va="center", fontsize=7.4, color=col, fontweight="bold")
            up = not up
    ax.text(0.2, y, name, ha="right", va="center", fontsize=9.5, color=INK, fontweight="bold")
ax.set_xlim(-6.5, 19); ax.set_ylim(-0.6, len(PLANS) - 0.4); ax.set_yticks([])
ax.set_xticks(range(1, 19)); ax.set_xlabel("Year of the programme"); ax.spines["left"].set_visible(False)
ax.set_title("Typical time from first cross (or collection) to release, by how the crop reproduces", loc="left")
_save(fig, out("figures", "02_timelines.png"))

# --------------------------------------------------------------------- 3. AUDPC
days = np.array([0, 7, 14, 21, 28, 35])     # days after first symptoms on spreader rows
SEV = {  # % leaf area diseased (illustrative yellow-rust style scoring)
    "New line A (resistant)":         [0, 1, 2, 4, 5, 6],
    "New line B (slow rusting)":      [0, 2, 5, 10, 16, 22],
    "Standard check":                 [0, 5, 15, 30, 45, 60],
    "Susceptible spreader":           [1, 10, 30, 55, 75, 90],
}
def audpc(t, s):
    s = np.asarray(s, float); t = np.asarray(t, float)
    return float(np.sum((s[1:] + s[:-1]) / 2 * np.diff(t)))
au = pd.DataFrame({"Entry": list(SEV), "Final severity %": [v[-1] for v in SEV.values()],
                   "AUDPC (%-days)": [audpc(days, v) for v in SEV.values()]})
au["Relative AUDPC %"] = 100 * au["AUDPC (%-days)"] / au["AUDPC (%-days)"].iloc[-1]
au["Reaction"] = ["Resistant", "Moderately resistant (slow rusting)", "Susceptible", "Very susceptible"]
au.to_csv(out("tables", "audpc.csv"), index=False)
fig, ax = plt.subplots(figsize=(8.5, 4.6))
for (k, v), c in zip(SEV.items(), [TEAL, BLUE, GOLD, RED]):
    ax.plot(days, v, "-o", color=c, lw=2, ms=4, label=f"{k}: AUDPC {audpc(days, v):.0f}")
    ax.fill_between(days, v, color=c, alpha=0.08)
ax.set_xlabel("Days after first symptoms"); ax.set_ylabel("Leaf area diseased (%)")
ax.set_title("Disease progress at a hot-spot site: the area under the curve ranks resistance", loc="left")
ax.legend(frameon=False, fontsize=8.5, loc="upper left")
_save(fig, out("figures", "03_disease_progress_audpc.png"))

# --------------------------------------------------------------------- 4. selection index (simulated PYT)
N = 200
cov = np.array([[1, 0.35, 0.45], [0.35, 1, 0.1], [0.45, 0.1, 1]])  # yield, disease, days: tall/late lines yield more, catch more disease
z = rng.multivariate_normal(np.zeros(3), cov, N)
pyt = pd.DataFrame({"line": [f"PYT-{i + 1:03d}" for i in range(N)],
                    "yield_t_ha": np.round(2.3 + 0.32 * z[:, 0], 2),
                    "disease_1_9": np.clip(np.round(4.5 + 1.6 * z[:, 1]), 1, 9).astype(int),
                    "days_to_maturity": np.round(95 + 7 * z[:, 2]).astype(int)})
W = {"yield_t_ha": 1.0, "disease_1_9": -0.7, "days_to_maturity": -0.4}  # relative economic weights per SD
zs = (pyt[list(W)] - pyt[list(W)].mean()) / pyt[list(W)].std()
pyt["index"] = sum(w * zs[k] for k, w in W.items())
K = 20  # keep 10 %
sel_i = pyt.nlargest(K, "index"); sel_y = pyt.nlargest(K, "yield_t_ha")
pyt.to_csv(out("tables", "pyt_simulated.csv"), index=False)
comp = pd.DataFrame({"Group": ["All 200 lines", "Top 20 on yield only", "Top 20 on the index"],
                     "Yield t/ha": [pyt.yield_t_ha.mean(), sel_y.yield_t_ha.mean(), sel_i.yield_t_ha.mean()],
                     "Disease score 1-9": [pyt.disease_1_9.mean(), sel_y.disease_1_9.mean(), sel_i.disease_1_9.mean()],
                     "Days to maturity": [pyt.days_to_maturity.mean(), sel_y.days_to_maturity.mean(), sel_i.days_to_maturity.mean()],
                     "Lines scoring 6 or worse": [int((pyt.disease_1_9 >= 6).sum()), int((sel_y.disease_1_9 >= 6).sum()), int((sel_i.disease_1_9 >= 6).sum())]})
comp.to_csv(out("tables", "selection_comparison.csv"), index=False)
fig, ax = plt.subplots(figsize=(8.5, 5.2))
jit = rng.uniform(-0.18, 0.18, N)
ax.scatter(pyt.disease_1_9 + jit, pyt.yield_t_ha, s=16, color=RULE, edgecolor=MUTED, lw=0.3, label="All PYT lines")
ax.scatter(sel_y.disease_1_9 + jit[sel_y.index], sel_y.yield_t_ha, s=50, facecolor="none", edgecolor=RED, lw=1.3, label="Top 20 on yield only")
ax.scatter(sel_i.disease_1_9 + jit[sel_i.index], sel_i.yield_t_ha, s=26, color=TEAL, label="Top 20 on the index")
ax.axvspan(5.5, 9.5, color=RED, alpha=0.05); ax.text(9.4, pyt.yield_t_ha.min(), "susceptible (6-9)", ha="right", va="bottom", fontsize=8.5, color=RED)
ax.set_xlabel("Disease score (1 = clean, 9 = dead)"); ax.set_ylabel("Grain yield (t/ha)"); ax.set_xlim(0.5, 9.5)
ax.set_title("Selecting on yield alone keeps susceptible lines; the index keeps far fewer", loc="left")
ax.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3)
_save(fig, out("figures", "04_selection_index.png"))

# --------------------------------------------------------------------- 5. genetic gain per year
MEAN, SA = 2.0, 0.20   # t/ha; additive SD of yield among lines
SC = pd.DataFrame([
    ("A. Conventional: one generation a year, select at AYT", 1.40, 0.60, 10),
    ("B. Off-season nursery: 2 generations a year", 1.40, 0.60, 7),
    ("C. B + recycle best PYT lines as new parents", 1.75, 0.55, 5),
    ("D. C + genomic prediction on early lines", 1.75, 0.45, 3),
], columns=["Programme", "i", "r", "L_years"])
SC["Gain t/ha per year"] = SC.i * SC.r * SA / SC.L_years
SC["Gain % per year"] = 100 * SC["Gain t/ha per year"] / MEAN
SC["After 15 years t/ha"] = MEAN + 15 * SC["Gain t/ha per year"]
SC.to_csv(out("tables", "genetic_gain_scenarios.csv"), index=False)
fig, ax = plt.subplots(figsize=(9, 4.3))
cols = [MUTED, BLUE, TEAL, COPPER]
ax.barh(range(4)[::-1], SC["Gain % per year"], color=cols)
for k, r in SC.iterrows():
    ax.text(r["Gain % per year"] + 0.04, 3 - k, f"{r['Gain % per year']:.2f} % a year  (i {r.i}, r {r.r}, L {r.L_years} yr)", va="center", fontsize=9)
ax.set_yticks(range(4)[::-1]); ax.set_yticklabels(SC.Programme, fontsize=9)
ax.set_xlabel("Genetic gain in yield, % of the mean per year"); ax.set_xlim(0, SC["Gain % per year"].max() * 1.75)
ax.set_title("Shorter cycles pay more than bigger trials: gain = i · r · σA / L", loc="left")
_save(fig, out("figures", "05_genetic_gain.png"))

# --------------------------------------------------------------------- 6. seed multiplication
SEEDRATE, MULT = 30, 15  # teff-style seed rate kg/ha, and a cautious multiplication ratio (kg harvested per kg sown, after cleaning)
classes = ["Breeder", "Pre-basic", "Basic", "Certified 1", "Farmers' fields"]
kg = [20.0]
for _ in classes[1:]:
    kg.append(kg[-1] * MULT)
seed = pd.DataFrame({"Class": classes, "Seed sown kg": kg})
seed["Area ha"] = seed["Seed sown kg"] / SEEDRATE
seed["Harvest kg"] = seed["Seed sown kg"] * MULT
seed["Season"] = range(1, len(classes) + 1)
seed.to_csv(out("tables", "seed_multiplication.csv"), index=False)
fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(seed.Class, seed["Area ha"], color=[GOLD, COPPER, BLUE, TEAL, MUTED])
ax.set_yscale("log"); ax.set_ylabel("Area sown (ha, log scale)")
for k, r in seed.iterrows():
    ax.text(k, r["Area ha"] * 1.25, f"{r['Area ha']:,.1f} ha\n{r['Seed sown kg']:,.0f} kg", ha="center", fontsize=8.5)
ax.set_ylim(0.3, seed["Area ha"].max() * 6)
ax.set_title(f"From 20 kg of breeder seed to farmers in five seasons (seed rate {SEEDRATE} kg/ha, ×{MULT} per season)", loc="left")
_save(fig, out("figures", "06_seed_multiplication.png"))

# --------------------------------------------------------------------- guide
def md_table(df, fmt="{:.2f}"):
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)):
                cells.append(fmt.format(v))
            elif isinstance(v, (int, np.integer)):
                cells.append(f"{v:,}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)

crops = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(HERE)), "catalogue", "crops.csv"))
pp = crops[crops.crop.isin(["Teff", "Bread wheat", "Faba bean", "Maize", "Potato", "Hot and red pepper (berbere)", "Ginger", "Coffee (arabica)"])]
pp_md = pp[["crop", "agroecology", "diseases_pests", "breeding_priorities"]].rename(columns={
    "crop": "Crop", "agroecology": "Target environment", "diseases_pests": "Diseases and pests to beat", "breeding_priorities": "Product profile: desired traits"})
au_md = au.copy()
gain = SC[["Programme", "i", "r", "L_years", "Gain % per year", "After 15 years t/ha"]].rename(columns={"L_years": "L (years)"})
vals = dict(
    pipeline=md_table(PIPE[["Stage", "Year", "Entries", "Sites", "Reps", "Plots", "Design", "Select on"]]),
    product_profiles=md_table(pp_md),
    audpc=md_table(au_md, "{:.0f}"),
    sel=md_table(comp, "{:.2f}"),
    gain=md_table(gain, "{:.2f}"),
    seed=md_table(seed[["Season", "Class", "Seed sown kg", "Area ha", "Harvest kg"]], "{:,.1f}"),
    n_crops=len(crops),
    yield_only_bad=int((sel_y.disease_1_9 >= 6).sum()), index_bad=int((sel_i.disease_1_9 >= 6).sum()),
    yield_loss=f"{sel_y.yield_t_ha.mean() - sel_i.yield_t_ha.mean():.2f}",
    days_saved=f"{sel_y.days_to_maturity.mean() - sel_i.days_to_maturity.mean():.0f}",
    gain_a=f"{SC['Gain % per year'].iloc[0]:.2f}", gain_d=f"{SC['Gain % per year'].iloc[3]:.2f}",
    gain_ratio=f"{SC['Gain % per year'].iloc[3] / SC['Gain % per year'].iloc[0]:.1f}",
    cert_ha=f"{seed['Area ha'].iloc[-1]:,.0f}",
)
tpl = open(out("guide_template.md"), encoding="utf-8").read()
for k, v in vals.items():
    tpl = tpl.replace("{" + k + "}", str(v))
left = [l for l in tpl.splitlines() if "{" in l and "}" in l]
assert not left, left[:3]
open(out("README.md"), "w", encoding="utf-8").write(tpl)
json.dump({k: v for k, v in vals.items() if not isinstance(v, str) or "|" not in v}, open(out("tables", "key_results.json"), "w"), indent=1)
print(PIPE[["Stage", "Entries", "Plots"]]); print(au.round(0)); print(comp.round(2)); print(SC.round(3)); print(seed)
