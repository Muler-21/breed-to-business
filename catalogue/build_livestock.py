"""Build catalogue/livestock_breeds.csv and catalogue/sources.csv.

Every row cites a source id. Breed lists follow DAGRIS (ILRI) "Breeds in Ethiopia",
completed with published characterisation studies for sheep, horses, donkeys and
honeybees. Region/agro-ecology is filled only where a cited source gives it.
"""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))

SOURCES = [
 ("DAGRIS", "ILRI DAGRIS: Breeds in Ethiopia (country listing)", "https://dagris.info/countries/192/breeds"),
 ("DAGRIS-R", "ILRI DAGRIS: Ethiopia regional breed listing", "https://dagris.info/regions/66/breeds?page=2"),
 ("FAO-CR", "FAO: State of Ethiopia's farm animal genetic resources (summary: 28 cattle, 9 sheep, 8 goat, 8 horse, 6 donkey, 7 chicken breeds)", "https://fao.org/4/i4787e/i4787e13.pdf"),
 ("GIZAW-TB28", "Solomon Gizaw (2008). Sheep breeds of Ethiopia: a guide for identification and utilization. ESGPIP Technical Bulletin 28", "https://goats.langston.edu/LINC/AIGR/tb/TB 28 Sheep breeds of Ethiopia.pdf"),
 ("SHEEP-REV", "Review of reproductive performance of Ethiopian indigenous sheep (14 breeds in four groups; recently reported breeds), Cogent Food & Agriculture 2024", "https://www.informahealthcare.com/doi/full/10.1080/23311932.2024.2353674?src=exp-la"),
 ("HORSE", "Kefena et al. (2012) Morphological diversities and ecozones of Ethiopian horse populations; Effa et al. (2021) Genes 12:155", "https://hdl.handle.net/10568/21160"),
 ("HORSE-W", "Ethiopian horses: breed descriptions (Bale, Borana, Horro, Kafa, Kundudo, Ogaden, Selale)", "https://www.doc.surf/wiki/ethiopian-horses"),
 ("DONKEY", "Kefena et al. (2014) Genetic diversity and matrilineal genetic signature of native Ethiopian donkeys", "https://hdl.handle.net/10568/41649"),
 ("DONKEY-MS", "Genetic diversity of Ethiopian donkeys from microsatellites (lowland vs highland lineages), Trop. Anim. Health Prod. 2021", "https://doi.org/10.1007/s11250-021-02776-2"),
 ("BEES", "Amssalu et al. (2004) Multivariate morphometric analysis of honeybees in the Ethiopian region, Apidologie 35:71-81", "https://www.apidologie.org/10.1051/apido:2003066"),
 ("BEES-TAX", "Pauly & Hora: Apini and Meliponini from Ethiopia (taxonomic status of bandasii and woyi-gambella)", "https://tb.plazi.org/GgServer/html/039E87A9FFA3FFF1FDCDFE25F7BFF31E"),
 ("SHEKO", "Management practice of the Sheko cattle breed in Ethiopia: a review, Genetic Resources", "https://www.genresj.org/index.php/grj/article/download/genresj.IBNU2035/179?inline=1"),
 ("NORTH6", "Zerabruk et al. (2007) Characterization of six cattle breeds in North Ethiopia, AGRI 40", "https://www.fao.org/docrep/pdf/010/a1128t/a1128t02.pdf"),
 ("FOGERA", "Genetic improvement of indigenous cattle breeds in Ethiopia: Fogera open nucleus scheme (review), Genetic Resources 2024", "https://genresj.org/index.php/grj/article/view/146"),
 ("CBBP", "Breeding plans for major sheep and goat breeds of Ethiopia (Begait, Bonga, Horro, Menz sheep; Abergelle, Arsi-Bale goats), ICARDA/ILRI", "https://mel.cgiar.org/reporting/downloadmelspace/hash/07HExS3J/v/ee7feb016ee7bd554bcbf5dd883a68e1"),
 ("CBBP-G", "Productivity benchmarks for community-based breeding of Abergelle, Central Highland and Woyto-Guji goats, LRRD 31(5) 2019", "https://lrrd.org/lrrd31/5/tjbak31074.html"),
 ("CATTLE-REV", "Hunde & Tadese (2020) Genetic distance and differentiation among cattle breeds in Ethiopia: a review", "https://ajol.info/index.php/ejap/article/view/255687"),
]

