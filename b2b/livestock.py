"""Livestock designs and analysis.

A. Community-based breeding: on-farm records, sire-model heritability, BLUP
   breeding values for bucks, sire x village (G x E) and genetic gain.
B. Fattening trial: randomised complete blocks by initial weight, ANCOVA,
   Tukey test, growth curves and partial budget analysis.
"""
import numpy as np
import pandas as pd
from scipy import stats
from .core import dummies, interaction, seq_anova, tukey_hsd


# ---------------------------------------------------------------------------
# A. COMMUNITY-BASED BREEDING PROGRAMME
# ---------------------------------------------------------------------------

def simulate_cbbp(n_sires=24, villages=("Village A", "Village B", "Village C"), years=(2023, 2024, 2025),
                  kids_per_sire_year=14, mean=9.2, sd_a=1.45, sd_p=2.74, sd_sv=0.30, seed=3):
    """Six-month weight records of kids, as recorded by enumerators in a CBBP.

    Each buck serves two consecutive seasons, rotated to a second village. Fixed effects
    reflect what CBBP studies report: sex, birth type, dam parity, season.
    sd_a and sd_p follow published values for six-month weight of a
    community-bred indigenous goat (sigma_a 1.45 kg, sigma_p 2.74 kg).
    """
    rng = np.random.default_rng(seed)
    var_s = sd_a ** 2 / 4
    var_e = sd_p ** 2 - var_s
    sire_eff = rng.normal(0, np.sqrt(var_s), n_sires)
    v_eff = dict(zip(villages, [0.0, -0.6, 0.5]))
    y_eff = dict(zip(years, [0.0, -0.5, 0.3]))
    sv_eff = {(s, v): rng.normal(0, sd_sv) for s in range(n_sires) for v in villages}
    rows = []
    for s in range(n_sires):
        start = years[s % (len(years) - 1)]
        # bucks are rotated: one village in their first season, the next village in the second
        for k, yr in enumerate((start, start + 1)):
            v = villages[(s + k) % len(villages)]
            for _ in range(kids_per_sire_year + rng.integers(-5, 6)):
                sex = rng.choice(["male", "female"])
                btype = rng.choice(["single", "twin"], p=[0.7, 0.3])
                parity = rng.choice(["1", "2-3", "4+"], p=[0.3, 0.45, 0.25])
                season = rng.choice(["wet", "dry"])
                w = (mean + v_eff[v] + y_eff[yr] + (0.8 if sex == "male" else -0.4) + (-0.9 if btype == "twin" else 0.2)
                     + {"1": -0.5, "2-3": 0.1, "4+": 0.3}[parity] + (0.4 if season == "wet" else -0.4)
                     + sire_eff[s] + sv_eff[(s, v)] + rng.normal(0, np.sqrt(var_e - sd_sv ** 2)))
                rows.append(dict(kid_id=len(rows) + 1, sire=f"Buck{s + 1:02d}", village=v, year=yr, season=season,
                                 sex=sex, birth_type=btype, dam_parity=parity, weight_6m_kg=round(max(3.5, w), 2)))
    return pd.DataFrame(rows), pd.Series(2 * sire_eff, index=[f"Buck{s + 1:02d}" for s in range(n_sires)])


FIXED = ["village", "year", "season", "sex", "birth_type", "dam_parity"]


def sire_model(d, trait="weight_6m_kg", fixed=FIXED):
    """Least-squares ANOVA with sire last, ANOVA (Henderson I-type) variance
    components and heritability h2 = 4 s2_sire / (s2_sire + s2_e)."""
    y = d[trait].values
    terms = [(f, dummies(d[f])) for f in fixed] + [("Sire (adjusted)", dummies(d["sire"]))]
    tab = seq_anova(y, terms)
    ms_s = tab.loc[tab.Source == "Sire (adjusted)", "MS"].iloc[0]
    df_s = int(tab.loc[tab.Source == "Sire (adjusted)", "df"].iloc[0])
    ms_e = tab["MS"].iloc[-1]
    n = d.groupby("sire").size()
    N, s = len(d), len(n)
    k0 = (N - (n ** 2).sum() / N) / (s - 1)
    var_s = max(1e-9, (ms_s - ms_e) / k0)
    h2 = 4 * var_s / (var_s + ms_e)
    t = var_s / (var_s + ms_e)
    se_h2 = 4 * np.sqrt(2 * (1 - t) ** 2 * (1 + (k0 - 1) * t) ** 2 / (k0 * (k0 - 1) * (s - 1)))
    return tab, dict(var_sire=var_s, var_e=ms_e, var_p=var_s + ms_e, h2=h2, se_h2=se_h2, k0=k0, n_sires=s, df_sire=df_s)


def sire_blup(d, var_s, var_e, trait="weight_6m_kg", fixed=FIXED):
    """Solve Henderson's mixed-model equations for a sire model.
    Returns EBV (= 2 x sire solution), accuracy and number of progeny."""
    y = d[trait].values
    X = np.hstack([np.ones((len(d), 1))] + [dummies(d[f]) for f in fixed])
    Z = dummies(d["sire"], drop_first=False)
    lam = var_e / var_s
    LHS = np.block([[X.T @ X, X.T @ Z], [Z.T @ X, Z.T @ Z + lam * np.eye(Z.shape[1])]])
    RHS = np.concatenate([X.T @ y, Z.T @ y])
    C = np.linalg.pinv(LHS)
    sol = C @ RHS
    p = X.shape[1]
    u = sol[p:]
    pev = np.diag(C)[p:] * var_e
    rel = np.clip(1 - pev / var_s, 0, 1)
    sires = pd.Categorical(d["sire"]).categories
    out = pd.DataFrame({"EBV_kg": 2 * u, "accuracy": np.sqrt(rel),
                        "progeny": d.groupby("sire").size().reindex(sires).values}, index=sires)
    out["SE_EBV"] = 2 * np.sqrt(pev)
    return out.sort_values("EBV_kg", ascending=False)


