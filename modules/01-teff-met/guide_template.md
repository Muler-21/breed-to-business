# Module 1 · Testing 60 teff varieties across locations and years

**ሞጁል 1 · 60 የጤፍ ዝርያዎችን በተለያዩ ቦታዎችና ዓመታት መሞከር**

> **The business question.** A breeder (or a seed company) has 58 new teff lines and must decide which to release, and *where*. Farmers pay for seed that wins in *their* field, in good years and bad. This module takes you from an empty field to that decision: design, field layout, data recording, every ANOVA, the G × E analysis, and the charts a release committee asks for.

The data here are **simulated for teaching**, with realistic Ethiopian values: trial practice follows published national teff trials (2 m × 2 m plots, three replications, alpha-lattice blocks), and the national average farm yield of teff is about 1.9 t/ha. Replace the data with your own field books and run the same script.

---

## 1. The trial plan

| Item | Choice | Why |
|---|---|---|
| Entries | 58 candidate lines + 2 checks = 60 | Checks: **Quncho** (high-potential areas) and **Tsedey** (low-moisture areas), so every line is compared with what farmers already grow |
| Design | Alpha-lattice, 3 replicates, 10 incomplete blocks of 6 plots per replicate | 60 plots in one block would span very different soil; small blocks of 6 remove that soil trend. Every pair of varieties shares a block at most once (checked by the script) |
| Plot | 2 m × 2 m = 4 m², rows 20 cm apart; 1 m between plots, 1.5 m between blocks | Standard for national teff trials |
| Field size per site | {width} m × {length} m ≈ **{area} ha**, {plots} plots | Fits on one research-station field |
| Seed | 12 g per plot (30 kg/ha); **{seed_var} g per variety per site, {seed_site} kg per site** | Prepare and label seed packets before the season |
| Locations | Debre Zeit, Holetta, Adet, Debre Markos (high potential) and Alem Tena (low moisture) | Cover the target region, including the dry end |
| Years | 3 (2024–2026); the script handles 2 to 5 | Years differ in rainfall, which you cannot predict, so you need more than one |
| Randomisation | New for every site and every year | Field books are in [`fieldbooks/`](fieldbooks/) |
| Traits | Grain yield, days to maturity, plant height, lodging | Yield pays; maturity decides fit to the season |

### Field layout (one site, one year)

![Field layout](figures/01_field_layout.png)

**How to lay it out:** peg the 35.5 m × 51 m rectangle, mark the 15 plot rows (every 3.5 m), and in each row two blocks of six 2 m plots. Walk the plots in serpentine order: plot 101 is top-left, plot 112 top-right, plot 113 starts back on the right. Sow, label each plot with its plot number (not the variety name, so scorers are not biased), and keep the field book in a plastic sleeve.

### Recording yield

Harvest the whole 4 m² plot (or a fixed net area if borders were damaged), thresh, clean and weigh the grain in grams. Convert:

```
yield (t/ha) = grams per plot ÷ (plot area in m² × 100)    e.g. 1,000 g ÷ (4 × 100) = 2.5 t/ha
```

Record days to maturity when about 90% of the panicles are mature, and note anything unusual (hail, waterlogging, birds) in the notes column. The analysis can only fix what you wrote down.

---

## 2. Step 1: analyse each site and year separately

For each of the {n_env} environments the script fits **replicate + block within replicate + variety**, with variety tested *after* removing the block effects.

ANOVA for Debre Zeit 2024:

{site_anova}

Quality check for every environment:

{site_summary}

**What to look at**

* **CV%** (coefficient of variation) should be below about 15–20%. Alem Tena, the dry site, is the noisiest, as dry sites usually are.
* **Efficiency vs RCBD** above 100% means the small blocks paid off: the same data analysed as an ordinary randomised complete block design would have had a larger error.
* **Heritability (H²)** shows how well one site ranks the varieties. One site alone is never enough.

## 3. Step 2: combined analysis over locations and years

