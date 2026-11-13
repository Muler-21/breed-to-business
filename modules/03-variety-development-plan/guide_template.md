# Module 3 · The variety development plan: from parents to farmers' fields

**ሞጁል 3 · የዝርያ ማሻሻያ ዕቅድ፦ ከወላጅ ዝርያዎች እስከ አርሶ አደሩ ማሳ**

> **The business question.** A variety is a product. Farmers buy it only if it beats what they grow, on their land, against the diseases and weather they face, and the grain sells. This module is the plan a breeding programme or a seed company follows to get there: what to breed for, how many lines to test where and when, how to screen for disease and climate stress, how to combine yield with resistance, how fast you gain, and how seed reaches farmers.

Use it with the **[crop advisor](../../crops/)**, which holds profiles of {n_crops} Ethiopian crops (cereals, pulses, oilseeds, roots and tubers, vegetables, fruits, spices, coffee) and recommends registered varieties for an altitude, a rainfall and a priority. Module 1 is the multi-location stage of this plan in full detail.

Numbers in the worked examples (disease scores, the 200-line trial, gains) are **simulated or illustrative for teaching**; the stages, designs and release steps follow Ethiopian practice as published in variety registration papers.

---

## 1. Start from a product profile, not from a cross

Before making a single cross, write down what the new variety must do better than the best variety farmers already grow. A product profile has four parts:

1. **Where:** the target environments (altitude, rainfall, soil, season). In Ethiopia altitude is the first sorting variable: the same crop faces different diseases at 1,800 m and at 2,600 m.
2. **What kills yield there:** the two or three diseases, pests and climate stresses that cost farmers the most.
3. **What the market pays for:** seed colour (very white teff), grain size (faba bean), pungency and colour (berbere pepper), cup quality (coffee), processing quality (potato chips, malt barley).
4. **The check to beat:** the most popular released variety in that area. A new variety must beat it on yield *and* not lose on any trait farmers care about.

Product profiles for some of Ethiopia's major crops (full list in the crop advisor and in [`catalogue/crops.csv`](https://github.com/Muler-21/breed-to-business/blob/main/catalogue/crops.csv)):

{product_profiles}

---

## 2. The pipeline for a self-pollinated crop

Teff, wheat, barley, rice, sorghum, most pulses, sesame, linseed and tomato fix their genes by selfing, so a selected line breeds true. This is the standard Ethiopian path, from crosses to the National Variety Release Committee (NVRC):

![Pipeline funnel](figures/01_pipeline_funnel.png)

{pipeline}

What the published release papers show:

- **Felagot teff** came from a cross between Quncho and the farmers' cultivar Gea Lammie, inbred for at least seven generations; 12 genotypes were then tested over two years at six teff locations, and the NVRC released it in March 2017.
- **Pawe-2 upland rice** was tested in a national variety trial at five sites for two years in an RCBD with three replications, then in verification trials, before the NVRC approved it.
- **Shafeta orange-fleshed sweet potato** went through a national variety trial at three sites over two years, then a variety verification trial against two standard checks.
- **Kale K14 and K18** (released May 2026) went through characterisation, preliminary screening, multi-location trials, the NVT and verification at eight sites; breeder seed multiplication then started at Kulumsa.

**Rules that save years:**

