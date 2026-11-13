"""Multi-environment trials (MET) for crop varieties.

Design (alpha-lattice), simulation of a teaching dataset, single-site analysis,
combined analysis over locations and years, AMMI, GGE biplot, stability and a
decision table.
"""
import itertools
import numpy as np
import pandas as pd
from scipy import stats
from .core import dummies, interaction, seq_anova, _fit

# ---------------------------------------------------------------------------
# 1. DESIGN: resolvable alpha(0,1) lattice
# ---------------------------------------------------------------------------

def alpha_array(k, s, r, seed=1, tries=200000):
    """Find a k x r generating array over Z_s so that every pair of entries
    meets in a block at most once (an alpha(0,1) design)."""
    rng = np.random.default_rng(seed)
    for _ in range(tries):
        a = np.zeros((k, r), int)
        a[:, 1:] = rng.integers(0, s, size=(k, r - 1))
        ok = True
        for i1, i2 in itertools.combinations(range(k), 2):
            d = (a[i1] - a[i2]) % s
            if len(set(d)) < r:
                ok = False
                break
        if ok:
            return a
    raise RuntimeError("No alpha(0,1) array found; try another seed or fewer reps")


def alpha_design(entries, k, reps, seed=1, blocks_per_row=2, plot_w=2.0, plot_l=2.0,
                 gap_plot=1.0, gap_block=1.5):
    """Randomised alpha-lattice field book.

    entries        : list of entry names (length v = s*k)
    k              : plots per incomplete block (needs k <= s = v/k for an alpha(0,1) design)
    blocks_per_row : incomplete blocks placed side by side in one field row
    Returns a DataFrame: rep, block, plot_in_block, plot (field number), entry,
    field_row, field_col and the plot corner position in metres.
    """
    v = len(entries)
    assert v % k == 0, "number of entries must be a multiple of block size"
    s = v // k
    assert k <= s, f"block size k={k} must be <= blocks per rep s={s}; use smaller blocks"
    assert s % blocks_per_row == 0
    rng = np.random.default_rng(seed)
    a = alpha_array(k, s, reps, seed)
    label = np.array(entries, dtype=object)[rng.permutation(v)]  # random entry -> design index
    rows_per_rep = s // blocks_per_row
    rows = []
    for rep in range(reps):
        for bi, j in enumerate(rng.permutation(s)):                # random block order
            idx = [i * s + (a[i, rep] + j) % s for i in range(k)]
            idx = [idx[t] for t in rng.permutation(k)]             # random plot order
            frow = rep * rows_per_rep + bi // blocks_per_row + 1
            cgrp = bi % blocks_per_row
            if frow % 2 == 0:                                      # serpentine: even rows run back
                cgrp = blocks_per_row - 1 - cgrp
            for p, d in enumerate(idx):
                pos = p if frow % 2 else k - 1 - p
                col = cgrp * k + pos + 1
                rows.append(dict(rep=rep + 1, block=bi + 1, plot_in_block=p + 1, entry=label[d],
                                 field_row=frow, field_col=col))
    fb = pd.DataFrame(rows)
    fb = fb.sort_values(["field_row", "field_col"]).reset_index(drop=True)
    # serpentine plot numbers: rep*100 + running number, the order you walk the field
    fb["walk"] = [r * 1000 + (c if r % 2 else 1000 - c) for r, c in zip(fb.field_row, fb.field_col)]
    fb = fb.sort_values("walk").reset_index(drop=True)
    fb["plot"] = fb["rep"] * 100 + fb.groupby("rep").cumcount() + 1
    fb = fb.drop(columns="walk")
    grp = (fb["field_col"] - 1) // k
    fb["x_m"] = (fb["field_col"] - 1) * (plot_w + gap_plot) + grp * (gap_block - gap_plot)
    fb["y_m"] = (fb["field_row"] - 1) * (plot_l + gap_block)
    return fb[["plot", "rep", "block", "plot_in_block", "entry", "field_row", "field_col", "x_m", "y_m"]]


def concurrence_check(fb):
    """Max number of times any two entries share a block (1 = perfect alpha(0,1))."""
    from collections import Counter
    c = Counter()
    for _, g in fb.groupby(["rep", "block"]):
        for p in itertools.combinations(sorted(g["entry"]), 2):
            c[p] += 1
    return max(c.values())


# ---------------------------------------------------------------------------
# 2. TEACHING DATA: simulate a realistic multi-location, multi-year trial
# ---------------------------------------------------------------------------

