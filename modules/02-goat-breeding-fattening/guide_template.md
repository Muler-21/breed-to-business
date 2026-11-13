# Module 2 · Goats: breed better bucks, fatten for profit

**ሞጁል 2 · ፍየሎች፦ የተሻሉ አውራ ፍየሎችን ማዳቀልና ለትርፍ ማደለብ**

> **The business questions.** (A) A goat breeders' cooperative must decide *which bucks to keep* each season so that every new generation of kids grows faster. (B) A young entrepreneur buying yearling goats to fatten must decide *which ration earns the most money*, not just which one grows goats fastest. This module answers both with real designs, every ANOVA, and the charts you need to decide.

Both datasets are **simulated for teaching** from published Ethiopian values: community-based breeding programmes (CBBPs) for Abergelle, Central Highland and Woyto-Guji goats, and on-farm fattening trials of castrated yearling goats fed cowpea hay and concentrate. Replace them with your own records and run the same script.

---

## Part A · Community-based breeding

### A1. The design: what to record, and how

Ethiopia's CBBPs keep goats in farmers' flocks. Trained enumerators record every kid, and the community selects bucks together. One season of records from 24 bucks rotated between three villages gave **{n_kids} kids** in this example.

| Record | When | Why |
|---|---|---|
| Kid ID, dam ID, sire (buck), village, household | at birth | pedigree: without the sire, no breeding value |
| Sex, birth type (single/twin), dam parity, birth date | at birth | non-genetic effects to correct for |
| Weight at 3 and 6 months | ± 7 days of the target age | six-month weight is the main selection trait for body size |
| Deaths, sales, notes | when they happen | survival and data cleaning |

Studies of Ethiopian CBBPs found that birth weight adds little for genetic improvement and is hard to record accurately in villages, so recording can focus on 3- and 6-month weights. A blank sheet is in [`fieldbooks/cbbp_recording_sheet.csv`](fieldbooks/cbbp_recording_sheet.csv).

**Rotate bucks between villages.** It limits inbreeding and, as a bonus, it lets you test whether a good buck is good everywhere (A4).

### A2. Correct for the environment, then estimate heritability

![Non-genetic effects](figures/01_non_genetic_effects.png)

Least-squares ANOVA, with the buck (sire) entered **after** all fixed effects so it is compared fairly:

{sire_anova}

From the sire mean square: σ²(sire) = {var_s}, σ²(error) = {var_e}, so

```
h² = 4 σ²(sire) / (σ²(sire) + σ²(error)) = {h2} ± {se_h2}
```

That is within the 0.15–0.40 range reported for weights in the Abergelle CBBP. It is high enough for selection to work.

### A3. Rank the bucks (BLUP breeding values)

![Buck breeding values](figures/02_buck_breeding_values.png)

The script solves Henderson's mixed-model equations: fixed effects for village, year, season, sex, birth type and parity, and a random effect for the buck. Bucks with few kids are pulled towards zero, so luck is not mistaken for genetics.

{ebv_table}

**Decision: keep the top 6 bucks for the next season,** retire the bottom ones from breeding, and sell them for meat. With about 27 kids per buck the accuracy is around {acc}; in this simulation the estimated values correlate {corr} with the true ones.

### A4. Is a good buck good in every village? (G × E for animals)

![Buck by village](figures/03_buck_by_village.png)

{sv_anova}

Buck × village is **not significant (p = {sv_p})**. The ranking of bucks holds across villages, so one joint evaluation and one buck exchange plan serve all three villages. If it were significant, you would rank bucks separately for each agro-ecology, exactly like the teff varieties in Module 1.

### A5. What selection is worth

![Genetic gain](figures/04_genetic_gain.png)

If the best {kept}% of young bucks are kept on their own six-month weight and does are not selected:

```
gain per year = i × √h² × σa ÷ (L_male + L_female) = {i_m} × {sqrt_h2} × {sd_a} ÷ (2.5 + 3.5) = {gain} kg
```

That is in line with the 0.17–0.25 kg per year predicted for the Abergelle CBBP. It is small in one year, but it **accumulates and is permanent**: after 10 years every kid is about {gain10} kg heavier at six months. For a cooperative selling {kids} kids a year at {price} birr/kg, that is about **{value10} birr more per year** by year 10, for the cost of recording and a few good bucks.

---

## Part B · Fattening trial: which ration pays?

### B1. The design

| Item | Choice | Why |
|---|---|---|
| Animals | 36 castrated yearling goats, about 28 kg | the class traders buy for fattening |
| Rations | T1 browsing only (control) · T2 + cowpea hay 400 g/day · T3 + 300 g concentrate + 100 g cowpea hay · T4 + concentrate 400 g/day | from home-grown forage to fully bought feed |
| Design | Randomised complete blocks: the 36 goats are sorted by starting weight into 9 blocks of 4, and each block gets all 4 rations at random | heavier goats gain differently; blocking removes that |
| Duration | 15 days adaptation + 90 days, weighed every 15 days in the morning before feeding | standard for Ethiopian fattening trials |
| Records | weights, feed offered and refused, health, prices paid and received | the partial budget needs the money too |

