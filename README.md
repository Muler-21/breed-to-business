# Breed to Business · ከዝርያ እስከ ንግድ

**Ethiopia's plant and animal genetic resources, from field design to company.**

A practical curriculum for breeders, students and young agri-entrepreneurs in Africa. Every module starts from a real decision someone has to make on African land, shows how to lay out the trial in the field, records the right data, runs every analysis (ANOVA, mixed models, G × E, breeding values), draws the charts a decision needs, and ends with the business that the result makes possible.

**Website:** https://muler-21.github.io/breed-to-business/

## Start here: the crop advisor and the catalogue

[`crops/`](https://muler-21.github.io/breed-to-business/crops/) is the **crop advisor**: profiles of 60 major crops, vegetables, fruits and spices of Ethiopia (8 cereals, 8 pulses, 6 oilseeds, 6 roots and tubers, 9 vegetables, 8 fruits, 12 spices, coffee, sugarcane and cotton). For each: where it grows, the diseases and pests to beat, climate and soil stresses, the traits to breed for, the breeding method, and sources. A variety finder ranks registered varieties for your altitude, rainfall and priority (yield, disease resistance, drought, early maturity, quality). Data: [`catalogue/crops.csv`](catalogue/crops.csv).


[`catalogue/`](catalogue/) holds open, sourced tables of **Ethiopia's livestock breeds** (99 breeds and populations of cattle, sheep, goats, chickens, camels, horses, donkeys and honeybees) and **the national Crop Variety Register**. The crop table fills completely when the **Scrape crop variety register** workflow runs (Actions tab → Run workflow), or with `python tools/scrape_ethioseed.py` on your own computer (see [catalogue/README.md](catalogue/README.md)).

## Modules ready now

| # | Module | The decision | What you get |
|---|---|---|---|
| 1 | [Testing 60 teff varieties across locations and years](modules/01-teff-met/) | Which varieties to release, and where? | Alpha-lattice design, 15 randomised field books, site and combined ANOVA, heritability planning, AMMI, GGE "which won where", Finlay–Wilkinson stability, decision map, seed-business arithmetic, R script |
| 2 | [Goats: breed better bucks, fatten for profit](modules/02-goat-breeding-fattening/) | Which bucks to keep? Which ration pays? | Community-based breeding records, sire-model heritability, BLUP breeding values, buck × village G × E, genetic gain; RCBD fattening trial, ANCOVA, Tukey, partial budget and break-even feed price |
| 3 | [The variety development plan](modules/03-variety-development-plan/) | What to breed for, and how to get a variety from parents to farmers? | Product profiles, the self-pollinated pipeline (entries, sites, reps, designs per stage), plans for hybrid, clonal and perennial crops, disease screening with AUDPC, durable resistance, climate adaptation, selection index, genetic gain per year, seed multiplication and the seed business |
| 4 | [Sheep: from the ground to a company](modules/04-sheep-ground-to-company/) | How to turn Ethiopia's 42.9 million sheep into a breeding and meat business? | **Real genomics** on public SNP data of 292 Ethiopian sheep (PCA, FST, ROH, genome scan, genomic relationships), published heritabilities and genetic trends, CBBP design and inbreeding control, AI, health calendar, crossbreeding lessons, fattening economics, markets (meat, export, leather), a three-business company plan |
| 5 | [Five agri-businesses to start around Debre Markos, A to Z](modules/05-five-businesses-debre-markos/) | Which business first, what it costs and earns, which licences, how to survive insecurity? | 11 ideas scored on 7 criteria; full plans for teff flour and injera, sheep fattening and rams, honey, quality seed, forage and feed; 5-year models (NPV, IRR, payback, DSCR, sensitivity); finance sources; an A–Z launch checklist |

Each module folder holds `run.py` (one command reproduces everything), `fieldbooks/`, `data/`, `tables/`, `figures/` and a written guide (`README.md`) in English with an Amharic summary. Data are simulated for teaching from published Ethiopian values; swap in your own field books to analyse a real trial.

```bash
pip install -r requirements.txt
python modules/01-teff-met/run.py
python modules/02-goat-breeding-fattening/run.py
python modules/03-variety-development-plan/run.py
python modules/04-sheep-ground-to-company/genomics/analyse.py <path>/OaSNP2818x28210   # data: branch data-sheep
python modules/04-sheep-ground-to-company/run.py
python modules/05-five-businesses-debre-markos/run.py
python tools/scrape_ethioseed.py  # fill the full crop variety register (run on your computer)
python tools/build_site.py        # rebuild the website pages
```

The analysis library `b2b/` uses only numpy, pandas, scipy and matplotlib, so it runs on any laptop: `core.py` (ANOVA, Tukey), `met.py` (alpha-lattice design, multi-environment trials, AMMI, GGE, stability), `livestock.py` (sire model, BLUP, genetic gain, fattening trials, partial budget), `plots.py`.

## Roadmap: from the ground to a company

| Stage | Modules planned |
|---|---|
| 1 · Know the resources | ✅ Catalogue of livestock breeds and the crop variety register (scraper). Next: landraces from the national genebank, performance data, Amharic names |
| 2 · Design toolkit | CRD, RCBD, Latin square, split-plot, augmented designs for unreplicated germplasm, on-farm trials, sample size and power |
| 3 · Crop breeding | Ready: crop advisor (60 crops), variety development plan (Module 3), multi-location trials (Module 1). Next: germplasm characterisation, participatory variety selection |
| 4 · Livestock breeding | Ready: goats (Module 2), sheep ground to company with real genomics (Module 4). Next, species by species: goats in full, cattle (dairy and beef), chicken, camel, honeybee, equines |
| 5 · Genomics and data | Started: public SNP data analysis for sheep (Module 4). Next: GWAS and genomic selection with PLINK and R |
| 6 · The company | Started: five business plans for Debre Markos with five-year models (Module 5). Next: variety release and plant variety protection, investor pitching |

## Author

**Mulusew Kassa Bitew**
Postdoctoral Research Fellow, University of Molise, Italy
Department of Plant Science, College of Agriculture and Natural Resources, Debre Markos University, Ethiopia

ORCID [0000-0001-6223-0037](https://orcid.org/0000-0001-6223-0037) · GitHub [@Muler-21](https://github.com/Muler-21) · [muler-21.github.io](https://muler-21.github.io)

Other apps: [Tech Stories](https://muler-21.github.io/Teck_Stories/) · [AdaptFit](https://muler-21.github.io/apps/adaptfit/) · [Sebel Hakim](https://muler-21.github.io/sebel-hakim/) · [Research Integrity Compass](https://muler-21.github.io/research-integrity-compass/) · [AMBKidsJoy](https://muler-21.github.io/AMBKidsJoy/)

© 2026 Mulusew Kassa Bitew. All rights reserved.

## Citation

Please cite this work using [CITATION.cff](CITATION.cff).