def simulate_met(fieldbooks, genos, env_info, seed=7, mu=2.3, sd_g=0.16, sd_gl=0.30,
                 sd_gy=0.09, sd_gly=0.12, sd_block=0.08, sd_rep=0.05, sd_e=0.21):
    """Simulate grain yield (t/ha) and days to maturity.

    fieldbooks: dict env -> field book (each year is re-randomised)

    env_info: DataFrame with location, year, env, loc_effect, year_effect, stress (0..1).
    G x L has a real, repeatable pattern: some genotypes are drought tolerant
    (do better at dry sites), others need high rainfall.
    """
    rng = np.random.default_rng(seed)
    G = len(genos)
    g_eff = pd.Series(rng.normal(0, sd_g, G), index=genos)
    tol = pd.Series(rng.normal(0, 1, G), index=genos)              # drought tolerance score
    mat = pd.Series(rng.normal(0, 5, G), index=genos)              # maturity (days)
    for c, (ge, t, m) in {"Check-Quncho": (0.18, -0.6, 4), "Check-Tsedey": (-0.10, 1.4, -14)}.items():
        if c in genos:
            g_eff[c], tol[c], mat[c] = ge, t, m
    locs = env_info["location"].unique()
    years = env_info["year"].unique()
    gl = {(g, l): rng.normal(0, sd_gl * 0.5) for g in genos for l in locs}
    gy = {(g, y): rng.normal(0, sd_gy) for g in genos for y in years}
    out = []
    for _, e in env_info.iterrows():
        fb = fieldbooks[e["env"]].copy()
        fb["location"], fb["year"], fb["env"] = e["location"], e["year"], e["env"]
        rep_eff = {r: rng.normal(0, sd_rep) for r in fb["rep"].unique()}
        blk_eff = {b: rng.normal(0, sd_block) for b in fb[["rep", "block"]].apply(tuple, axis=1).unique()}
        ymean = mu + e["loc_effect"] + e["year_effect"]
        vals = []
        for _, p in fb.iterrows():
            g = p["entry"]
            inter = (sd_gl * 0.9 * tol[g] * (e["stress"] - 0.4)                  # crossover by moisture
                     + gl[(g, e["location"])] + gy[(g, e["year"])] + rng.normal(0, sd_gly))
            yv = (ymean + g_eff[g] + inter + rep_eff[p["rep"]] + blk_eff[(p["rep"], p["block"])]
                  + rng.normal(0, sd_e))
            vals.append(max(0.2, yv))
        fb["yield_t_ha"] = np.round(vals, 3)
        fb["days_to_maturity"] = np.round(105 - 12 * e["stress"] + mat[fb["entry"]].values
                                          + rng.normal(0, 2.5, len(fb))).astype(int)
        out.append(fb)
    return pd.concat(out, ignore_index=True)


# ---------------------------------------------------------------------------
# 3. SINGLE-SITE ANALYSIS (one location in one year)
# ---------------------------------------------------------------------------

def site_analysis(d, trait="yield_t_ha"):
    """Alpha-lattice ANOVA for one environment.

    Model: y = mean + rep + block(rep) + genotype + error.
    Genotype is entered last, so its test is adjusted for incomplete blocks.
    Returns (anova table, adjusted means Series, summary dict).
    """
    y = d[trait].values
    R = dummies(d["rep"])
    B = dummies(interaction(d["rep"], d["block"]))
    Gm = dummies(d["entry"])
    tab = seq_anova(y, [("Replication", R), ("Block(Rep), unadjusted", B), ("Genotype, adjusted", Gm)])
    # adjusted (least-squares) means: genotype effect + average block and rep effect
    X = np.hstack([np.ones((len(y), 1)), R, B, Gm])
    _, _, beta = _fit(X, y)
    nR, nB = R.shape[1], B.shape[1]
    # average the fitted block environment over all incomplete blocks (an estimable function)
    _, first = np.unique(interaction(d["rep"], d["block"]), return_index=True)
    block_rows = np.hstack([np.ones((len(first), 1)), R[first], B[first]])
    base = float((block_rows @ beta[:1 + nR + nB]).mean())
    cats = pd.Categorical(d["entry"]).categories
    geff = np.concatenate([[0.0], beta[1 + nR + nB:]])
    adj = pd.Series(base + geff, index=cats)
    # RCBD analysis of the same data, to show what the incomplete blocks gained
    rc = seq_anova(y, [("Replication", R), ("Genotype", Gm)])
    mse, mse_rcbd = tab["MS"].iloc[-1], rc["MS"].iloc[-1]
    r = d["rep"].nunique()
    ms_g = tab.loc[tab.Source.str.startswith("Genotype"), "MS"].iloc[0]
    var_g = max(0.0, (ms_g - mse) / r)
    summ = dict(env=d["env"].iloc[0], mean=float(np.mean(y)), mse=float(mse), df_e=int(tab["df"].iloc[-1]),
                cv_pct=float(100 * np.sqrt(mse) / np.mean(y)), lsd5=float(stats.t.ppf(0.975, tab["df"].iloc[-1]) * np.sqrt(2 * mse / r)),
                h2=float(var_g / (var_g + mse / r)) if var_g > 0 else 0.0,
                efficiency_vs_rcbd_pct=float(100 * mse_rcbd / mse),
                p_genotype=float(tab.loc[tab.Source.str.startswith("Genotype"), "p"].iloc[0]))
    return tab, adj, summ


