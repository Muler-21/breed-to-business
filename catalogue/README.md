# Catalogue · Ethiopia's crop varieties and livestock breeds

**ካታሎግ · የኢትዮጵያ የሰብል ዝርያዎችና የእንስሳት ዝርያዎች**

Two open tables that every other module builds on:

| File | What | Status |
|---|---|---|
| [`livestock_breeds.csv`](livestock_breeds.csv) | Breeds and populations of cattle, sheep, goats, chickens, camels, horses, donkeys and honeybees, with synonyms, breed group, region and notes | 99 entries, every row cited in [`sources.csv`](sources.csv) |
| [`crop_varieties.csv`](crop_varieties.csv) | Every variety in the national Crop Variety Register: crop, register issue, year, pedigree, adaptation, altitude, rainfall, seed rate, fertilizer, maturity, yield, breeder, seed colour, disease reaction | 8 verified sample records now; **run the scraper to fill the full register** |

## Livestock: how the list was built

The backbone is ILRI's Domestic Animal Genetic Resources Information System (DAGRIS) "Breeds in Ethiopia". Sheep follow the 14 traditional populations in four groups, plus breeds reported more recently. Horses follow the eight populations identified by Kefena et al. (2012), donkeys the six populations of Kefena et al. (2014), and honeybees the five morphoclusters of Amssalu et al. (2004). Region and agro-ecology are filled **only where a cited source gives them**. Blank cells are gaps to fill, not zeros.

Breed lists are not final. Official counts differ between sources (for example, 28, 31 or 32 cattle breeds), because populations are still being characterised. Each row says where it came from, so you can judge it.

## Crops: complete the register in one command

The Ministry of Agriculture's seed portal publishes the Crop Variety Register online, one page per variety. A recent review counted 1,489 varieties of 149 crops registered up to 2021, and more are added every year. The portal can't be reached in bulk from the workspace where this repository was built, so the scraper is meant to run on your own computer:

```bash
python tools/scrape_ethioseed.py              # ids 1..2500, about 1 hour at 1.5 s per page
python tools/build_site.py                     # rebuild the catalogue page
```

It reads `robots.txt`, waits between requests, caches every page (a stopped run resumes), and writes `catalogue/crop_varieties.csv`. Commit the CSV, not the cache.

## Next additions

* Farmers' varieties and landraces held in the national genebank (Ethiopian Biodiversity Institute) and in Genesys
* Performance data per breed (body weight, milk, prolificacy) from characterisation studies
* Amharic names for every breed and crop