# species, breed, synonyms, breed_group, region / agro-ecology, notes, sources
ROWS = [
 # ---------------- cattle (DAGRIS) ----------------
 ("Cattle", "Arsi", "Arusi", "Large East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Ethiopian Boran", "Borana", "Large East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Somali Boran", "Awai", "Large East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Barka", "Begait", "Large East African Zebu", "Western Tigray (Begait type at Tekeze river, Sheraro)", "Pastoral breed with the highest milk production of six northern breeds studied", "DAGRIS; NORTH6"),
 ("Cattle", "Murle", "", "Large East African Zebu", "", "", "DAGRIS-R"),
 ("Cattle", "Bale", "", "Small East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Goffa", "Goffa Dwarf", "Small East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Guraghe", "", "Small East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Hammer", "", "Small East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Harar", "", "Small East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Jem-Jem", "Black Highland Cattle", "Small East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Mursi", "", "Small East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Smada", "", "Small East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Baherie", "Arab Cattle, Bahari, Berbera", "Small East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Ogaden Zebu", "Lowland Zebu", "Small East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Ambo", "", "Small East African Zebu", "", "", "DAGRIS"),
 ("Cattle", "Afar", "", "Small East African Zebu", "Afar (Igahiboda type, Abala)", "Short calving interval among northern breeds", "DAGRIS; NORTH6"),
 ("Cattle", "Adwa", "", "Small East African Zebu", "", "", "DAGRIS-R"),
 ("Cattle", "Danakil", "Adal, Adali, Afar, Kereyu, Keriyu", "Sanga", "", "", "DAGRIS"),
 ("Cattle", "Raya-Azebo", "Galla-Azebo", "Sanga", "", "", "DAGRIS"),
 ("Cattle", "Anuak", "Abigar", "Sanga", "", "", "DAGRIS"),
 ("Cattle", "Aliab Dinka", "", "Sanga", "", "", "DAGRIS"),
 ("Cattle", "Fogera", "", "Zenga", "Around Lake Tana, Amhara", "Milk-type local breed; open nucleus breeding scheme", "DAGRIS; FOGERA"),
 ("Cattle", "Horro", "", "Zenga", "", "", "DAGRIS"),
 ("Cattle", "Arado", "", "Zenga", "", "", "DAGRIS"),
 ("Cattle", "Sheko", "Shewa-Ghimira, Goda, Mitzan, Mizan", "Humpless Shorthorn (taurine)", "South-west: Bench-Sheko, Sheka and Keffa zones", "Trypano-tolerant; population declining through interbreeding with zebu", "DAGRIS; SHEKO"),
 ("Cattle", "Medenece", "Medenes", "Composite", "", "", "DAGRIS"),
 ("Cattle", "Semien", "", "Composite", "", "", "DAGRIS"),
 ("Cattle", "Wegera", "", "Composite", "", "", "DAGRIS"),
 ("Cattle", "Dembia", "", "Composite", "", "", "DAGRIS"),
 ("Cattle", "Qocherie", "Local", "Composite", "", "", "DAGRIS"),
 ("Cattle", "Mahbere-Slassie", "The Monastery", "Composite", "", "", "DAGRIS"),
 ("Cattle", "Irob", "", "", "", "Studied for molecular diversity", "CATTLE-REV"),
 # ---------------- sheep ----------------
 ("Sheep", "Menz", "Ethiopian Highland, Abyssinian, Legagora", "Sub-alpine short fat-tailed (coarse wool)", "Sub-alpine highlands", "Community-based breeding programme breed", "DAGRIS; SHEEP-REV; CBBP"),
 ("Sheep", "Farta", "", "Sub-alpine short fat-tailed", "Sub-alpine highlands", "", "DAGRIS; SHEEP-REV"),
 ("Sheep", "Sekota", "", "Sub-alpine short fat-tailed", "Sub-alpine highlands", "", "SHEEP-REV; GIZAW-TB28"),
 ("Sheep", "Wollo", "Wello", "Sub-alpine short fat-tailed", "Sub-alpine highlands", "", "DAGRIS; SHEEP-REV"),
 ("Sheep", "Tikur", "Tukur, Lasta, Ethiopian Highland, Abyssinian", "Sub-alpine short fat-tailed (coarse wool)", "Sub-alpine highlands", "", "DAGRIS; SHEEP-REV"),
 ("Sheep", "Semien", "Simien", "Sub-alpine short fat-tailed", "Sub-alpine highlands", "Wool/fleece", "SHEEP-REV; GIZAW-TB28"),
 ("Sheep", "Washera", "Agew, Dangilla", "Sub-alpine short fat-tailed (short hair)", "Wet, warmer mid-highlands (Agew Awi)", "", "DAGRIS; SHEEP-REV; GIZAW-TB28"),
 ("Sheep", "Adilo", "", "Highland long fat-tailed", "Mid to high altitude", "", "SHEEP-REV"),
 ("Sheep", "Arsi-Bale", "Ethiopian Highland, Abyssinian, Arusi", "Highland long fat-tailed", "Mid to high altitude", "", "DAGRIS; SHEEP-REV"),
 ("Sheep", "Horro", "Abyssinian, Ethiopian, Wollaga", "Highland long fat-tailed (hair)", "Mid to high altitude, western Oromia", "Community-based breeding programme breed", "DAGRIS; SHEEP-REV; CBBP"),
 ("Sheep", "Bonga", "", "Highland long fat-tailed (hair)", "Mid to high altitude, south-west", "Community-based breeding programme breed", "DAGRIS; SHEEP-REV; CBBP"),
 ("Sheep", "Afar", "Danakil, Adal", "Lowland fat-rumped", "Arid lowlands", "", "DAGRIS; SHEEP-REV"),
 ("Sheep", "Blackhead Somali", "Berbera Blackhead, Blackhead Ogaden, Adali", "Lowland fat-rumped (hair)", "Arid lowlands", "", "DAGRIS; SHEEP-REV"),
 ("Sheep", "Gumuz", "", "Lowland thin-tailed", "Sub-humid lowlands (west)", "The only thin-tailed Ethiopian sheep", "SHEEP-REV"),
 ("Sheep", "Begait", "", "Recently reported", "", "Community-based breeding programme breed", "SHEEP-REV; CBBP"),
 ("Sheep", "Elle", "Ille", "Recently reported", "", "", "SHEEP-REV"),
 ("Sheep", "Abergelle", "", "Recently reported", "", "", "SHEEP-REV"),
 ("Sheep", "Doyogena", "", "Recently reported (long fat-tailed)", "Cool, wet highland (Kembata Tembaro)", "", "SHEEP-REV"),
 ("Sheep", "Abera", "", "Recently reported", "", "", "SHEEP-REV"),
 ("Sheep", "Akale-Guzay", "Shimenzana, Rashaidi", "Fat-tailed coarse wool", "", "Listed by DAGRIS; mainly an Eritrean population", "DAGRIS"),
 # ---------------- goats (DAGRIS) ----------------
 ("Goat", "Abergelle", "", "Short-eared small-horned", "", "Community-based breeding programme breed", "DAGRIS; CBBP; CBBP-G"),
 ("Goat", "Afar", "Adal, Assaorta, Denakil, Abyssinian short-eared", "Short-eared small-horned", "", "", "DAGRIS"),
 ("Goat", "Arsi-Bale", "Arsi, Gishe, Sidama, Manta, Awarch, Arusi", "Short-eared small-horned", "", "Community-based breeding programme breed", "DAGRIS; CBBP"),
 ("Goat", "Central Highland", "Brown Goat, Kaye, Maefur (Eritrea)", "Short-eared small-horned", "", "Community-based breeding programme breed", "DAGRIS; CBBP-G"),
 ("Goat", "Hararghe Highland", "Kotu-Oromo", "Short-eared small-horned", "", "", "DAGRIS"),
 ("Goat", "Keffa", "", "Short-eared small-horned", "", "", "DAGRIS"),
 ("Goat", "Long-eared Somali", "Large-White Somali, Galla, Digodi, Melebo, Boran Somali, Benadir", "Short-eared small-horned", "", "", "DAGRIS"),
 ("Goat", "Short-eared Somali", "Ogaden, Galla, Mudugh, Deghiyer, Issa-Somali", "Short-eared small-horned", "", "", "DAGRIS"),
 ("Goat", "Western Highland", "Agew", "Short-eared small-horned", "", "", "DAGRIS"),
 ("Goat", "Western Lowland", "Shankila, Gumuz", "Short-eared small-horned", "", "DAGRIS also lists Gumuz separately (thin-tailed group)", "DAGRIS"),
 ("Goat", "Woyto-Guji", "Woyto, Guji, Konso", "Short-eared small-horned", "", "Community-based breeding programme breed", "DAGRIS; CBBP-G"),
 ("Goat", "Nubian", "Sudanese Nubian, Shukria, Beladi", "Lop-eared", "", "", "DAGRIS"),
 # ---------------- chickens (DAGRIS) ----------------
 ("Chicken", "Tilili", "Ye-Tilili Doro", "Ecotype", "", "", "DAGRIS"),
 ("Chicken", "Horro", "", "Ecotype", "", "", "DAGRIS"),
 ("Chicken", "Jarso", "", "Ecotype", "", "", "DAGRIS"),
 ("Chicken", "Tepi", "", "Ecotype", "", "", "DAGRIS"),
 ("Chicken", "Chefe", "", "Ecotype", "", "", "DAGRIS"),
 ("Chicken", "Netch (white plumage)", "Netch doro", "Plumage variety", "", "", "DAGRIS"),
 ("Chicken", "Tikur (black plumage)", "Tikur doro", "Plumage variety", "", "", "DAGRIS"),
 ("Chicken", "Kei (red plumage)", "Kei doro", "Plumage variety", "", "", "DAGRIS"),
 ("Chicken", "Gebsima (greyish mixed plumage)", "Gebsima doro", "Plumage variety", "", "", "DAGRIS"),
 ("Chicken", "Naked neck", "", "Variety", "", "", "DAGRIS"),
 # ---------------- camels (DAGRIS) ----------------
 ("Camel", "Afar", "", "Dromedary", "", "", "DAGRIS"),
 ("Camel", "Anfi", "", "Dromedary", "", "", "DAGRIS"),
 ("Camel", "Borena", "", "Dromedary", "", "", "DAGRIS"),
 ("Camel", "Somali/Ogaden", "", "Dromedary", "", "", "DAGRIS"),
 ("Camel", "Ethiopian Dromedary", "", "Dromedary", "", "General entry in DAGRIS", "DAGRIS"),
 # ---------------- horses ----------------
 ("Horse", "Abyssinian", "", "", "North, especially Semien Mountains around Gondar", "Agricultural work; the breed reported to FAO DAD-IS", "HORSE; HORSE-W"),
 ("Horse", "Bale", "", "", "Highlands of Bale Zone, Oromia", "", "HORSE; HORSE-W"),
 ("Horse", "Borana", "", "", "Southern lowlands, Borana (around Megga)", "Kept by pastoralists; not used for draught; slightly diverged genetically", "HORSE; HORSE-W"),
 ("Horse", "Horro", "Horo", "", "Horo area, western Oromia", "Agricultural horse", "HORSE; HORSE-W"),
 ("Horse", "Kafa", "", "", "Rain-forests of Sheka and Keffa zones", "Well conformed, robust", "HORSE; HORSE-W"),
 ("Horse", "Kundudo", "Kundido", "Feral", "Kundudo plateau near Harar (East Hararghe)", "Gravely endangered feral population", "HORSE; HORSE-W"),
 ("Horse", "Ogaden", "Somali, Wilwal", "", "Somali Region, around Jijiga", "Well conformed", "HORSE; HORSE-W"),
 ("Horse", "Selale", "Oromo", "", "Selale / Shewa, central Ethiopia", "Good riding horse", "HORSE; HORSE-W"),
 # ---------------- donkeys ----------------
 ("Donkey", "Abyssinian", "", "Highland lineage", "Highlands", "", "DONKEY; DONKEY-MS"),
 ("Donkey", "Afar", "", "Highland lineage (genetic clustering)", "Afar", "", "DONKEY; DONKEY-MS"),
 ("Donkey", "Hararghe", "", "Highland lineage", "Hararghe", "", "DONKEY; DONKEY-MS"),
 ("Donkey", "Ogaden", "", "Lowland lineage", "Ogaden / Somali Region", "", "DONKEY; DONKEY-MS"),
 ("Donkey", "Omo", "", "Lowland lineage", "Omo valley", "", "DONKEY; DONKEY-MS"),
 ("Donkey", "Sinnar", "", "Lowland lineage", "Western lowlands", "Genetically the most divergent Ethiopian donkey", "DONKEY; DONKEY-MS"),
 # ---------------- honeybees ----------------
 ("Honeybee", "Apis mellifera jemenitica", "", "Morphocluster", "North-west and eastern arid and semi-arid lowlands", "Small, yellow; high tendency to migrate", "BEES"),
 ("Honeybee", "Apis mellifera scutellata", "", "Morphocluster", "West, south and south-west humid midlands", "", "BEES"),
 ("Honeybee", "Apis mellifera bandasii", "", "Morphocluster", "Central moist highlands", "Large, dark; name not formally validated", "BEES; BEES-TAX"),
 ("Honeybee", "Apis mellifera monticola", "simensis (proposed)", "Morphocluster", "Northern mountainous highlands", "Larger, gentler; taxonomy debated", "BEES; BEES-TAX"),
 ("Honeybee", "Apis mellifera woyi-gambella", "", "Morphocluster", "South-western semi-arid to sub-humid lowlands", "Smallest, yellow; name not formally validated", "BEES; BEES-TAX"),
]

with open(os.path.join(HERE, "livestock_breeds.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["species", "breed", "synonyms", "breed_group", "region_agroecology", "notes", "sources"])
    w.writerows(ROWS)
with open(os.path.join(HERE, "sources.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["source_id", "citation", "url"])
    w.writerows(SOURCES)
from collections import Counter
print(len(ROWS), dict(Counter(r[0] for r in ROWS)))
ids = {s[0] for s in SOURCES}
for r in ROWS:
    for s in r[6].split("; "):
        assert s in ids, (r, s)