# ---------------------------------------------------------------------------
# 4. COMBINED ANALYSIS over locations and years
# ---------------------------------------------------------------------------

def combined_anova(means, site_summ, reps):
    """Combined ANOVA from adjusted means (genotype x location x year) and the
    pooled within-site error, as GenStat and most breeding reports do.

    means: DataFrame with columns entry, location, year, mean.
    Locations and years are treated as random (they sample the target region and
    the future seasons), so G is tested against G x L + G x Y - G x L x Y.
    """
    from .core import dummies as dm
    m = means.copy()
    gN, lN, yN = m.entry.nunique(), m.location.nunique(), m.year.nunique()
    Y = m["mean"].values
    terms = [("Year (Y)", dm(m.year)), ("Location (L)", dm(m.location)),
             ("L x Y", dm(interaction(m.location, m.year))),
             ("Genotype (G)", dm(m.entry)), ("G x L", dm(interaction(m.entry, m.location))),
             ("G x Y", dm(interaction(m.entry, m.year)))]
    t = seq_anova(Y, terms)
    t.loc[t.Source == "Residual", "Source"] = "G x L x Y"
    t["SS"] *= reps                     # put on a plot basis
    t["MS"] = t["SS"] / t["df"]
    df_err = int(site_summ["df_e"].sum())
    ss_err = float((site_summ["mse"] * site_summ["df_e"]).sum())
    ms_err = ss_err / df_err
    t = pd.concat([t[["Source", "df", "SS", "MS"]],
                   pd.DataFrame([["Pooled error", df_err, ss_err, ms_err]], columns=["Source", "df", "SS", "MS"])],
                  ignore_index=True)
    ms = dict(zip(t.Source, t.MS)); dfs = dict(zip(t.Source, t.df))
    # F tests with the right denominators (random L and Y)
    F, P = {}, {}
    for a, b in [("G x L x Y", "Pooled error"), ("G x L", "G x L x Y"), ("G x Y", "G x L x Y")]:
        F[a] = ms[a] / ms[b]; P[a] = stats.f.sf(F[a], dfs[a], dfs[b])
    den = ms["G x L"] + ms["G x Y"] - ms["G x L x Y"]
    df_den = den ** 2 / (ms["G x L"] ** 2 / dfs["G x L"] + ms["G x Y"] ** 2 / dfs["G x Y"] + ms["G x L x Y"] ** 2 / dfs["G x L x Y"])
    F["Genotype (G)"] = ms["Genotype (G)"] / den; P["Genotype (G)"] = stats.f.sf(F["Genotype (G)"], dfs["Genotype (G)"], df_den)
    for a in ["Year (Y)", "Location (L)"]:
        F[a] = ms[a] / ms["L x Y"]; P[a] = stats.f.sf(F[a], dfs[a], dfs["L x Y"])
    F["L x Y"] = ms["L x Y"] / ms["Pooled error"]; P["L x Y"] = stats.f.sf(F["L x Y"], dfs["L x Y"], df_err)
    t["F"] = t.Source.map(F); t["p"] = t.Source.map(P)
    total = t.loc[t.Source != "Pooled error", "SS"].sum()
    t["% of SS"] = np.where(t.Source != "Pooled error", 100 * t.SS / total, np.nan)
    # variance components on the plot scale from expected mean squares
    e = ms["Pooled error"]
    vc = dict(error=e,
              gly=max(0, (ms["G x L x Y"] - e) / reps),
              gl=max(0, (ms["G x L"] - ms["G x L x Y"]) / (reps * yN)),
              gy=max(0, (ms["G x Y"] - ms["G x L x Y"]) / (reps * lN)),
              g=max(0, (ms["Genotype (G)"] - ms["G x L"] - ms["G x Y"] + ms["G x L x Y"]) / (reps * lN * yN)))
    return t, vc, dict(G=gN, L=lN, Y=yN, r=reps)


def heritability(vc, L, Y, r):
    """Broad-sense heritability of a genotype mean over L locations, Y years, r reps."""
    return vc["g"] / (vc["g"] + vc["gl"] / L + vc["gy"] / Y + vc["gly"] / (L * Y) + vc["error"] / (L * Y * r))


