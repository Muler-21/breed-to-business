# Breed to Business · ከዝርያ እስከ ንግድ

**Ethiopia's plant and animal genetic resources, from field design to company.**

A practical curriculum for breeders, students and young agri-entrepreneurs in Africa. Every module starts from a real decision someone has to make on African land, shows how to lay out the trial in the field, records the right data, runs every analysis (ANOVA, mixed models, G × E, breeding values), draws the charts a decision needs, and ends with the business that the result makes possible.

**Website:** https://muler-21.github.io/breed-to-business/

## Modules ready now

| # | Module | The decision | What you get |
|---|---|---|---|
| 1 | [Testing 60 teff varieties across locations and years](modules/01-teff-met/) | Which varieties to release, and where? | Alpha-lattice design, 15 randomised field books, site and combined ANOVA, heritability planning, AMMI, GGE "which won where", Finlay–Wilkinson stability, decision map, seed-business arithmetic, R script |
| 2 | [Goats: breed better bucks, fatten for profit](modules/02-goat-breeding-fattening/) | Which bucks to keep? Which ration pays? | Community-based breeding records, sire-model heritability, BLUP breeding values, buck × village G × E, genetic gain; RCBD fattening trial, ANCOVA, Tukey, partial budget and break-even feed price |

Each module folder holds `run.py` (one command reproduces everything), `fieldbooks/`, `data/`, `tables/`, `figures/` and a written guide (`README.md`) in English with an Amharic summary. Data are simulated for teaching from published Ethiopian values; swap in your own field books to analyse a real trial.

```bash
pip install -r requirements.txt
python modules/01-teff-met/run.py
python modules/02-goat-breeding-fattening/run.py
python tools/build_site.py        # rebuild the website pages
```

The analysis library `b2b/` uses only numpy, pandas, scipy and matplotlib, so it runs on any laptop: `core.py` (ANOVA, Tukey), `met.py` (alpha-lattice design, multi-environment trials, AMMI, GGE, stability), `livestock.py` (sire model, BLUP, genetic gain, fattening trials, partial budget), `plots.py`.

## Roadmap: from the ground to a company

| Stage | Modules planned |
|---|---|
| 1 · Know the resources | Catalogue of Ethiopian crop varieties and livestock breeds (cattle, sheep, goats, chickens, camels, equines, honeybees), with sources such as FAO DAD-IS and the Ethiopian Biodiversity Institute |
| 2 · Design toolkit | CRD, RCBD, Latin square, split-plot, augmented designs for unreplicated germplasm, on-farm trials, sample size and power |
| 3 · Crop breeding | Germplasm characterisation, crossing and generation advance, participatory variety selection, seed systems |
| 4 · Livestock breeding | Dairy crossbreeding and milk recording, village poultry testing, sheep CBBPs (Menz, Bonga, Horro) |
| 5 · Genomics and data | Genotyping, GWAS and genomic selection with PLINK and R |
| 6 · The company | Business models, variety release and plant variety protection, finance and pitching |

## Author

**Mulusew Kassa Bitew**
Postdoctoral Research Fellow, University of Molise, Italy
Department of Plant Science, College of Agriculture and Natural Resources, Debre Markos University, Ethiopia

ORCID [0000-0001-6223-0037](https://orcid.org/0000-0001-6223-0037) · GitHub [@Muler-21](https://github.com/Muler-21) · [muler-21.github.io](https://muler-21.github.io)

Other apps: [Tech Stories](https://muler-21.github.io/Teck_Stories/) · [AdaptFit](https://muler-21.github.io/apps/adaptfit/) · [Sebel Hakim](https://muler-21.github.io/sebel-hakim/) · [Research Integrity Compass](https://muler-21.github.io/research-integrity-compass/) · [AMBKidsJoy](https://muler-21.github.io/AMBKidsJoy/)

© 2026 Mulusew Kassa Bitew. All rights reserved.

## Citation

Please cite this work using [CITATION.cff](CITATION.cff).
