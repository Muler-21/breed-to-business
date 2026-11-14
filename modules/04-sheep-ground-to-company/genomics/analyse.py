"""Real genomic analysis of Ethiopian sheep from public SNP data.

Data: Da Silva et al. (2024, Animal Genetics) public PLINK set, 2,818 sheep x 28,210 SNPs,
CC BY 4.0, figshare doi 10.6084/m9.figshare.26731378.v2. It holds 18 Ethiopian populations
(genotyped originally by Edea et al. 2017 and Ahbara et al. 2019, among others) and
reference breeds from Sudan, Kenya, southern Africa and the Middle East.

Get the data (either):
  git fetch https://github.com/Muler-21/breed-to-business.git data-sheep && git worktree add ../sheepdata FETCH_HEAD
  or download the three figshare files OaSNP2818x28210.{bed,bim,fam}
Run:
  python modules/04-sheep-ground-to-company/genomics/analyse.py /path/to/OaSNP2818x28210

Pure numpy/pandas/scipy/matplotlib: no PLINK needed. Same steps in PLINK are in plink_steps.sh.
Outputs go to genomics/results/ and genomics/figures/.
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
from b2b.plots import plt, _save, INK, MUTED, RULE, COPPER, TEAL, GOLD, BLUE, RED

PREFIX = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(ROOT), "sheepdata", "OaSNP2818x28210")
RES, FIG = os.path.join(HERE, "results"), os.path.join(HERE, "figures")
os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)

ETH = ["Menz", "EthiopianMenz", "Wollo", "Farta", "Washera", "Adile", "ArsiBale", "Horro", "Bonga", "Doyogena",
       "BlHeadedSomali", "Adane", "Arabo", "Kefis", "Gesses", "Kido", "Loya", "ShubiGemo"]
REF = ["Hammari", "Kabashi", "RedMaasai", "Dorper", "LocalAwassi", "Djallonke", "Damara", "EgyptianBarki"]
NAME = {"EthiopianMenz": "Menz (600K set)", "Adile": "Adilo", "ArsiBale": "Arsi-Bale", "BlHeadedSomali": "Blackhead Somali",
        "ShubiGemo": "Shubi Gemo", "LocalAwassi": "Awassi", "RedMaasai": "Red Maasai", "EgyptianBarki": "Barki (Egypt)",
        "Hammari": "Hammari (Sudan)", "Kabashi": "Kabashi (Sudan)", "Damara": "Damara (Namibia)", "Djallonke": "Djallonke (W. Africa)"}
# tail-type groups follow catalogue/livestock_breeds.csv (DAGRIS; Gizaw et al.). Unlisted Ethiopian populations: "other"
GROUP = {**{p: "Short fat-tailed (sub-alpine)" for p in ["Menz", "EthiopianMenz", "Wollo", "Farta", "Washera"]},
         **{p: "Long fat-tailed (highland)" for p in ["Adile", "ArsiBale", "Horro", "Bonga", "Doyogena"]},
         "BlHeadedSomali": "Fat-rumped (lowland)",
         **{p: "Other Ethiopian (Ahbara et al. 2019 sampling)" for p in ["Adane", "Arabo", "Kefis", "Gesses", "Kido", "Loya", "ShubiGemo"]},
         **{p: "Reference breed (outside Ethiopia)" for p in REF}}
GCOL = {"Short fat-tailed (sub-alpine)": BLUE, "Long fat-tailed (highland)": TEAL, "Fat-rumped (lowland)": COPPER,
        "Other Ethiopian (Ahbara et al. 2019 sampling)": GOLD, "Reference breed (outside Ethiopia)": MUTED}
nm = lambda p: NAME.get(p, p)


def read_plink(prefix, keep_pops):
    fam = pd.read_csv(prefix + ".fam", sep=r"\s+", header=None, names=["pop", "iid", "pat", "mat", "sex", "phe"])
    bim = pd.read_csv(prefix + ".bim", sep="\t", header=None, names=["chr", "snp", "cm", "bp", "a1", "a2"])
    n, m = len(fam), len(bim)
    raw = np.fromfile(prefix + ".bed", dtype=np.uint8)
    assert raw[0] == 0x6C and raw[1] == 0x1B and raw[2] == 1, "need SNP-major .bed"
    nb = (n + 3) // 4
    byts = raw[3:].reshape(m, nb)
    keep = np.where(fam["pop"].isin(keep_pops))[0]
    # decode 2-bit codes: 00 hom A1 (2 copies of a1), 01 missing, 10 het, 11 hom A2
    lut = np.array([2, -1, 1, 0], dtype=np.int8)
    g = np.empty((m, n), dtype=np.int8)
    for k in range(4):
        cols = np.arange(k, n, 4)
        g[:, cols] = lut[(byts[:, : len(cols)] >> (2 * k)) & 3]
    return fam.iloc[keep].reset_index(drop=True), bim, g[:, keep].T.copy()   # individuals x SNPs, a1 dosage, -1 missing


fam, bim, G = read_plink(PREFIX, ETH + REF)
log = {"animals_loaded": int(len(fam)), "snps_loaded": int(G.shape[1])}

# ------------------------------------------------------------------ QC (as PLINK --geno 0.05 --mind 0.10 --maf 0.01)
miss = G < 0
snp_call = 1 - miss.mean(0)
ok_snp = snp_call >= 0.95
ind_call = 1 - miss[:, ok_snp].mean(1)
ok_ind = ind_call >= 0.90
G, fam = G[ok_ind][:, ok_snp], fam[ok_ind].reset_index(drop=True)
bim = bim[ok_snp].reset_index(drop=True)
Gf = np.where(G < 0, np.nan, G).astype(float)
p = np.nanmean(Gf, 0) / 2
maf = np.minimum(p, 1 - p)
ok = maf >= 0.01
G, Gf, p, bim = G[:, ok], Gf[:, ok], p[ok], bim[ok].reset_index(drop=True)
log.update(animals_after_qc=int(len(fam)), snps_after_qc=int(G.shape[1]),
           ethiopian_animals=int(fam["pop"].isin(ETH).sum()), ethiopian_pops=len(ETH))

# ------------------------------------------------------------------ diversity per population
rows = []
for pop, idx in fam.groupby("pop").groups.items():
    X = Gf[idx]
    n_i = np.sum(~np.isnan(X), 0)
    pp = np.nansum(X, 0) / (2 * np.maximum(n_i, 1))
    ho = np.nanmean(X == 1, 0)
    he = 2 * pp * (1 - pp) * (2 * n_i / np.maximum(2 * n_i - 1, 1))      # unbiased He
    poly = np.mean((pp > 0) & (pp < 1))
    Ho, He = np.nanmean(ho), np.nanmean(he)
    rows.append((nm(pop), GROUP[pop], len(idx), Ho, He, 1 - Ho / He, poly))
div = pd.DataFrame(rows, columns=["Population", "Group", "n", "Ho", "He", "F (1-Ho/He)", "Polymorphic SNPs"])
div["eth"] = div.Population.isin([nm(x) for x in ETH])
div = div.sort_values(["eth", "Group", "He"], ascending=[False, True, False]).drop(columns="eth")
div.round(4).to_csv(os.path.join(RES, "diversity_by_population.csv"), index=False)

# ------------------------------------------------------------------ PCA (standardised genotypes, mean-imputed)
Z = (np.where(np.isnan(Gf), 2 * p, Gf) - 2 * p) / np.sqrt(2 * p * (1 - p))
U, S, Vt = np.linalg.svd(Z - Z.mean(0), full_matrices=False)
ve = S ** 2 / np.sum(S ** 2)
pcs = pd.DataFrame(U[:, :4] * S[:4], columns=["PC1", "PC2", "PC3", "PC4"])
pcs["pop"] = fam["pop"].values
pcs.round(4).to_csv(os.path.join(RES, "pca_all.csv"), index=False)
# Ethiopian-only PCA
e = fam["pop"].isin(ETH).values
Ze = Z[e]; Ue, Se, _ = np.linalg.svd(Ze - Ze.mean(0), full_matrices=False)
vee = Se ** 2 / np.sum(Se ** 2)
pce = pd.DataFrame(Ue[:, :3] * Se[:3], columns=["PC1", "PC2", "PC3"]); pce["pop"] = fam["pop"].values[e]


def pca_plot(df, v, fn, title, label_pops):
    fig, ax = plt.subplots(figsize=(9.5, 7))
    for pop, d in df.groupby("pop"):
        c = GCOL[GROUP[pop]]
        ax.scatter(d.PC1, d.PC2, s=18, color=c, alpha=0.75, edgecolor="white", lw=0.3)
        if pop in label_pops:
            ax.text(d.PC1.mean(), d.PC2.mean(), nm(pop), fontsize=8.5, color=INK, ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=c, lw=0.8, alpha=0.85))
    for g, c in GCOL.items():
        if any(GROUP[x] == g for x in df["pop"].unique()):
            ax.scatter([], [], color=c, s=30, label=g)
    ax.set_xlabel(f"PC1 ({100 * v[0]:.1f} % of variance)"); ax.set_ylabel(f"PC2 ({100 * v[1]:.1f} %)")
    ax.legend(frameon=False, fontsize=8.5, loc="best"); ax.set_title(title, loc="left")
    _save(fig, os.path.join(FIG, fn))


pca_plot(pcs, ve, "01_pca_ethiopia_and_reference.png", "Ethiopian sheep among African and Middle Eastern breeds (PCA, 28K SNPs)",
         set(REF) | {"Menz", "Washera", "Bonga", "Horro", "Kefis", "Adane", "BlHeadedSomali"})
pca_plot(pce, vee, "02_pca_ethiopia_only.png", "Within Ethiopia: genetic structure of 18 populations (PCA)", set(ETH))

# ------------------------------------------------------------------ pairwise FST (Hudson, ratio of averages) among Ethiopian pops
freq, nn = {}, {}
for pop in ETH:
    X = Gf[(fam["pop"] == pop).values]
    c = np.sum(~np.isnan(X), 0)
    freq[pop], nn[pop] = np.nansum(X, 0) / (2 * np.maximum(c, 1)), 2 * c


def hudson(a, b):
    p1, p2, n1, n2 = freq[a], freq[b], nn[a], nn[b]
    ok_ = (n1 > 1) & (n2 > 1)
    num = (p1 - p2) ** 2 - p1 * (1 - p1) / (n1 - 1) - p2 * (1 - p2) / (n2 - 1)
    den = p1 * (1 - p2) + p2 * (1 - p1)
    return np.sum(num[ok_]) / np.sum(den[ok_])


F = pd.DataFrame(0.0, index=[nm(x) for x in ETH], columns=[nm(x) for x in ETH])
for i, a in enumerate(ETH):
    for b in ETH[i + 1:]:
        F.loc[nm(a), nm(b)] = F.loc[nm(b), nm(a)] = hudson(a, b)
F.round(4).to_csv(os.path.join(RES, "fst_ethiopian_pairwise.csv"))
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
from scipy.spatial.distance import squareform
L = linkage(squareform(np.clip(F.values, 0, None), checks=False), "average")
order = leaves_list(L)[::-1]          # dendrogram (orientation left) draws leaf 0 at the bottom
Fo = F.iloc[order, order]
fig, (a0, a1) = plt.subplots(1, 2, figsize=(13, 7), gridspec_kw={"width_ratios": [1, 3.2], "wspace": 0.02})
dendrogram(L, orientation="left", ax=a0, no_labels=True, color_threshold=0, above_threshold_color=MUTED)
a0.set_xlabel("FST (UPGMA)"); a0.set_yticks([]); a0.spines["left"].set_visible(False)
im = a1.imshow(Fo.values, cmap="YlOrBr", vmin=0, aspect="auto")
a1.set_xticks(range(len(Fo))); a1.set_xticklabels(Fo.columns, rotation=60, ha="right", fontsize=8.5)
a1.yaxis.tick_right(); a1.set_yticks(range(len(Fo))); a1.set_yticklabels(Fo.index, fontsize=8.5)
for i in range(len(Fo)):
    for j in range(len(Fo)):
        if i != j:
            a1.text(j, i, f"{Fo.values[i, j]:.2f}"[1:], ha="center", va="center", fontsize=6.5,
                    color="white" if Fo.values[i, j] > 0.07 else INK)
fig.colorbar(im, ax=a1, shrink=0.6, label="FST", pad=0.2)
a0.set_title("How different are Ethiopian sheep populations? Pairwise FST, clustered", loc="left")
_save(fig, os.path.join(FIG, "03_fst_heatmap.png"))

# ------------------------------------------------------------------ runs of homozygosity (>= 4 Mb, >= 25 SNPs, 1 het allowed)
MIN_MB, MIN_SNP, MAX_HET = 4.0, 25, 1
chrom, pos = bim["chr"].values, bim["bp"].values
auto_len = bim.groupby("chr")["bp"].agg(lambda x: x.max() - x.min()).sum()
froh = np.zeros(len(fam))
for c in np.unique(chrom):
    idx = np.where(chrom == c)[0]
    pc = pos[idx]
    H = (G[:, idx] == 1)
    M = G[:, idx] < 0
    for a in range(len(fam)):
        het, miss_ = H[a], M[a]
        start, nhet, tot = 0, 0, 0
        segs = []
        for k in range(len(idx)):
            if het[k]:
                nhet += 1
                if nhet > MAX_HET:
                    segs.append((start, k - 1)); start, nhet = k + 1, 0
        segs.append((start, len(idx) - 1))
        for s0, s1 in segs:
            if s1 - s0 + 1 >= MIN_SNP and (pc[s1] - pc[s0]) / 1e6 >= MIN_MB:
                tot += pc[s1] - pc[s0]
        froh[a] += tot
froh = froh / auto_len
fam["F_ROH"] = froh
roh = fam.groupby("pop")["F_ROH"].agg(["mean", "max", "count"]).reset_index()
roh["Population"] = roh["pop"].map(nm); roh["Group"] = roh["pop"].map(GROUP)
roh = roh[roh["pop"].isin(ETH)].sort_values("mean", ascending=False)
roh[["Population", "Group", "count", "mean", "max"]].rename(columns={"count": "n", "mean": "Mean F_ROH", "max": "Max F_ROH"}).round(4) \
    .to_csv(os.path.join(RES, "froh_ethiopian.csv"), index=False)
fig, ax = plt.subplots(figsize=(10, 4.6))
dd = fam[fam["pop"].isin(ETH)].copy(); dd["P"] = dd["pop"].map(nm)
ordp = roh["Population"].tolist()
for k, pn in enumerate(ordp):
    v = dd.loc[dd.P == pn, "F_ROH"].values
    c = GCOL[GROUP[roh.loc[roh.Population == pn, "pop"].iloc[0]]]
    ax.scatter(np.full(len(v), k) + np.random.default_rng(k).uniform(-0.2, 0.2, len(v)), v, s=14, color=c, alpha=0.7)
    ax.plot([k - 0.3, k + 0.3], [v.mean()] * 2, color=INK, lw=2)
ax.set_xticks(range(len(ordp))); ax.set_xticklabels(ordp, rotation=55, ha="right", fontsize=8.5)
ax.set_ylabel("F_ROH (share of genome in ROH ≥ 4 Mb)")
ax.set_title("Inbreeding from runs of homozygosity, per animal (bar = population mean)", loc="left")
_save(fig, os.path.join(FIG, "04_froh.png"))

# ------------------------------------------------------------------ selection scan: short fat-tailed vs long fat-tailed (FST in 2 Mb windows)
A = ["Menz", "EthiopianMenz", "Wollo", "Farta", "Washera"]
B = ["Adile", "ArsiBale", "Horro", "Bonga", "Doyogena"]
def grp_freq(pops):
    X = Gf[fam["pop"].isin(pops).values]
    c = np.sum(~np.isnan(X), 0)
    return np.nansum(X, 0) / (2 * np.maximum(c, 1)), 2 * c
p1, n1 = grp_freq(A); p2, n2 = grp_freq(B)
num = (p1 - p2) ** 2 - p1 * (1 - p1) / (n1 - 1) - p2 * (1 - p2) / (n2 - 1)
den = p1 * (1 - p2) + p2 * (1 - p1)
snp = bim[["chr", "snp", "bp"]].copy(); snp["num"], snp["den"] = num, den
snp["fst"] = np.where(den > 0, num / den, 0)
WIN, STEP = 2_000_000, 1_000_000
w = []
for c, d in snp.groupby("chr"):
    for s in range(0, int(d.bp.max()) + 1, STEP):
        q = d[(d.bp >= s) & (d.bp < s + WIN)]
        if len(q) >= 8:
            w.append((c, s, s + WIN, len(q), q.num.sum() / q.den.sum()))
W = pd.DataFrame(w, columns=["chr", "start", "end", "snps", "fst"])
W["z"] = (W.fst - W.fst.mean()) / W.fst.std()
thr = W.fst.quantile(0.995)
top = W[W.fst >= thr].sort_values("fst", ascending=False)
# merge overlapping top windows
merged = []
for c, d in top.sort_values(["chr", "start"]).groupby("chr"):
    cur = None
    for _, r in d.iterrows():
        if cur and r.start <= cur[2]:
            cur = (c, cur[1], max(cur[2], r.end), max(cur[3], r.fst))
        else:
            if cur: merged.append(cur)
            cur = (c, r.start, r.end, r.fst)
    merged.append(cur)
TOP = pd.DataFrame(merged, columns=["chr", "start_bp", "end_bp", "max_window_fst"]).sort_values("max_window_fst", ascending=False)
TOP.round(4).to_csv(os.path.join(RES, "selection_scan_top_regions.csv"), index=False)
W.round(5).to_csv(os.path.join(RES, "selection_scan_windows.csv"), index=False)
fig, ax = plt.subplots(figsize=(12, 4.2))
off, ticks = 0, []
for c, d in W.groupby("chr"):
    ax.scatter(off + (d.start + d.end) / 2, d.fst, s=6, color=BLUE if c % 2 else MUTED)
    ticks.append(off + d.end.max() / 2); off += d.end.max()
ax.axhline(thr, color=RED, lw=1, ls="--"); ax.text(off, thr, " top 0.5 %", color=RED, va="bottom", ha="right", fontsize=8.5)
ax.set_xticks(ticks); ax.set_xticklabels(sorted(W.chr.unique()), fontsize=7.5)
ax.set_xlabel("Chromosome"); ax.set_ylabel("Window FST")
ax.set_title("Genome scan: short fat-tailed vs long fat-tailed Ethiopian sheep (2 Mb windows)", loc="left")
_save(fig, os.path.join(FIG, "05_selection_scan.png"))

# ------------------------------------------------------------------ genomic relationships inside a breed (what a CBBP would use)
def grm(X, pp):
    Zc = np.where(np.isnan(X), 2 * pp, X) - 2 * pp
    return Zc @ Zc.T / (2 * np.sum(pp * (1 - pp)))
rel = []
for pop in ["Menz", "Horro", "Bonga", "Washera", "Doyogena"]:
    X = Gf[(fam["pop"] == pop).values]
    pb = np.nanmean(X, 0) / 2            # base = this breed's own allele frequencies
    keep_ = (pb > 0.01) & (pb < 0.99)
    Gm = grm(X[:, keep_], pb[keep_])
    off_ = Gm[np.triu_indices(len(Gm), 1)]
    rel.append((nm(pop), len(Gm), np.mean(np.diag(Gm) - 1), np.mean(off_), int(np.sum(off_ > 0.20))))
REL = pd.DataFrame(rel, columns=["Breed", "n", "Mean genomic F (GRM diag - 1)", "Mean relationship", "Pairs related at half-sib level or closer (>0.20)"])
REL.round(4).to_csv(os.path.join(RES, "genomic_relationships.csv"), index=False)

eth_div = div[div.Group != "Reference breed (outside Ethiopia)"]
log.update(
    pc1_all=float(ve[0]), pc2_all=float(ve[1]), pc1_eth=float(vee[0]), pc2_eth=float(vee[1]),
    he_min=[eth_div.iloc[eth_div.He.argmin()].Population, float(eth_div.He.min())],
    he_max=[eth_div.iloc[eth_div.He.argmax()].Population, float(eth_div.He.max())],
    fst_eth_min=float(F.values[np.triu_indices(len(F), 1)].min()), fst_eth_max=float(F.values[np.triu_indices(len(F), 1)].max()),
    fst_eth_mean=float(F.values[np.triu_indices(len(F), 1)].mean()),
    fst_max_pair=list(F.stack().idxmax()), fst_sft_lft_genome=float(np.sum(num) / np.sum(den)),
    froh_highest=[roh.iloc[0].Population, float(roh.iloc[0]["mean"])], froh_lowest=[roh.iloc[-1].Population, float(roh.iloc[-1]["mean"])],
    top_regions=int(len(TOP)), scan_threshold=float(thr),
)
json.dump(log, open(os.path.join(RES, "summary.json"), "w"), indent=1, default=str)
print(json.dumps(log, indent=1, default=str))
print(div.round(3).to_string(index=False)); print(roh.round(3).to_string(index=False)); print(TOP.head(12).to_string(index=False)); print(REL.round(3))
