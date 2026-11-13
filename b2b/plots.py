"""Figures for decision making. matplotlib only."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.spatial import ConvexHull

INK, MUTED, RULE = "#131a24", "#56606f", "#d6dbe2"
COPPER, TEAL, GOLD, BLUE, RED = "#b5602b", "#0f7a6c", "#c98a12", "#2f7fd1", "#b8321a"
LOC_COL = [TEAL, COPPER, BLUE, GOLD, "#7a4fb5", "#4a7a2c"]
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 12, "figure.dpi": 110, "savefig.dpi": 150,
                     "savefig.bbox": "tight"})


def _save(fig, path):
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def field_map(fb, checks, path, title):
    fig, ax = plt.subplots(figsize=(11, 13))
    rep_col = {1: "#e0f1ee", 2: "#f7e7dc", 3: "#e3ecf8", 4: "#f3ecd6"}
    for _, p in fb.iterrows():
        chk = p.entry in checks
        ax.add_patch(Rectangle((p.x_m, p.y_m), 2, 2, facecolor=COPPER if chk else rep_col[p.rep],
                               edgecolor=INK if chk else MUTED, lw=1.2 if chk else 0.5))
        ax.text(p.x_m + 1, p.y_m + 0.75, p.entry.replace("Check-", ""), ha="center", va="center", fontsize=6.3,
                color="white" if chk else INK, fontweight="bold" if chk else "normal")
        ax.text(p.x_m + 1, p.y_m + 1.45, str(p["plot"]), ha="center", va="center", fontsize=5.5,
                color="white" if chk else MUTED)
    for (r, b), g in fb.groupby(["rep", "block"]):
        x0, y0 = g.x_m.min() - 0.25, g.y_m.min() - 0.25
        ax.add_patch(Rectangle((x0, y0), g.x_m.max() - g.x_m.min() + 2.5, 2.5, fill=False, edgecolor=TEAL, lw=1.3))
        right = g.x_m.min() > fb.x_m.max() / 2
        ax.text(g.x_m.max() + 2.7 if right else x0 - 0.4, y0 + 1.25, f"R{r}B{b}", ha="left" if right else "right",
                va="center", fontsize=6.5, color=TEAL)
    W, L = fb.x_m.max() + 2, fb.y_m.max() + 2
    ax.set_xlim(-4, W + 4); ax.set_ylim(L + 2, -3); ax.set_aspect("equal")
    ax.set_xlabel("metres"); ax.set_ylabel("metres")
    ax.set_title(f"{title}: {len(fb)} plots of 2 m x 2 m, field {W:.1f} m x {L:.1f} m")
    ax.annotate("", xy=(W, -1.8), xytext=(0, -1.8), arrowprops=dict(arrowstyle="<->", color=MUTED))
    ax.text(W / 2, -2.3, f"{W:.1f} m", ha="center", color=MUTED)
    ax.text(0, L + 1.4, "Upper number = plot number (walk in serpentine order). Copper = check varieties. "
            "Colour = replicate. Teal box = incomplete block.", fontsize=8, color=MUTED)
    _save(fig, path)


def env_box(d, env, path):
    order = env.env.tolist()
    locs = list(dict.fromkeys(env.location))
    fig, ax = plt.subplots(figsize=(11, 4.6))
    data = [d.loc[d.env == e, "yield_t_ha"].values for e in order]
    bp = ax.boxplot(data, patch_artist=True, widths=0.6, medianprops=dict(color=INK), flierprops=dict(markersize=2))
    for patch, e in zip(bp["boxes"], order):
        loc = env.set_index("env").loc[e, "location"]
        patch.set_facecolor(LOC_COL[locs.index(loc)]); patch.set_alpha(0.75)
    ax.set_xticks(range(1, len(order) + 1)); ax.set_xticklabels(order)
    ax.set_ylabel("Grain yield (t/ha), all plots")
    ax.set_title("Environments differ more than varieties: yield in every location and year")
    for i, l in enumerate(locs):
        ax.plot([], [], "s", color=LOC_COL[i], label=l)
    ax.legend(ncol=len(locs), frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    _save(fig, path)


def ss_share(comb, path):
    t = comb[comb.Source != "Pooled error"].copy()
    fig, ax = plt.subplots(figsize=(8, 4))
    cols = [MUTED if s in ("Year (Y)", "Location (L)", "L x Y") else COPPER if s == "Genotype (G)" else TEAL for s in t.Source]
    ax.barh(t.Source[::-1], t["% of SS"][::-1], color=cols[::-1])
    for i, (v, p) in enumerate(zip(t["% of SS"][::-1], t["p"][::-1])):
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        ax.text(v + 0.6, i, f"{v:.1f}%  {sig}", va="center", fontsize=9)
    ax.set_xlabel("% of total sum of squares (plot basis)")
    ax.set_title("Where the variation comes from (grey: environment, copper: variety, teal: G x E)")
    ax.set_xlim(0, t["% of SS"].max() * 1.25)
    _save(fig, path)


def h2_plan(plan, path):
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for i, (Y, g) in enumerate(plan.groupby("years")):
        ax.plot(g.locations, g.H2, "-o", ms=4, color=[MUTED, TEAL, COPPER, BLUE, GOLD][i], label=f"{Y} year{'s' if Y > 1 else ''}")
    ax.axhline(0.8, ls="--", color=RED, lw=1); ax.text(1, 0.81, "target 0.80", ha="left", va="bottom", color=RED, fontsize=9)
    ax.set_xlabel("Number of locations (3 replicates each)"); ax.set_ylabel("Heritability of a variety mean")
    ax.set_title("How many locations and years do you need?")
    ax.set_ylim(0, 1); ax.legend(frameon=False)
    _save(fig, path)


def ammi1(GE, g, e, checks, top, path):
    fig, ax = plt.subplots(figsize=(8, 6))
    gm = GE.mean(1); em = GE.mean(0)
    ax.scatter(gm, g.IPCA1, s=18, color=TEAL, alpha=0.7, label="varieties")
    ax.scatter(em, e.IPCA1, s=60, marker="^", color=COPPER, label="environments")
    for env_, x, y in zip(GE.columns, em, e.IPCA1):
        ax.text(x, y + 0.012, env_, color=COPPER, fontsize=8, ha="center")
    for n in list(top) + checks:
        ax.annotate(n.replace("Check-", "chk "), (gm[n], g.IPCA1[n]), xytext=(4, 3), textcoords="offset points",
                    fontsize=8, color=RED if n in checks else INK, fontweight="bold")
    ax.axvline(GE.values.mean(), color=MUTED, lw=0.8); ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xlabel("Mean grain yield (t/ha)"); ax.set_ylabel("IPCA1 score (interaction)")
    ax.set_title("AMMI1: right = high yield, near the zero line = stable")
    ax.legend(frameon=False, loc="lower left")
    _save(fig, path)


def gge_www(g, e, expl, checks, path):
    fig, ax = plt.subplots(figsize=(8, 8))
    P = g.values
    hull = ConvexHull(P)
    verts = list(hull.vertices) + [hull.vertices[0]]
    ax.plot(P[verts, 0], P[verts, 1], color=MUTED, lw=1)
    lim = np.abs(np.vstack([P, e.values])).max() * 1.15
    for a, b in zip(hull.vertices, np.roll(hull.vertices, -1)):
        p1, p2 = P[a], P[b]
        d = p2 - p1
        t = -p1 @ d / (d @ d)
        foot = p1 + t * d
        if np.linalg.norm(foot) > 1e-9:
            ray = foot / np.linalg.norm(foot) * lim * 1.5
            ax.plot([0, ray[0]], [0, ray[1]], ls="--", color=RULE, lw=1)
    ax.scatter(P[:, 0], P[:, 1], s=14, color=TEAL, alpha=0.6)
    for i in hull.vertices:
        n = g.index[i]
        ax.annotate(n.replace("Check-", "chk "), P[i], xytext=(4, 4), textcoords="offset points", fontsize=9,
                    fontweight="bold", color=RED if n in checks else INK)
    for n in checks:
        if n in g.index and g.index.get_loc(n) not in hull.vertices:
            ax.annotate(n.replace("Check-", "chk "), g.loc[n].values, xytext=(4, -10), textcoords="offset points", fontsize=8, color=RED)
    ax.scatter(e.PC1, e.PC2, marker="^", s=55, color=COPPER)
    for n, (x, y) in e.iterrows():
        ax.text(x, y + lim * 0.02, n, color=COPPER, fontsize=8, ha="center")
    ax.axhline(0, color=MUTED, lw=0.6); ax.axvline(0, color=MUTED, lw=0.6)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal")
    ax.set_xlabel(f"PC1 ({expl[0]:.1f}%)"); ax.set_ylabel(f"PC2 ({expl[1]:.1f}%)")
    ax.set_title("GGE 'which won where': the corner variety of each sector wins\nin the environments (triangles) inside that sector")
    _save(fig, path)


def fw_lines(GE, stab, entries, path):
    idx = GE.mean(0)
    xs = np.linspace(idx.min(), idx.max(), 10)
    fig, ax = plt.subplots(figsize=(7.5, 5))
    cols = [TEAL, COPPER, BLUE, GOLD, RED, MUTED, "#7a4fb5"]
    for c, n in zip(cols, entries):
        b, a = np.polyfit(idx.values, GE.loc[n].values, 1)
        ax.scatter(idx, GE.loc[n], s=12, color=c, alpha=0.6)
        ax.plot(xs, a + b * xs, color=c, lw=2, ls="--" if n.startswith("Check") else "-",
                label=f"{n.replace('Check-', 'check ')} (b = {b:.2f})")
    ax.plot(xs, xs, color=INK, lw=0.8, ls=":", label="average variety (b = 1)")
    ax.set_xlabel("Environment mean yield (t/ha): poor to good environments")
    ax.set_ylabel("Variety yield (t/ha)")
    ax.set_title("Finlay-Wilkinson: b > 1 needs good conditions, b < 1 holds up in poor ones")
    ax.legend(frameon=False, fontsize=8)
    _save(fig, path)


def decision(dec, checks, path):
    fig, ax = plt.subplots(figsize=(8.5, 6))
    sc = ax.scatter(dec.mean_t_ha, dec.wins_vs_check_pct, c=dec.maturity_days, cmap="viridis_r",
                    s=30 + 300 * (1 - dec.ASV.rank(pct=True)), alpha=0.8, edgecolor="white")
    cb = fig.colorbar(sc, ax=ax); cb.set_label("Days to maturity")
    bc = dec.loc[checks, "mean_t_ha"].max()
    ax.axvline(bc, color=RED, ls="--", lw=1); ax.axhline(50, color=MUTED, ls=":", lw=1)
    lab = list(dec.drop(checks, errors="ignore").sort_values("mean_t_ha", ascending=False).index[:6]) + checks
    offs = [(6, 4), (6, -12), (-34, 8), (-34, -12), (6, 12), (-30, 0), (6, 4), (6, 4)]
    for n, o in zip(lab, offs):
        ax.annotate(n.replace("Check-", "chk "), (dec.mean_t_ha[n], dec.wins_vs_check_pct[n]), xytext=o,
                    textcoords="offset points", fontsize=8.5, fontweight="bold", color=RED if n in checks else INK,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5))
    ax.text(bc, ax.get_ylim()[1], " best check", color=RED, fontsize=8, va="top")
    ax.set_xlabel("Mean yield over all environments (t/ha)")
    ax.set_ylabel("% of environments where it beat the best check")
    ax.set_title("Release candidates sit top-right (big dot = stable)")
    _save(fig, path)


def rank_heat(GE, entries, path):
    R = GE.rank(ascending=False).loc[list(entries)]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    im = ax.imshow(R.values, cmap="RdYlGn_r", vmin=1, vmax=len(GE), aspect="auto")
    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            ax.text(j, i, int(R.values[i, j]), ha="center", va="center", fontsize=7)
    ax.set_xticks(range(R.shape[1])); ax.set_xticklabels(R.columns, rotation=0, fontsize=8)
    ax.set_yticks(range(R.shape[0])); ax.set_yticklabels([n.replace("Check-", "chk ") for n in R.index], fontsize=8)
    ax.set_title(f"Rank (1 = best of {len(GE)}) of the leading entries in every environment")
    fig.colorbar(im, ax=ax, fraction=0.025)
    _save(fig, path)


# ---------------- livestock ----------------

def cbbp_factors(d, path):
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.6), sharey=True)
    for ax, f in zip(axes, ["village", "sex", "birth_type", "season"]):
        g = d.groupby(f).weight_6m_kg
        m, se = g.mean(), g.std() / np.sqrt(g.size())
        ax.bar(m.index.astype(str), m.values, yerr=1.96 * se.values, color=[TEAL, COPPER, BLUE][:len(m)], capsize=4)
        ax.set_title(f.replace("_", " ")); ax.set_ylim(0, m.max() * 1.25)
    axes[0].set_ylabel("Six-month weight (kg), mean ± 95% CI")
    fig.suptitle("Non-genetic effects: correct for these before ranking bucks", fontweight="bold", y=1.04)
    _save(fig, path)


def ebv_caterpillar(e, n_keep, path):
    e = e.sort_values("EBV_kg")
    fig, ax = plt.subplots(figsize=(7.5, 7))
    cols = [TEAL if i >= len(e) - n_keep else MUTED for i in range(len(e))]
    ax.errorbar(e.EBV_kg, range(len(e)), xerr=1.96 * e.SE_EBV, fmt="none", ecolor=RULE, lw=2)
    ax.scatter(e.EBV_kg, range(len(e)), c=cols, s=40, zorder=3)
    ax.set_yticks(range(len(e))); ax.set_yticklabels(e.index, fontsize=8)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_xlabel("Estimated breeding value for six-month weight (kg), ± 95% interval")
    ax.set_title(f"Rank the bucks: keep the top {n_keep} (teal) for breeding")
    _save(fig, path)


def gain_projection(gg, kids_per_year, price, path):
    yrs = np.arange(len(gg["cumulative"]))
    fig, ax = plt.subplots(figsize=(7.5, 4.3))
    ax.plot(yrs, gg["cumulative"], "-o", color=TEAL)
    ax.set_xlabel("Years of selection"); ax.set_ylabel("Extra six-month weight per kid (kg)")
    ax2 = ax.twinx()
    ax2.plot(yrs, np.array(gg["cumulative"]) * kids_per_year * price / 1000, alpha=0)
    ax2.set_ylabel(f"Extra value per year for {kids_per_year} kids sold (thousand birr)", color=COPPER)
    ax2.spines["right"].set_visible(True); ax2.tick_params(axis="y", colors=COPPER)
    ax.set_title(f"Genetic gain adds up: {gg['gain_per_year']:.2f} kg per kid per year, every year")
    _save(fig, path)


def reaction_norms(d, ebv, path):
    m = d.groupby(["sire", "village"]).weight_6m_kg.mean().unstack()
    top, bot = list(ebv.index[:3]), list(ebv.index[-3:])
    fig, ax = plt.subplots(figsize=(7, 4.5))
    vil = list(m.columns)
    for s in m.index:
        r = m.loc[s].dropna()
        c = TEAL if s in top else COPPER if s in bot else RULE
        ax.plot([vil.index(v) for v in r.index], r.values, "-o", color=c, lw=2 if c != RULE else 1, ms=4, alpha=1 if c != RULE else 0.8)
        if c != RULE:
            ax.text(vil.index(r.index[-1]) + 0.05, r.values[-1], s, color=c, fontsize=8, va="center")
    ax.set_xticks(range(len(vil))); ax.set_xticklabels(vil)
    ax.set_ylabel("Mean six-month weight of progeny (kg)")
    ax.set_title("Bucks in two villages: lines mostly parallel = little G x E")
    _save(fig, path)


def growth_curves(w, order, path):
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for c, t in zip([MUTED, BLUE, TEAL, COPPER], order):
        g = w[w.treatment == t].groupby("day").weight_kg
        m, se = g.mean(), g.std() / np.sqrt(g.size())
        ax.errorbar(m.index, m.values, yerr=se.values, fmt="-o", color=c, capsize=3, ms=4, label=t)
    ax.set_xlabel("Days on feed (after 15 days adaptation)"); ax.set_ylabel("Live weight (kg), mean ± SE")
    ax.set_title("Weighed every 15 days")
    ax.legend(frameon=False, fontsize=8)
    _save(fig, path)


def adg_bars(summ, hsd, path):
    fig, ax = plt.subplots(figsize=(7.5, 4.3))
    x = range(len(summ))
    ax.bar(x, summ.adg_g, color=[MUTED, BLUE, TEAL, COPPER][:len(summ)])
    for i, (m, l) in enumerate(zip(summ.adg_g, summ.tukey)):
        ax.text(i, m + 1.5, f"{m:.0f} g  {l}", ha="center", fontweight="bold")
    ax.set_xticks(list(x)); ax.set_xticklabels([t.split(":")[0] for t in summ.index])
    ax.set_ylabel("Average daily gain (g/day)")
    ax.set_title(f"Same letter = not different (Tukey, HSD = {hsd:.1f} g/day)")
    ax.set_ylim(0, summ.adg_g.max() * 1.2)
    _save(fig, path)


def budget_bars(pb, path):
    fig, ax = plt.subplots(figsize=(7.5, 4.3))
    x = np.arange(len(pb))
    ax.bar(x - 0.2, pb.feed_cost, 0.4, color=RULE, label="Supplement cost")
    ax.bar(x + 0.2, pb.net_return, 0.4, color=[RED if d else TEAL for d in pb.dominated], label="Net return")
    for i, (n, m) in enumerate(zip(pb.net_return, pb.MRR_pct)):
        ax.text(i + 0.2, n + 30, f"{n:,.0f}" + (f"\nMRR {m:.0f}%" if not np.isnan(m) else ""), ha="center", fontsize=8.5)
    ax.set_xticks(x); ax.set_xticklabels([t.split(":")[0] for t in pb.index])
    ax.set_ylabel("Birr per goat over the trial")
    ax.set_title("Partial budget: red = dominated (costs more, earns less)")
    ax.set_ylim(0, max(pb.net_return.max(), pb.feed_cost.max()) * 1.25)
    ax.legend(frameon=False)
    _save(fig, path)