Allocation sheet: [`fieldbooks/fattening_allocation.csv`](fieldbooks/fattening_allocation.csv).

### B2. Growth and ANOVA

![Growth curves](figures/05_growth_curves.png)

RCBD ANOVA for average daily gain:

{rcbd}

ANCOVA with starting weight as a covariate:

{ancova}

The covariate adds nothing here (p = {cov_p}) because **blocking by starting weight already did its job**. That is why you block.

![Daily gain](figures/06_daily_gain.png)

{fat_means}

### B3. The money: partial budget

Only costs and returns that differ between rations are counted (CIMMYT partial-budget method). Example prices: buy {buy} birr/kg live, sell {sell} birr/kg, concentrate {conc} birr/kg, cowpea hay {hay} birr/kg.

![Partial budget](figures/07_partial_budget.png)

{budget}

**Decision:** at these prices **T2 (cowpea hay) earns the most per goat**. The concentrate rations grow goats faster but cost more than the extra weight is worth, so they are *dominated*. The marginal rate of return (MRR) of moving from T1 to T2 is {mrr}%.

**The number that changes the decision:** T4 beats T2 only if concentrate costs less than **{be_conc} birr/kg**. Check the price before you buy feed; this one line of arithmetic decides the business.

### B4. From trial to business

* **Batch plan:** 20 goats per 105-day batch, 3 batches a year. At T2 that is about {annual} birr net a year before labour and housing, and it needs about 2.2 t of cowpea hay a year (20 goats × 0.4 kg × 90 days × 3 batches).
* **Grow the feed:** under-sowing cowpea is one way to produce hay on the farm, and it turns a bought input into your own margin.
* **Sell at the right time:** holidays raise goat prices. Plan the batch so day 90 falls before them.
* **Join the CBBP:** buy yearlings from improved bucks (Part A) and the fattening gain starts from a heavier, faster-growing animal.

---

## Run it yourself

```bash
pip install numpy pandas scipy matplotlib
python run.py
```

Change the prices, rations and genetic parameters at the top of `run.py`. To use your own records, keep the column names of the CSV files in `data/` and replace the simulation lines with `pd.read_csv(...)`.

---

## በአማርኛ አጭር ማጠቃለያ

* **ማዳቀል፦** ከ6 ወር ክብደት የተገኘው የዘር ውርስ መጠን (h²) {h2} ነው፤ ምርጥ 6 አውራ ፍየሎችን ይያዙ፤ አውራ × መንደር መስተጋብር የለም፤ በየዓመቱ ለእያንዳንዱ ግልገል {gain} ኪግ ይጨመራል፣ ይህም ይከማቻል።
* **ማደለብ፦** ሙሉ የፋብሪካ መኖ (T4) ፈጣን ዕድገት ቢሰጥም በዚህ ዋጋ በጣም ትርፋማው በአካባቢ የሚመረተው የላም አተር ድርቆሽ (T2) ነው።
* **ወሳኙ ቁጥር፦** የፋብሪካ መኖ ከ{be_conc} ብር/ኪግ በታች ካልሆነ T2 ያሸንፋል።

*Data in this module are simulated for teaching from published Ethiopian values:*
*[Abergelle CBBP evaluation, Hawassa University](https://etd.hu.edu.et/handle/123456789/640) (six-month weight, heritabilities) ·
[ZPLAN breeding schemes for Abergelle and Western Lowland goats](https://journal.uni-mate.hu/index.php/aak/article/download/2100/2616/2327) (σa 1.45, σp 2.74) ·
[Genetic parameters and breeding plans for CBBP goats](https://agris.fao.org/search/en/records/64746b442d3f560f80a89575) (predicted annual gain) ·
[Birth weight in village breeding programmes, LRRD](https://lrrd.org/lrrd28/8/teme28135.html) ·
[On-farm goat fattening with cowpea hay and concentrate, Tropentag 2021](https://www.tropentag.de/2021/abstracts/links/Abebe_1Z34yRR6.pdf) (36 yearlings, 28.2 kg) ·
[ICARDA goat feeding demonstration](https://mel.cgiar.org/reporting/download/hash/YNtSqdaW) (400 g/day supplement, partial budget, MRR) ·
[Goat supplementation trial with 90-day feeding and fortnightly weighing](https://springerlink.bibliotecabuap.elogim.com/content/pdf/10.1007/s11250-017-1477-3.pdf) ·
[Partial budget of goat feeding systems, LRRD](https://lrrd.org/lrrd17/6/lege17066.htm).*