Locations and years are treated as **random**: they stand for the farms and the future seasons where the variety will be grown. So the variety effect is tested against the interactions, not only against plot error.

{combined_anova}

**What it means**

* The environment (location and year) causes most of the variation. That is normal and is not what you select on.
* **G × L ({gl_pct}% of SS) is much larger than G × Y ({gy_pct}%).** Variety ranking changes between *locations* in a repeatable way, but changes little between years. Repeatable differences can be used: recommend varieties for groups of locations, not for the whole country.
* Variance components (plot basis): genotype {vc_g}, G × L {vc_gl}, G × Y {vc_gy}, G × L × Y {vc_gly}, error {vc_e}.

## 4. Step 3: how many locations and years do you need?

![Heritability planning](figures/04_heritability_planning.png)

With 5 locations, one year gives a heritability of **{h2_5x1}**, three years **{h2_5x3}**. Because G × L is large, adding locations helps more than adding years. Reaching 0.80 for the whole region needs about 8–10 locations; testing *within* each mega-environment (Step 4) is the cheaper way.

## 5. Step 4: AMMI and GGE: who wins where?

![Environment means](figures/02_environment_means.png)

![Sources of variation](figures/03_variance_sources.png)

{ammi_table}

![AMMI1 biplot](figures/05_ammi1_biplot.png)

![GGE which-won-where](figures/06_gge_which_won_where.png)

The GGE biplot (PC1 {pc1}% + PC2 {pc2}% of variety + G × E variation) splits the environments into sectors. The variety at the corner of a sector wins there:

* **Low-moisture mega-environment ({tf48_envs}): TF48 wins.** Over the three Alem Tena seasons it averaged {tf48_at} t/ha against {tsedey_at} t/ha for the drought check Tsedey and {quncho_at} t/ha for Quncho.
* **High-potential mega-environment (Debre Zeit, Adet, Debre Markos, Holetta): TF47 and TF50 win.** TF47 averaged {tf47_hp} t/ha against {quncho_hp} t/ha for Quncho, and it matures about {tf47_earlier} days earlier.

## 6. Step 5: stability

![Finlay-Wilkinson](figures/07_finlay_wilkinson.png)

A slope **b near 1** means the variety follows the environment like an average variety; **b > 1** means it needs good conditions to shine; **b < 1** means it holds up in poor conditions but cannot use good ones. The drought check Tsedey (b ≈ {tsedey_b}) is the classic "safe but low ceiling" type.

## 7. Step 6: the decision

![Decision map](figures/08_decision_map.png)

![Rank heat map](figures/09_rank_heatmap.png)

Top entries by the yield–stability index (rank of mean yield + rank of AMMI stability value, smaller is better):

{decision_table}

### Recommendation

1. **Advance TF47 and TF50 to variety verification trials in high-potential areas.** TF47 beats Quncho in {tf47_wins}% of environments and matures earlier, which also helps farmers escape end-of-season drought.
2. **Advance TF48 for low-moisture areas** such as the Alem Tena corridor. It is not the best nationally, but it is the best where farmers have the fewest options.
3. **Keep TF45** as the most *widely* stable line (top of the yield–stability index) for farmers who cannot choose by location.
4. Drop the lines that never beat the checks: they cost land and labour every season.

**Value to a farmer** (example price {price} birr/kg): every extra 0.1 t/ha is worth **{per_01} birr per hectare** per season. TF48 in the dry area gives about {tf48_gain_t} t/ha more than Quncho, about **{tf48_gain_birr} birr/ha**.

---

## 8. From variety to business

A released variety is only valuable when farmers can buy clean seed of it.

* **Seed multiplication arithmetic:** a 1 ha seed field yielding 2.5 t of clean seed sows about **140 ha** at 18 kg/ha (the upper end of the 15–18 kg/ha recommended for row planting), or 83 ha at 30 kg/ha broadcast.
* **Business models:** a youth seed-producer cooperative licensed to multiply the variety; a seed-cleaning and packing service; contract growing for a processor that wants one grain colour.
* **What to measure next:** farmer-preferred traits (grain colour, *injera* quality, straw for cattle) through participatory variety selection in the target mega-environment.