def sire_by_village(d, trait="weight_6m_kg"):
    """Test sire x village and estimate the genetic correlation between villages
    rg = s2_sire / (s2_sire + s2_sire.village). Needs bucks used in more than one village."""
    y = d[trait].values
    sv = interaction(d["sire"], d["village"])
    terms = [(f, dummies(d[f])) for f in FIXED] + [("Sire", dummies(d["sire"])), ("Sire x village", dummies(sv))]
    tab = seq_anova(y, terms)
    return tab


def genetic_gain(sd_a, h2, prop_bucks_kept=0.25, L_male=2.5, L_female=3.5, years=10):
    """Annual response when young bucks are selected on their own six-month weight
    (accuracy = sqrt(h2)) and does are not selected."""
    i_m = stats.norm.pdf(stats.norm.ppf(1 - prop_bucks_kept)) / prop_bucks_kept
    dg = i_m * np.sqrt(h2) * sd_a / (L_male + L_female)
    return dict(i_male=i_m, gain_per_year=dg, cumulative=[dg * t for t in range(years + 1)])


# ---------------------------------------------------------------------------
# B. FATTENING TRIAL
# ---------------------------------------------------------------------------

def rcbd_by_weight(initial_weights, treatments, seed=5):
    """Block animals by initial weight (heaviest t together) and randomise
    treatments inside each block. Returns the allocation table."""
    rng = np.random.default_rng(seed)
    w = pd.Series(initial_weights).sort_values(ascending=False)
    t = len(treatments)
    rows = []
    for b in range(len(w) // t):
        ids = w.index[b * t:(b + 1) * t]
        for a, tr in zip(ids, rng.permutation(treatments)):
            rows.append(dict(goat_id=a, block=b + 1, treatment=tr, initial_wt_kg=w[a]))
    return pd.DataFrame(rows)


def simulate_fattening(alloc, adg_g, days=90, every=15, sd_adg=12, seed=8):
    rng = np.random.default_rng(seed)
    rows = []
    for _, a in alloc.iterrows():
        adg = rng.normal(adg_g[a.treatment], sd_adg) + 0.6 * (a.initial_wt_kg - alloc.initial_wt_kg.mean())
        for day in range(0, days + 1, every):
            wt = a.initial_wt_kg + adg / 1000 * day + (rng.normal(0, 0.35) if day else 0)
            rows.append(dict(goat_id=a.goat_id, block=a.block, treatment=a.treatment, day=day, weight_kg=round(wt, 2)))
    return pd.DataFrame(rows)


def fattening_analysis(w, days=90, order=None):
    first = w[w.day == 0].set_index("goat_id")
    last = w[w.day == days].set_index("goat_id")
    a = first[["block", "treatment"]].copy()
    a["initial_kg"] = first.weight_kg
    a["final_kg"] = last.weight_kg
    a["adg_g"] = (a.final_kg - a.initial_kg) / days * 1000
    y = a.adg_g.values
    rcbd = seq_anova(y, [("Block", dummies(a.block)), ("Ration", dummies(a.treatment))])
    ancova = seq_anova(y, [("Block", dummies(a.block)), ("Initial weight (covariate)", a[["initial_kg"]].values - a.initial_kg.mean()),
                           ("Ration (adjusted)", dummies(a.treatment))])
    means = a.groupby("treatment").adg_g.mean()
    if order:
        means = means.reindex(order)
    n = a.groupby("treatment").size().iloc[0]
    letters, hsd = tukey_hsd(means, n, rcbd["MS"].iloc[-1], int(rcbd["df"].iloc[-1]))
    summ = a.groupby("treatment").agg(initial_kg=("initial_kg", "mean"), final_kg=("final_kg", "mean"),
                                      adg_g=("adg_g", "mean"), sd_adg=("adg_g", "std"))
    if order:
        summ = summ.reindex(order)
    summ["tukey"] = [letters[t] for t in summ.index]
    return a, rcbd, ancova, summ, hsd


def partial_budget(summ, days, feed, prices, order):
    """Partial budget per goat (CIMMYT method): only costs that differ between rations.
    feed: dict ration -> dict feed_name -> kg per goat per day."""
    rows = []
    for t in order:
        s = summ.loc[t]
        buy = s.initial_kg * prices["buy_birr_per_kg"]
        sell = s.final_kg * prices["sell_birr_per_kg"]
        feed_cost = sum(kg * days * prices[f + "_birr_per_kg"] for f, kg in feed[t].items())
        rows.append(dict(ration=t, purchase=buy, sale=sell, gross_margin=sell - buy, feed_cost=feed_cost,
                         net_return=sell - buy - feed_cost))
    pb = pd.DataFrame(rows).set_index("ration")
    pb = pb.sort_values("feed_cost")
    # dominance analysis and marginal rate of return
    pb["dominated"] = False
    best = -np.inf
    for t in pb.index:
        if pb.loc[t, "net_return"] <= best:
            pb.loc[t, "dominated"] = True
        else:
            best = pb.loc[t, "net_return"]
    pb["MRR_pct"] = np.nan
    prev = None
    for t in pb.index[~pb.dominated]:
        if prev is not None:
            dni = pb.loc[t, "net_return"] - pb.loc[prev, "net_return"]
            dvc = pb.loc[t, "feed_cost"] - pb.loc[prev, "feed_cost"]
            pb.loc[t, "MRR_pct"] = 100 * dni / dvc if dvc > 0 else np.nan
        prev = t
    return pb.reindex(order)