# ---------------------------------------------------------------------------
# 5. AMMI, GGE and stability on the genotype x environment table
# ---------------------------------------------------------------------------

def ge_table(means):
    return means.pivot_table(index="entry", columns="env", values="mean")


def ammi(M, reps, ms_err, df_err):
    """AMMI: additive main effects + PCA of the interaction residuals."""
    X = M.values
    g, e = X.shape
    inter = X - X.mean(1, keepdims=True) - X.mean(0, keepdims=True) + X.mean()
    U, S, Vt = np.linalg.svd(inter, full_matrices=False)
    n_ax = min(g - 1, e - 1)
    ss_ge = reps * (inter ** 2).sum()
    rows = []
    for i in range(n_ax):
        ss = reps * S[i] ** 2
        df = g + e - 1 - 2 * (i + 1)
        rows.append([f"IPCA{i+1}", df, ss, ss / df, 100 * S[i] ** 2 / (S[:n_ax] ** 2).sum()])
    t = pd.DataFrame(rows, columns=["Source", "df", "SS", "MS", "% of G x E"])
    t["F"] = t.MS / ms_err
    t["p"] = stats.f.sf(t.F, t.df, df_err)
    gs = pd.DataFrame({"IPCA1": U[:, 0] * np.sqrt(S[0]), "IPCA2": U[:, 1] * np.sqrt(S[1])}, index=M.index)
    es = pd.DataFrame({"IPCA1": Vt[0] * np.sqrt(S[0]), "IPCA2": Vt[1] * np.sqrt(S[1])}, index=M.columns)
    # AMMI stability value (Purchase et al. 2000): smaller = more stable
    ss1, ss2 = S[0] ** 2, S[1] ** 2
    gs["ASV"] = np.sqrt((ss1 / ss2 * gs["IPCA1"]) ** 2 + gs["IPCA2"] ** 2)
    return t.head(4), gs, es, ss_ge


def gge(M):
    """GGE biplot coordinates (environment-centred, symmetric scaling)."""
    X = M.values - M.values.mean(0, keepdims=True)
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    gs = pd.DataFrame(U[:, :2] * np.sqrt(S[:2]), index=M.index, columns=["PC1", "PC2"])
    es = pd.DataFrame(Vt[:2].T * np.sqrt(S[:2]), index=M.columns, columns=["PC1", "PC2"])
    for c in ["PC1", "PC2"]:                     # orient so most environments point to + side
        if es[c].mean() < 0:
            gs[c] *= -1; es[c] *= -1
    expl = 100 * S[:2] ** 2 / (S ** 2).sum()
    # which genotype wins in each environment according to the 2-PC GGE model
    pred = gs.values @ es.values.T
    winners = pd.Series(M.index[pred.argmax(0)], index=M.columns)
    return gs, es, expl, winners


def stability(M):
    """Finlay-Wilkinson slope b, Eberhart-Russell deviation S2d, Wricke ecovalence W2."""
    X = M.values
    env_idx = X.mean(0) - X.mean()
    rows = []
    for i, g in enumerate(M.index):
        yi = X[i]
        b, a = np.polyfit(env_idx, yi, 1)
        dev = yi - (a + b * env_idx)
        s2d = (dev ** 2).sum() / (len(yi) - 2)
        w2 = ((yi - yi.mean() - X.mean(0) + X.mean()) ** 2).sum()
        rows.append([g, yi.mean(), b, s2d, w2])
    return pd.DataFrame(rows, columns=["entry", "mean", "b_FW", "S2d", "W2"]).set_index("entry")


def decision_table(M, checks, amm_g, stab, maturity, price_birr_per_kg):
    """Rank candidates the way a release committee would."""
    best_check = M.loc[checks].mean(1).idxmax()
    d = pd.DataFrame(index=M.index)
    d["mean_t_ha"] = M.mean(1)
    d["vs_best_check_pct"] = 100 * (d.mean_t_ha / M.loc[best_check].mean() - 1)
    d["wins_vs_check_pct"] = 100 * (M.values > M.loc[best_check].values).mean(1)
    d["worst_env_t_ha"] = M.min(1)
    d["b_FW"] = stab["b_FW"]
    d["ASV"] = amm_g["ASV"]
    d["maturity_days"] = maturity.reindex(M.index)
    d["extra_birr_per_ha"] = (d.mean_t_ha - M.loc[best_check].mean()) * 1000 * price_birr_per_kg
    d["rank_mean"] = d.mean_t_ha.rank(ascending=False)
    d["rank_ASV"] = d.ASV.rank()
    d["rank_sum"] = d.rank_mean + d.rank_ASV
    return d.sort_values("rank_sum"), best_check