- Select only highly heritable traits in early generations (height, maturity, seed colour, disease on spreader rows). Do not select for yield on single unreplicated plots: heritability there is too low.
- Use an irrigated off-season site to grow two generations a year.
- Put every stage from the PYT on in an **alpha-lattice** (Module 1). Fields in the highlands are not uniform.
- Always include the **standard check** (best released variety for the area) and a **local check** (farmers' variety). The release committee compares against both.

---

## 3. Plans by how the crop reproduces

![Timelines](figures/02_timelines.png)

| Reproduction | Crops | How you make a variety | Typical years to release | What to watch |
|---|---|---|---|---|
| **Self-pollinated** | Teff, wheat, barley, rice, sorghum, faba bean*, field pea, chickpea, lentil, haricot bean, sesame, linseed, tomato, black cumin, fenugreek | Cross, then inbreed to pure lines (single-seed descent, bulk or pedigree); test lines | 8–11 | Keep diversity: cross landraces into elite lines |
| **Cross-pollinated / hybrid** | Maize, onion, noug, sunflower, head cabbage, carrot, coriander | Hybrids: develop inbred lines in heterotic groups, test their crosses, sell F1 seed every year. Or population improvement (recurrent selection) for open-pollinated and synthetic varieties | 9–12 | Hybrid seed must be bought each season: a business, but farmers need the cash and a seed company to deliver |
| **Clonal** | Potato, sweet potato, enset, taro, cassava, ginger, turmeric, garlic, shallot, banana, sugarcane | Cross (or collect), then every good seedling is a clone: no inbreeding needed. Test clones over generations and sites | 8–11 | Viruses and bacterial wilt travel in planting material. Clean seed (tissue culture, mini-tubers) is half of the variety |
| **Perennial tree crops** | Coffee, avocado, mango, citrus, apple | Select elite mother trees (from forests, gardens, introductions); test progenies or grafted clones over 4–6 harvests; propagate by seed lines, grafting or budding | 15–20 | Each cycle is long, so start from the best existing trees and use rootstocks for soil diseases |

\* Faba bean is partly cross-pollinated by bees: isolate selection plots or use bags, or lines drift.

---

## 4. Breeding for disease resistance

**Where to screen.** Screen where the disease is every year: a *hot-spot* site, with rows of a very susceptible variety (spreader rows) around and through the trial so every line is exposed. For diseases that are not reliable in the field, inoculate. Wheat rust screening in Ethiopia uses hot-spot sites in the Arsi and Bale highlands; faba bean chocolate spot and gall need wet highland sites.

**How to score.** Score the same plots 4–6 times through the epidemic, as % leaf area diseased or on a 1–9 scale, and compute the **area under the disease progress curve (AUDPC)**. AUDPC separates a line that stays clean from one that only starts late.

![AUDPC](figures/03_disease_progress_audpc.png)

{audpc}

AUDPC = Σ (sᵢ + sᵢ₊₁)/2 × (tᵢ₊₁ − tᵢ). The *relative* AUDPC (as % of the susceptible spreader) lets you compare sites and years. Analyse it with the same ANOVA as yield (log-transform if variances differ).

**How to make resistance last.**

- **Avoid relying on one major gene.** A single major gene (all-or-nothing resistance) is often defeated by a new pathogen race within a few years. The 2010 yellow rust epidemic in Ethiopia hit about 600,000 ha of wheat; the varieties Kakaba and Danda'a stayed resistant and were then fast-tracked to farmers.
- **Prefer slow-rusting, adult-plant resistance** (line B above): several minor genes that slow the epidemic. It is harder to defeat.
- **Pyramid** two or three resistance genes in one variety, using markers where they exist.
- **Backcross to fix a defect.** When a popular variety has one weakness, backcross a resistance source into it and keep everything else. Faba bean breeders used this "defect removal" approach to add chocolate spot resistance.
- **Deploy diverse varieties** across an area, and keep monitoring races with trap nurseries.
- **Clean planting material** for clonal crops: for ginger bacterial wilt, enset bacterial wilt, potato viruses and late blight, a resistant variety on infected seed still fails.

---

## 5. Breeding for climate adaptation

1. **Define the target population of environments.** Map where the crop is grown by altitude, rainfall, season length and soil (vertisols, acid soils). Group them into a few *mega-environments*.
2. **Test in the right places.** Pick trial sites that represent each mega-environment, including the stressed end (Alem Tena in Module 1). Use managed stress where nature is unreliable: late sowing or rain-out shelters for terminal drought, acid-soil sites (western Oromia, Awi) for aluminium tolerance, undrained vertisols for waterlogging.
3. **Match maturity to the season.** In dry, short-season areas an early variety *escapes* terminal drought. In Module 1, TF47 matures about 11 days earlier than Quncho and still yields well in high-potential sites.
4. **Measure stability and decide broad or specific adaptation.** Run the multi-location analysis (combined ANOVA, AMMI, GGE which-won-where, Eberhart–Russell) from Module 1. Release a widely adapted variety where one is stable everywhere, and separate varieties for separate mega-environments where the which-won-where plot splits them.
5. **Plan for the next 20 years, not the last 20.** Climate warming pushes diseases uphill (coffee leaf rust at lower altitudes, wheat rusts) and shortens seasons in the lowlands. Test today's lines at sites that are already as warm as the target area will be.

---

## 6. Combining yield, disease and maturity: the selection index

A breeder rarely gets one trait at a time. In this simulated preliminary yield trial (200 lines, 2 sites), taller and later lines yield more but also carry more disease. Selecting the top 20 on yield alone keeps the susceptible ones.

![Selection index](figures/04_selection_index.png)

A simple index standardises each trait and adds them with economic weights: **I = 1.0 × z(yield) − 0.7 × z(disease) − 0.4 × z(days to maturity)**. Here the weights say that a one-standard-deviation rise in disease costs 70 % as much as a one-SD gain in yield.

{sel}

The yield-only top 20 included **{yield_only_bad} lines scoring 6 or worse** for disease; the index top 20 included **{index_bad}**. The index gave up **{yield_loss} t/ha** of average yield in this trial to buy resistance and **{days_saved} days** earlier maturity: yield that the susceptible lines would lose in an epidemic year anyway.

Set the weights with farmers and buyers: how much yield would they give up for a variety that does not need fungicide, or that is ready two weeks earlier?

---

## 7. How fast you gain: shorten the cycle

The breeder's equation gives genetic gain per year: **ΔG = i × r × σA / L**, where *i* is selection intensity, *r* the accuracy of selection, *σA* the additive genetic standard deviation, and *L* the years from making a cross to using its best offspring as parents.

![Genetic gain](figures/05_genetic_gain.png)

{gain}

With the same field budget, programme D gains **{gain_d} %** a year against **{gain_a} %** for the conventional one: **{gain_ratio} times faster**, mostly because L falls from 10 to 3 years. The cheap first step is the off-season nursery and recycling the best PYT lines as parents straight away; genomic prediction comes later, once a programme has genotyped trials to train on.

---

## 8. Release, seed and the business

1. **NVT (2 years, multi-location, standard + local checks)** → **VVT** on station and on farms → **NVRC field evaluation and release** → entry in the national Crop Variety Register (see the [catalogue](../../catalogue/)).
2. **Seed classes:** breeder seed (kept by the breeding centre) → pre-basic → basic → certified seed sold to farmers. Each class is a season of multiplication under inspection.

![Seed multiplication](figures/06_seed_multiplication.png)

{seed}

Twenty kilograms of breeder teff seed can plant about **{cert_ha} ha** of farmers' fields in the fifth season, *if* every class is multiplied on time. The usual bottleneck in Ethiopia is not the breeding but this chain: many released varieties never reach farmers at scale.

**Where the entrepreneur fits:**

- **Seed company or seed cooperative:** license a released variety (or a public one), multiply basic → certified seed, and sell it. Hybrids (maize, vegetables) mean repeat customers every season.
- **Clean planting material:** tissue-cultured potato mini-tubers, ginger and turmeric rhizomes, banana plantlets, grafted avocado and mango seedlings. Disease-free material is a product farmers will pay for.
- **Contract breeding and trials:** run multi-location trials (Module 1) for seed companies and NGOs.
- **Market varieties:** malt barley for breweries, export white haricot beans, high-colour pepper for oleoresin, specialty coffee. Here the buyer often pays for the seed system.

---

## በአማርኛ አጭር ማጠቃለያ

- ዝርያ ምርት ነው። አርሶ አደሩ የሚገዛው በማሳው ላይ፣ በሽታውንና የአየር ንብረቱን ተቋቁሞ ካለው ዝርያ በላይ ሲያመርትና ምርቱ ሲሸጥ ብቻ ነው።
- **የምርት መገለጫ (product profile)** ይጻፉ፦ የት (ከፍታ፣ ዝናብ፣ አፈር)፣ ምርትን የሚቀንሱ በሽታዎችና ተባዮች፣ ገበያው የሚፈልገው ባሕርይ፣ እና ሊበለጥ የሚገባው ደረጃ ዝርያ።
- ራሳቸውን የሚያዳቅሉ ሰብሎች (ጤፍ፣ ስንዴ፣ ገብስ፣ ጥራጥሬዎች)፦ ማዳቀል → F1–F5 → የምልከታ ማሳ → PYT → AYT → ብሔራዊ የዝርያ ሙከራ (2 ዓመት፣ በብዙ ቦታዎች) → የማረጋገጫ ሙከራ (VVT) → በብሔራዊ የዝርያ አጽዳቂ ኮሚቴ መልቀቅ። ከ8–11 ዓመት ይወስዳል።
- በቆሎና ሽንኩርት (ዲቃላ)፣ ድንችና ዝንጅብል (በክሎን የሚራቡ)፣ ቡናና አቮካዶ (ቋሚ ተክሎች) የተለያየ ዕቅድ አላቸው። ቋሚ ተክሎች 15–20 ዓመት ይፈጃሉ።
- **በሽታን መቋቋም፦** በሽታው ሁልጊዜ በሚገኝበት ቦታ ይሞክሩ፣ በተደጋጋሚ ይመዝግቡ፣ AUDPC ያስሉ። በአንድ ዋና ዘረመል ብቻ አይመኩ፤ ቀስ ብሎ የሚታመም (slow rusting) መቋቋምን ይምረጡ። በ2010 ቢጫ ዋግ ወደ 600,000 ሄክታር ስንዴ አጥቅቷል።
- **የአየር ንብረት መላመድ፦** የሙከራ ቦታዎች የደረቁትንና አሲዳማ አፈር ያላቸውን ቦታዎች ያካትቱ፤ ቀድመው የሚደርሱ ዝርያዎች ድርቅን ያመልጣሉ፤ የመረጋጋት ትንተና (ሞጁል 1) ይጠቀሙ።
- **የምርጫ መለኪያ (selection index)፦** ምርትን ብቻ መምረጥ በሽታ የሚይዛቸውን መስመሮች ያስቀራል፤ ምርት፣ በሽታና የመድረሻ ቀንን አንድ ላይ ይመዝኑ።
- **የዘረመል ዕድገት = i × r × σA / L።** ዑደቱን ማሳጠር (በዓመት ሁለት ትውልድ፣ ጥሩ መስመሮችን ቶሎ ወላጅ ማድረግ) ከትልቅ ሙከራ በላይ ይጠቅማል።
- **ዘር፦** የአርቢ ዘር → ቅድመ-መሠረታዊ → መሠረታዊ → የተረጋገጠ ዘር። የዘር ኩባንያ፣ ንጹሕ የመትከያ ቁሳቁስ (ቲሹ ካልቸር) እና የኮንትራት ሙከራ የሥራ ፈጠራ ዕድሎች ናቸው።

## Sources

- Felagot tef release: [Ethiop. J. Agric. Sci.](https://ajol.info/index.php/ejas/article/view/201108)
- Pawe-2 rice release: [East African Journal of Sciences](https://www.eajs.haramayajournals.org/index.php/eajs/article/view/1857)
- Shafeta sweet potato release: [Ethiop. J. Agric. Sci. 34(1)](https://ajol.info/index.php/ejas/article/view/276022/260501)
- Kale K14 and K18 release, 2026: [FreshPlaza](https://www.freshplaza.com/africa/article/9845533/ethiopia-releases-first-locally-adapted-kale-varieties/)
- Wheat rust epidemic and fast-track release: [ICARDA](https://mel.cgiar.org/reporting/download/hash/2uerl9Gt); [CIMMYT](https://cimmyt.org/?p=19901)
- Faba bean backcross defect removal: [IJGPB](https://isgpb.org/journal/index.php/IJGPB/article/download/198/1979)
- Variety register size and seed uptake: [Trends of crop variety release in Ethiopia](https://ajol.info/index.php/ejcs/article/view/267222/252133)
- All crop profile sources: [`catalogue/sources.csv`](https://github.com/Muler-21/breed-to-business/blob/main/catalogue/sources.csv)

**Reproduce:** `python modules/03-variety-development-plan/run.py` writes the figures, the tables in [`tables/`](tables/) and this guide.
