"""Module 5 · Five agri-businesses to start around Debre Markos (East Gojjam, Amhara).

Everything a reader should change sits in the dictionaries at the top: prices, volumes,
investment, salaries, loan terms. Run the script again and every table, chart and the
guide update.

Labels used in the guide:
  sourced     a price or fact from a cited 2025-2026 report (national or Addis Ababa)
  assumption  a planning value for Debre Markos, to be replaced with quotes you collect

All money in Ethiopian birr at 2026 prices (constant prices, so the discount rate is a
real rate). Exchange rate for imported equipment: 160 birr per US dollar (NBE auction,
Nov 2026, sourced).

Run:  python modules/05-five-businesses-debre-markos/run.py
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from b2b.plots import plt, _save, INK, MUTED, RULE, COPPER, TEAL, GOLD, BLUE, RED

out = lambda *p: os.path.join(HERE, *p)
os.makedirs(out("figures"), exist_ok=True); os.makedirs(out("tables"), exist_ok=True)

YEARS = 5
USD = 160                      # sourced: NBE auction rate ~159-160 birr/USD, Nov 2026
FIN = dict(equity_share=0.30,  # assumption: DBE asks 20-30 % equity; MFIs similar
           loan_rate=0.18,     # assumption: policy rate 16 % (Nov 2026) + margin
           loan_years=5,
           grace_years=1,      # assumption: one year interest-only, common for DBE and bank project loans
           tax_rate=0.30,      # assumption: business income tax for a PLC
           discount=0.12,      # assumption: real hurdle rate (constant prices)
           )

# ===================================================================== 1. choose: score 11 candidates
CRIT = {"Local resource fit": 0.20, "Proven demand and price": 0.20, "Low capital need": 0.15,
        "Fast first cash": 0.10, "Keeps running if roads close": 0.15, "Jobs and farmers reached": 0.10,
        "Uses this curriculum": 0.10}
CAND = {  # scores 1-5 (assumption: the author's judgement, open to change)
    "Teff flour and injera bakery":              [5, 5, 4, 5, 4, 4, 3],
    "Sheep fattening and breeding rams":         [4, 5, 4, 4, 4, 3, 5],
    "Teff and wheat quality seed":               [5, 4, 3, 2, 3, 5, 5],
    "Honey: apiary, collection and packing":     [5, 4, 4, 3, 4, 5, 3],
    "Forage seed, hay and feed blocks":          [4, 4, 4, 3, 4, 4, 3],
    "Milk collection and dairy processing":      [4, 5, 2, 4, 3, 5, 3],
    "Improved chicken brooding (45-day chicks)": [3, 4, 4, 4, 3, 4, 2],
    "Vermicompost and bio-fertiliser":           [4, 3, 5, 4, 4, 3, 2],
    "Seed potato and vegetables":                [4, 3, 3, 3, 3, 4, 3],
    "Layer farm (eggs)":                         [3, 3, 3, 3, 3, 3, 2],
    "Farm data, trials and breeding services":   [3, 2, 5, 3, 2, 2, 5],
}
S = pd.DataFrame(CAND, index=list(CRIT)).T
S["Weighted score"] = (S[list(CRIT)] * pd.Series(CRIT)).sum(axis=1)
S = S.sort_values("Weighted score", ascending=False)
S.round(2).to_csv(out("tables", "candidate_scores.csv"))
TOP5 = list(S.index[:5])

fig, ax = plt.subplots(figsize=(10, 5.2))
cols = [TEAL if n in TOP5 else RULE for n in S.index]
ax.barh(range(len(S))[::-1], S["Weighted score"], color=cols, edgecolor=[INK if n in TOP5 else MUTED for n in S.index], lw=0.4)
for k, (n, v) in enumerate(S["Weighted score"].items()):
    ax.text(v + 0.03, len(S) - 1 - k, f"{v:.2f}", va="center", fontsize=9, color=INK if n in TOP5 else MUTED)
ax.set_yticks(range(len(S))[::-1]); ax.set_yticklabels(S.index, fontsize=9.5)
ax.set_xlim(0, 5.4); ax.set_xlabel("Weighted score (1 = poor, 5 = excellent)")
ax.set_title("Eleven agri-business ideas for Debre Markos, scored on seven criteria: the top five (teal) are planned in full", loc="left")
_save(fig, out("figures", "01_candidate_scores.png"))

# ===================================================================== 2. the five businesses
# Each business: capex items (birr), fixed costs per year (birr), and a per-year volume ramp with unit economics.
B = {}

B["Teff flour and injera bakery"] = dict(
    short="Teff & injera", colour=COPPER,
    capex={"Teff cleaner and destoner": 4_500 * USD, "Stone/hammer mill, 1 t/day": 6_000 * USD,
           "Electric mitads (24) and baking hall fit-out": 24 * 18_000 + 350_000, "Packing scale, sealer, shelves": 220_000,
           "Store and premises improvement (rented building)": 600_000, "Cargo three-wheeler": 900_000},
    fixed={"Manager": 25_000 * 12, "Bakers (8)": 8 * 9_000 * 12, "Mill operator and helpers (3)": 3 * 9_000 * 12,
           "Sales and delivery (2)": 2 * 10_000 * 12, "Rent": 30_000 * 12, "Licences, food safety, insurance": 120_000},
    lines={
        "Injera (pieces)": dict(volume=[180_000, 260_000, 300_000, 330_000, 330_000], price=40,  # assumption: Addis was 25 Br in 2023 (sourced)
                                unit_cost=12_000 / 500 + 5.0),  # teff 12,000 Br/qt (assumption) / 500 injera per qt (sourced) + energy, packing
        "Packed white teff flour (quintals)": dict(volume=[400, 800, 1_200, 1_400, 1_500], price=14_500,  # assumption, Addis 15,000 Br/qt (sourced 2025)
                                                   unit_cost=12_000 + 900),  # grain + cleaning loss, milling, bags, transport
    },
    working_capital_months=1.0, life_years=8)

B["Sheep fattening and breeding rams"] = dict(
    short="Sheep", colour=TEAL,
    capex={"Fattening shed and pens, 300 head (local materials, iron roof)": 1_400_000, "Feed store": 350_000,
           "Animal scale, feeders, water troughs": 180_000, "Forage chopper": 2_500 * USD, "Handling race and quarantine pen": 150_000},
    fixed={"Manager / livestock technician": 22_000 * 12, "Herders (4)": 4 * 8_000 * 12, "Guard": 7_000 * 12,
           "Vet contract and records": 60_000, "Land rent, 2 ha": 80_000},
    lines={  # three 90-day cycles timed to holidays (Meskel, Christmas/Timket, Easter)
        "Finished rams sold": dict(volume=[3 * 100 * 0.97, 3 * 200 * 0.97, 3 * 300 * 0.97, 3 * 300 * 0.97, 3 * 300 * 0.97],
                                   price=31 * 450,          # 31 kg x 450 Br/kg live weight (assumption)
                                   unit_cost=8_000 / 0.97 + 54 * 30 + 90 * 8 + 250),  # young ram 8,000 Br, concentrate, hay, vet (assumption)
        "Breeding rams from partner CBBP villages (resale)": dict(volume=[0, 40, 80, 120, 120], price=18_000, unit_cost=14_500),
    },
    working_capital_months=3.0, life_years=10)

B["Teff and wheat quality seed"] = dict(
    short="Quality seed", colour=BLUE,
    capex={"Seed cleaner-grader, locally made, 1 t/h": 850_000, "Rented store fit-out (pallets, ventilation, fumigation)": 450_000,
           "Moisture meter, germination kit, scales": 350_000, "Bag sewing machine and label printing": 120_000,
           "Demonstration and isolation plots equipment": 150_000},
    fixed={"Seed manager (agronomist)": 28_000 * 12, "Field supervisors (2)": 2 * 15_000 * 12, "Store and cleaning workers (3)": 3 * 9_000 * 12,
           "Store rent": 25_000 * 12, "Certification, inspection, CoC renewal": 150_000, "Transport hire": 200_000,
           "Demonstration plots and promotion": 200_000, "Insurance": 60_000},
    lines={  # contract outgrowers: 60 -> 250 ha teff; 0 -> 60 ha bread wheat. 15 qt/ha raw seed, 90 % passes cleaning
        "Certified/QDS teff seed (quintals)": dict(volume=[60 * 15 * 0.9, 120 * 15 * 0.9, 200 * 15 * 0.9, 250 * 15 * 0.9, 250 * 15 * 0.9],
                                                    price=15_000,      # assumption: grain ~11,500 Br/qt + 30 % seed premium
                                                    # pay outgrowers grain +10 % for raw seed; 10 % cleaned out is sold back as grain
                                                    unit_cost=(11_500 * 1.10 - 0.10 * 11_500) / 0.90 + 500),
        "Bread wheat seed (quintals)": dict(volume=[0, 20 * 35 * 0.9, 40 * 35 * 0.9, 60 * 35 * 0.9, 60 * 35 * 0.9],
                                            price=10_700,      # wheat retail 8,250 Br/qt (sourced 2026) + 30 %
                                            unit_cost=(8_250 * 1.10 - 0.10 * 8_250) / 0.90 + 450),
    },
    working_capital_months=4.0, life_years=10)

B["Honey: apiary, collection and packing"] = dict(
    short="Honey", colour=GOLD,
    capex={"Modern hives with colonies (200)": 200 * (6_000 + 3_000), "Extractor, uncapping tray, settling tanks": 3_500 * USD,
           "Honey house fit-out (food grade)": 450_000, "Jar filler, labels, refractometer": 1_800 * USD, "Protective kits and smoker (20)": 60_000},
    fixed={"Manager / apiculturist": 22_000 * 12, "Beekeepers (3)": 3 * 9_000 * 12, "Processing and packing (2)": 2 * 9_000 * 12,
           "Sales, transport to Bahir Dar and Addis": 180_000, "Licences, food safety, insurance": 80_000},
    lines={
        "Own apiary honey (kg)": dict(volume=[200 * 8, 200 * 14, 200 * 16, 200 * 16, 200 * 16], price=600, unit_cost=45),
        "Collected strained honey from member beekeepers (kg)": dict(volume=[8_000, 16_000, 25_000, 32_000, 35_000],
                                                                       price=600,  # wholesale branded jars; Addis retail up to 800 (sourced)
                                                                       unit_cost=420 / 0.95 + 45),  # pay 420 Br/kg (farm gate < 400, sourced) + loss + jar
        "Beeswax (kg)": dict(volume=[150, 350, 500, 620, 680], price=700, unit_cost=60),
    },
    working_capital_months=3.0, life_years=8)

B["Forage seed, hay and feed blocks"] = dict(
    short="Forage & feed", colour=BLUE,
    capex={"Hay baler (small, tractor-hire) and rakes": 9_000 * USD, "Hay barn 300 m²": 1_200_000,
           "Feed-block press and mixer": 4_000 * USD, "Forage seed cleaner": 2_500 * USD, "Scales and moisture meter": 120_000},
    fixed={"Manager (animal scientist)": 24_000 * 12, "Workers (5)": 5 * 8_500 * 12, "Tractor hire and fuel": 300_000,
           "Land rent 20 ha (oats-vetch, Desho, Rhodes)": 20 * 12_000, "Promotion and demos": 100_000},
    lines={
        "Oats-vetch and grass hay bales (25 kg)": dict(volume=[6_000, 12_000, 16_000, 18_000, 18_000], price=320, unit_cost=150),
        "Urea-molasses multi-nutrient blocks (pieces)": dict(volume=[3_000, 8_000, 12_000, 14_000, 15_000], price=420, unit_cost=260),
        "Forage seed and splits (kg)": dict(volume=[500, 1_500, 2_500, 3_000, 3_000], price=600, unit_cost=250),
    },
    working_capital_months=2.0, life_years=8)

# the guide template has one section per business in this order; keep the scores consistent with it
ORDER = ["Teff flour and injera bakery", "Sheep fattening and breeding rams", "Honey: apiary, collection and packing",
         "Teff and wheat quality seed", "Forage seed, hay and feed blocks"]
if TOP5 != ORDER:
    print("NOTE: the top five changed after rescoring:", TOP5, "- the guide keeps its section order:", ORDER)
    TOP5 = ORDER
missing = [n for n in TOP5 if n not in B]
assert not missing, f"top five changed, add a model for: {missing}"


def model(name, d, price_f=1.0, volume_f=1.0, cost_f=1.0, capex_f=1.0):
    capex = sum(d["capex"].values()) * capex_f
    fixed = sum(d["fixed"].values()) * cost_f
    rows = []
    for y in range(YEARS):
        rev = sum(l["volume"][y] * volume_f * l["price"] * price_f for l in d["lines"].values())
        var = sum(l["volume"][y] * volume_f * l["unit_cost"] * cost_f for l in d["lines"].values())
        rows.append((y + 1, rev, var, fixed))
    P = pd.DataFrame(rows, columns=["Year", "Revenue", "Variable costs", "Fixed costs"])
    P["Gross margin"] = P.Revenue - P["Variable costs"]
    P["EBITDA"] = P["Gross margin"] - P["Fixed costs"]
    P["Depreciation"] = capex / d["life_years"]
    wc = d["working_capital_months"] / 12 * (P["Variable costs"] + P["Fixed costs"])
    loan = (capex + wc.iloc[0]) * (1 - FIN["equity_share"])
    r, n = FIN["loan_rate"], FIN["loan_years"]
    g = FIN["grace_years"]                       # interest only during the grace period
    pay = loan * r / (1 - (1 + r) ** -(n - g))
    bal, interest, service = loan, [], []
    for y in range(YEARS):
        i_ = bal * r
        p_ = 0.0 if y < g else pay - i_
        bal -= p_
        interest.append(i_); service.append(i_ + p_)
    P["Interest"] = interest
    P["Profit before tax"] = P.EBITDA - P.Depreciation - P.Interest
    P["Tax"] = np.where(P["Profit before tax"] > 0, P["Profit before tax"] * FIN["tax_rate"], 0)
    P["Net profit"] = P["Profit before tax"] - P.Tax
    P["Debt service"] = service
    P["DSCR"] = (P.EBITDA - P.Tax) / P["Debt service"]
    # project cash flow (unlevered): -capex -wc at t0, then EBITDA - tax on EBIT - change in WC, salvage at end
    ebit = P.EBITDA - P.Depreciation
    tax_u = np.where(ebit > 0, ebit * FIN["tax_rate"], 0)
    dwc = wc.diff().fillna(0)
    salvage = capex * max(0, 1 - YEARS / d["life_years"]) + wc.iloc[-1]
    cf = np.concatenate([[-capex - wc.iloc[0]], (P.EBITDA - tax_u - dwc).values])
    cf[-1] += salvage
    disc = (1 + FIN["discount"]) ** -np.arange(YEARS + 1)
    npv = float(np.sum(cf * disc))
    try:
        from scipy.optimize import brentq
        irr = brentq(lambda x: np.sum(cf / (1 + x) ** np.arange(YEARS + 1)), -0.9, 5)
    except ValueError:
        irr = float("nan")
    cum = np.cumsum(cf)
    payback = next((k - 1 + (-cum[k - 1]) / (cum[k] - cum[k - 1]) for k in range(1, len(cum)) if cum[k] >= 0 > cum[k - 1]), float("nan"))
    # break-even revenue in a steady year (year 4): fixed / gross margin ratio
    y4 = P.iloc[3]
    be = y4["Fixed costs"] / (y4["Gross margin"] / y4.Revenue) if y4["Gross margin"] > 0 else float("nan")
    return dict(P=P, capex=capex, wc0=float(wc.iloc[0]), loan=loan, equity=(capex + wc.iloc[0]) * FIN["equity_share"], cf=cf,
                npv=npv, irr=irr, payback=payback, breakeven=be, be_share=be / y4.Revenue)


R = {n: model(n, B[n]) for n in TOP5}
summary = []
for n in TOP5:
    m, d = R[n], B[n]
    P = m["P"]
    jobs = sum(int(''.join(c for c in k.split("(")[-1] if c.isdigit()) or 1) if "(" in k and any(c.isdigit() for c in k.split("(")[-1]) else 1
               for k in d["fixed"] if not any(w in k for w in ["Rent", "rent", "Licen", "Certif", "Vet", "Insur", "Demo", "Sales,", "Tractor", "Land", "promotion", "Promotion"]))
    summary.append(dict(Business=n, **{"Investment (capex)": m["capex"], "Start-up working capital": m["wc0"], "Equity 30 %": m["equity"],
                                        "Loan 70 %": m["loan"], "Revenue year 4": P.Revenue.iloc[3], "EBITDA year 4": P.EBITDA.iloc[3],
                                        "Net profit year 1": P["Net profit"].iloc[0], "Net profit year 4": P["Net profit"].iloc[3],
                                        "Min DSCR": P.DSCR.min(), "NPV at 12 %": m["npv"], "IRR": m["irr"], "Payback (years)": m["payback"],
                                        "Break-even as % of year-4 sales": 100 * m["be_share"], "Direct jobs": jobs}))
    P.round(0).to_csv(out("tables", f"model_{TOP5.index(n) + 1}_{d['short'].split()[0].lower().replace('&', '')}.csv"), index=False)
SUM = pd.DataFrame(summary)
SUM.round(2).to_csv(out("tables", "five_business_summary.csv"), index=False)

# ===================================================================== 3. figures
fig, axes = plt.subplots(1, 5, figsize=(16, 4.2), sharey=False)
for ax, n in zip(axes, TOP5):
    P = R[n]["P"]; c = B[n]["colour"]
    ax.bar(P.Year - 0.2, P.Revenue / 1e6, 0.4, color=c, alpha=0.35, label="Revenue")
    ax.bar(P.Year + 0.2, P["Net profit"] / 1e6, 0.4, color=c, label="Net profit")
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_title(B[n]["short"], loc="left", fontsize=11); ax.set_xticks(P.Year)
    ax.set_xlabel("Year")
axes[0].set_ylabel("Million birr (2026 prices)"); axes[0].legend(frameon=False, fontsize=8.5)
fig.suptitle("Five-year revenue and net profit after interest and tax (70 % loan at 18 %, one-year grace)", x=0.01, ha="left", fontsize=12.5, fontweight="bold", y=1.04)
_save(fig, out("figures", "02_five_year_profit.png"))

fig, ax = plt.subplots(figsize=(9.5, 5))
for n in TOP5:
    m = R[n]
    ax.scatter(m["capex"] / 1e6, 100 * m["irr"], s=np.clip(m["npv"] / 6e3, 60, 1500), color=B[n]["colour"], alpha=0.8, edgecolor=INK, lw=0.5)
    ax.annotate(f"{B[n]['short']}\nNPV {m['npv'] / 1e6:.1f} M", (m["capex"] / 1e6, 100 * m["irr"]), xytext=(0, 22), textcoords="offset points",
                ha="center", fontsize=9)
ax.set_ylim(0, max(100 * R[n]["irr"] for n in TOP5) * 1.35); ax.set_xlim(0, max(R[n]["capex"] for n in TOP5) / 1e6 * 1.2)
ax.axhline(100 * FIN["discount"], color=RED, ls="--", lw=1)
ax.text(ax.get_xlim()[1], 100 * FIN["discount"], " 12 % hurdle", color=RED, va="bottom", ha="right", fontsize=8.5)
ax.set_xlabel("Investment in equipment and buildings (million birr)"); ax.set_ylabel("Project IRR (%, real)")
ax.set_title("Return against investment (bubble size = NPV at 12 %)", loc="left")
_save(fig, out("figures", "03_return_vs_investment.png"))

# tornado: NPV change for +-20 % in price, volume, costs, capex
TOR = []
for n in TOP5:
    base = R[n]["npv"]
    for lab, kw in [("Selling price", "price_f"), ("Volume sold", "volume_f"), ("Operating costs", "cost_f"), ("Investment", "capex_f")]:
        lo = model(n, B[n], **{kw: 0.8})["npv"]; hi = model(n, B[n], **{kw: 1.2})["npv"]
        TOR.append((n, lab, base, lo, hi))
T = pd.DataFrame(TOR, columns=["Business", "Driver", "Base NPV", "NPV at -20 %", "NPV at +20 %"])
T.round(0).to_csv(out("tables", "sensitivity_npv.csv"), index=False)
fig, axes = plt.subplots(1, 5, figsize=(16, 3.6), sharey=True)
for ax, n in zip(axes, TOP5):
    d = T[T.Business == n].iloc[::-1]
    for k, (_, r) in enumerate(d.iterrows()):
        for v in [(r["NPV at -20 %"] - r["Base NPV"]) / 1e6, (r["NPV at +20 %"] - r["Base NPV"]) / 1e6]:
            ax.barh(k, v, color=TEAL if v > 0 else RED, alpha=0.8)
    ax.axvline(0, color=INK, lw=0.6); ax.set_yticks(range(4)); ax.set_yticklabels(d.Driver)
    ax.set_title(B[n]["short"], loc="left", fontsize=11); ax.set_xlabel("Change in NPV (million birr)")
fig.suptitle("What moves the money: NPV change when one driver moves 20 % up or down (teal = NPV rises, red = NPV falls)", x=0.01, ha="left", fontsize=12.5, fontweight="bold", y=1.04)
_save(fig, out("figures", "04_sensitivity.png"))

# ===================================================================== 4. guide
def md_table(df, fmt="{:,.0f}"):
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


def capex_md(n):
    d = pd.DataFrame([(k, v) for k, v in B[n]["capex"].items()], columns=["Investment item", "Birr"])
    d.loc[len(d)] = ["**Total**", d.Birr.sum()]
    return md_table(d)


def fixed_md(n):
    d = pd.DataFrame([(k, v) for k, v in B[n]["fixed"].items()], columns=["Fixed cost per year", "Birr"])
    d.loc[len(d)] = ["**Total**", d.Birr.sum()]
    return md_table(d)


def lines_md(n):
    rows = [(k, f"{l['volume'][0]:,.0f} → {l['volume'][3]:,.0f}", l["price"], l["unit_cost"], l["price"] - l["unit_cost"]) for k, l in B[n]["lines"].items()]
    return md_table(pd.DataFrame(rows, columns=["Product", "Volume year 1 → year 4", "Price (birr/unit)", "Variable cost (birr/unit)", "Margin per unit"]))


def pl_md(n):
    P = R[n]["P"][["Year", "Revenue", "Variable costs", "Fixed costs", "EBITDA", "Interest", "Net profit", "DSCR"]].copy()
    for c in ["Revenue", "Variable costs", "Fixed costs", "EBITDA", "Interest", "Net profit"]:
        P[c] = P[c] / 1e6
    P = P.rename(columns={c: c + " (M birr)" for c in ["Revenue", "Variable costs", "Fixed costs", "EBITDA", "Interest", "Net profit"]})
    P["Year"] = P["Year"].astype(int)
    return md_table(P, "{:,.2f}")


def kpi(n):
    m = R[n]
    return (f"Investment **{m['capex'] / 1e6:,.1f} M birr** + start-up working capital {m['wc0'] / 1e6:,.1f} M · equity {m['equity'] / 1e6:,.1f} M, "
            f"loan {m['loan'] / 1e6:,.1f} M · NPV at 12 % **{m['npv'] / 1e6:,.1f} M birr** · IRR **{100 * m['irr']:.0f} %** · "
            f"payback **{m['payback']:.1f} years** · break-even at **{100 * m['be_share']:.0f} %** of year-4 sales")


SUMMD = SUM[["Business", "Investment (capex)", "Equity 30 %", "Revenue year 4", "Net profit year 4", "NPV at 12 %", "IRR", "Payback (years)", "Min DSCR"]].copy()
for c in ["Investment (capex)", "Equity 30 %", "Revenue year 4", "Net profit year 4", "NPV at 12 %"]:
    SUMMD[c] = SUMMD[c] / 1e6
SUMMD["IRR"] = 100 * SUMMD["IRR"]
SUMMD = SUMMD.rename(columns={"Investment (capex)": "Investment (M birr)", "Equity 30 %": "Your equity (M birr)", "Revenue year 4": "Revenue yr 4 (M)",
                              "Net profit year 4": "Net profit yr 4 (M)", "NPV at 12 %": "NPV 12 % (M)", "IRR": "IRR %"})
scores_md = S.copy(); scores_md.insert(0, "Idea", scores_md.index)
vals = {"scores": md_table(scores_md.reset_index(drop=True), "{:.2f}"), "summary": md_table(SUMMD, "{:,.2f}"),
        "usd": USD, "top5": ", ".join(TOP5)}
for k, n in enumerate(TOP5, 1):
    vals.update({f"capex{k}": capex_md(n), f"fixed{k}": fixed_md(n), f"lines{k}": lines_md(n), f"pl{k}": pl_md(n), f"kpi{k}": kpi(n)})
tpl = open(out("guide_template.md"), encoding="utf-8").read()
for k, v in vals.items():
    tpl = tpl.replace("{" + k + "}", str(v))
left = [l for l in tpl.splitlines() if "{" in l and "}" in l]
assert not left, left[:3]
open(out("README.md"), "w", encoding="utf-8").write(tpl)
json.dump({"top5": TOP5, "fin": FIN, "usd": USD}, open(out("tables", "key_results.json"), "w"), indent=1)
print(S.round(2)); print(SUM.round(2).T)