## 9. Run it yourself

```bash
pip install numpy pandas scipy matplotlib
python run.py                 # design, field books, analysis and all figures
```

* **Your own data:** collect the 15 field books into one CSV with the same columns as `data/teff_met_simulated.csv` and set `DATA_FILE` at the top of `run.py`.
* **Another crop or size:** change `N_TEST`, `CHECKS`, `BLOCK_SIZE`, `REPS`, `LOCATIONS` and `YEARS`. Block size must not exceed the number of blocks per replicate (e.g. 100 entries: blocks of 10; 36 entries: blocks of 6).
* **R users:** [`R/teff_met.R`](R/teff_met.R) does the same analysis with agricolae, lme4 and metan.

Outputs: [`tables/`](tables/) (every ANOVA, means, decision table) and [`figures/`](figures/).

---

## በአማርኛ አጭር ማጠቃለያ

* **ጥያቄው፦** ከ58 አዳዲስ የጤፍ መስመሮች የትኛው ይለቀቅ፣ የትስ?
* **ዲዛይኑ፦** አልፋ-ላቲስ፣ 3 ድግግሞሽ፣ በእያንዳንዱ ድግግሞሽ 6 ማሳ ያላቸው 10 ብሎኮች፤ 2 ሜ × 2 ሜ ማሳ፤ 5 ቦታዎች × 3 ዓመታት፤ በየዓመቱ አዲስ የዕጣ ድልድል።
* **ውጤቱ፦** አካባቢ ትልቁን ልዩነት ያመጣል፤ የዝርያ × የቦታ መስተጋብር ከዝርያ × የዓመት መስተጋብር ይበልጣል፤ ስለዚህ ዝርያዎችን በአካባቢ ቡድን መምከር ይገባል።
* **ውሳኔው፦** TF47 እና TF50 ለከፍተኛ አቅም ቦታዎች (TF47 ከኩንቾ 11 ቀን ገደማ ቀድሞ ይደርሳል)፤ TF48 ለዝቅተኛ እርጥበት ቦታዎች (አለም ጤና)፤ TF45 በሰፊው የተረጋጋ።
* **ንግዱ፦** 1 ሄክታር የዘር ማሳ በመስመር ተዘርቶ 140 ሄክታር ገደማ ለመዝራት በቂ ዘር ይሰጣል፤ ወጣቶች ዘር አባዢ ማኅበር ሊያቋቁሙ ይችላሉ።

*Data in this module are simulated for teaching. Trial practice follows published Ethiopian teff trials:*
*[Worede 2020, BSJ Agri](https://dergipark.org.tr/en/download/article-file/882832) (2 m × 2 m plots, AMMI/GGE) ·
[Jifar et al. 2019, J. Exp. Agric. Int.](https://boris.unibe.ch/130598) (35 varieties, nine environments) ·
[Kulle variety release, Ethiop. J. Agric. Sci.](https://ajol.info/index.php/ejas/article/view/271201/255992) (drilled rows 0.2 m, SS shares) ·
[70 tef genotypes in a 7 × 10 alpha-lattice, Hawassa Univ. journal](https://journals.hu.edu.et/hu-journals/index.php/agvs/article/download/90/52/292) (Quncho and Tsedey checks) ·
[Northeast Ethiopia tef G × E, Cogent Food & Agric.](https://informahealthcare.com/doi/abs/10.1080/23311932.2020.1847760) (30 kg/ha, 12 g per plot) ·
[national tef yield 1.91 t/ha, 2021–22](https://tas.scione.com/cms/fulltext.php?id=380) ·
[seed rate 15–18 kg/ha for row planting](https://ejol.aau.edu.et/index.php/EJDR/article/download/10270/8212/19204).*
