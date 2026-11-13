"""Build the GitHub Pages site: index.html at the root and one page per module,
made from each module's README.md. Run after the module scripts:
    python tools/build_site.py
"""
import os, re, glob, html, csv, json
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "https://github.com/Muler-21/breed-to-business"
SITE = "https://muler-21.github.io/breed-to-business/"

CSS = """
:root{--paper:#f4f5f2;--panel:#fff;--ink:#16211b;--muted:#5a665e;--rule:#d8ddd6;--accent:#0f7a6c;--accent-soft:#e1f1ed;--copper:#b5602b;--copper-soft:#f7e8dd;
--display:"Bricolage Grotesque","Segoe UI",system-ui,sans-serif;--body:"Literata",Georgia,serif;--ethi:"Noto Serif Ethiopic","Nyala",serif;--mono:"JetBrains Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root{--paper:#0f1412;--panel:#161d1a;--ink:#e5ebe7;--muted:#9aa8a0;--rule:#28322d;--accent:#4cc3b0;--accent-soft:#15302b;--copper:#e08a52;--copper-soft:#33231a}
 .md img{background:#fff;border-radius:8px}}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:18px/1.65 var(--body)}
a{color:var(--accent)}.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
header.hero{padding:34px 0 26px;border-bottom:1px solid var(--rule)}
.home{font:600 14px var(--display);text-decoration:none}
.kicker{font:500 13px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--copper);margin:14px 0 8px}
h1{font:800 clamp(32px,5.5vw,54px)/1.05 var(--display);margin:0;letter-spacing:-.02em;text-wrap:balance}
h1 .am,.am-title{display:block;font:700 .55em/1.5 var(--ethi);color:var(--accent);margin-top:8px;letter-spacing:0}
.dek{color:var(--muted);max-width:66ch}
.md h1{font-size:clamp(28px,4.4vw,42px);margin-top:10px}
.md h2{font:800 28px/1.2 var(--display);margin:46px 0 12px;padding-top:18px;border-top:1px solid var(--rule)}
.md h3{font:700 20px/1.3 var(--display);margin:28px 0 8px}
.md img{max-width:min(100%,860px);height:auto;display:block;margin:18px auto;border:1px solid var(--rule);border-radius:10px;background:#fff}
.md table{border-collapse:collapse;width:100%;font-size:15px;margin:16px 0;display:block;overflow-x:auto}
.md th,.md td{border-bottom:1px solid var(--rule);padding:8px 10px;text-align:left;vertical-align:top}
.md th{font:700 12.5px var(--mono);text-transform:uppercase;letter-spacing:.04em;color:var(--muted);background:var(--panel)}
.md td{background:var(--panel)}
.md code{font:500 .86em var(--mono);background:var(--panel);border:1px solid var(--rule);border-radius:5px;padding:1px 5px}
.md pre{background:#16211b;color:#e5ebe7;border-radius:10px;padding:14px 16px;overflow-x:auto}
.md pre code{background:none;border:0;color:inherit;padding:0}
.md blockquote{margin:18px 0;padding:14px 18px;border-left:4px solid var(--copper);background:var(--copper-soft);border-radius:0 10px 10px 0}
.md hr{border:0;border-top:1px solid var(--rule);margin:30px 0}
.am-block{font-family:var(--ethi);line-height:1.9}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;margin:26px 0}
.card{display:grid;text-decoration:none;color:inherit;background:var(--panel);border:1px solid var(--rule);border-radius:14px;overflow:hidden}
.card:hover{border-color:var(--accent)}.card img{width:100%;aspect-ratio:16/9;object-fit:cover;object-position:top;background:#fff}
.card .t{padding:16px 18px}.card .n{font:700 12px var(--mono);color:var(--copper)}
.card h2{font:800 22px/1.2 var(--display);margin:4px 0}.card h3{font:600 16px/1.6 var(--ethi);color:var(--accent);margin:0 0 6px}
.card p{margin:0;color:var(--muted);font-size:16px}
.road{display:grid;gap:10px;margin:20px 0}.stage{background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:14px 16px}
.stage b{font:700 16px var(--display)}.stage span{display:block;color:var(--muted);font-size:15.5px}
.stage.ready{border-color:var(--accent)}
footer{padding:30px 0 60px;color:var(--muted);font-size:15px}
.author{padding:20px;border:1px solid var(--rule);border-radius:14px;background:var(--panel);color:var(--ink);font-size:15.5px}
.author .name{font:800 20px var(--display);margin:0 0 4px}.author p{margin:0 0 6px}.author .meta,.author .copy{color:var(--muted)}
.author .apps a{margin-right:10px}.author .copy{font-size:14px;margin-top:10px}
#gc-views{font:500 13px var(--mono);color:var(--muted);text-align:center;margin:18px 0 0}
"""

HEAD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}"><meta name="author" content="Mulusew Kassa Bitew">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{img}"><meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Literata:opsz,wght@7..72,400;7..72,600&family=Noto+Serif+Ethiopic:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
"""

AUTHOR = """<footer class="wrap"><div class="author">
<p class="name">Mulusew Kassa Bitew</p>
<p>Postdoctoral Research Fellow, University of Molise, Italy</p>
<p>Department of Plant Science, College of Agriculture and Natural Resources, Debre Markos University, Ethiopia</p>
<p class="meta">ORCID <a href="https://orcid.org/0000-0001-6223-0037">0000-0001-6223-0037</a> · GitHub <a href="https://github.com/Muler-21">@Muler-21</a> · <a href="https://muler-21.github.io">muler-21.github.io</a></p>
<p class="apps">Other apps: <a href="https://muler-21.github.io/Teck_Stories/">Tech Stories</a> <a href="https://muler-21.github.io/apps/adaptfit/">AdaptFit</a> <a href="https://muler-21.github.io/sebel-hakim/">Sebel Hakim</a> <a href="https://muler-21.github.io/research-integrity-compass/">Research Integrity Compass</a> <a href="https://muler-21.github.io/AMBKidsJoy/">AMBKidsJoy</a></p>
<p class="copy">© 2026 Mulusew Kassa Bitew. All rights reserved. Cite with <a href="{repo}/blob/main/CITATION.cff">CITATION.cff</a>.</p>
</div>
<p id="gc-views" hidden></p>
</footer>
<script>
(function () {{
  var el = document.getElementById("gc-views");
  if (!el || !window.fetch) return;
  fetch("https://ambkidsjoy.goatcounter.com/counter/" + encodeURIComponent(location.pathname) + ".json")
    .then(function (r) {{ if (!r.ok) throw new Error(r.status); return r.json(); }})
    .then(function (d) {{ el.textContent = "👁 " + d.count + " views · እይታዎች"; el.hidden = false; }})
    .catch(function () {{}});
}})();
</script>
<script data-goatcounter="https://ambkidsjoy.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body></html>
""".replace("{repo}", REPO)


def module_page(folder):
    name = os.path.basename(folder)
    src = open(os.path.join(folder, "README.md"), encoding="utf-8").read()
    body = markdown.markdown(src, extensions=["tables", "fenced_code"])
    # links to folders and data files go to GitHub (Pages does not list folders)
    def fix(m):
        href = m.group(1)
        if href.startswith(("http", "#", "mailto")) or href.endswith((".png", ".jpg", ".svg")):
            return m.group(0)
        kind = "tree" if href.endswith("/") else "blob"
        return f'href="{REPO}/{kind}/main/modules/{name}/{href}"'
    body = re.sub(r'href="([^"]+)"', fix, body)
    # Amharic summary paragraphs get the Ethiopic font
    body = body.replace("<h2>በአማርኛ አጭር ማጠቃለያ</h2>\n<ul>", '<h2>በአማርኛ አጭር ማጠቃለያ</h2>\n<ul class="am-block" lang="am">')
    h1 = re.search(r"<h1>(.*?)</h1>", body).group(1)
    title = html.unescape(re.sub("<[^>]+>", "", h1))
    q = html.unescape(re.sub("<[^>]+>", "", re.search(r"<blockquote>\s*<p>(.*?)</p>", body, re.S).group(1)))
    q = re.sub(r"^The business questions?\.\s*", "", q)
    sents = re.split(r"(?<=[.?!])\s+", q)
    desc = sents[0]
    for x in sents[1:]:
        if len(desc) + len(x) > 230:
            break
        desc += " " + x
    url = f"{SITE}modules/{name}/"
    figs = sorted(glob.glob(os.path.join(folder, "figures", "*.png")))
    img = f"{url}figures/{os.path.basename(figs[-2 if len(figs) > 1 else 0])}"
    page = HEAD.format(title=html.escape(title + " · Breed to Business"), desc=html.escape(desc), url=url, img=img, css=CSS)
    page += f'<header class="hero"><div class="wrap"><a class="home" href="../../">← Breed to Business · ከዝርያ እስከ ንግድ</a>' \
            f'<p class="kicker">Module · <a href="{REPO}/tree/main/modules/{name}">code and data on GitHub</a></p></div></header>'
    page += f'<main class="wrap md">{body}</main>' + AUTHOR
    open(os.path.join(folder, "index.html"), "w", encoding="utf-8").write(page)
    return dict(name=name, title=title, desc=desc, url=f"modules/{name}/")


def home(mods):
    am = {"01-teff-met": "60 የጤፍ ዝርያዎችን በተለያዩ ቦታዎችና ዓመታት መሞከር",
          "02-goat-breeding-fattening": "ፍየሎች፦ የተሻሉ አውራ ፍየሎችን ማዳቀልና ለትርፍ ማደለብ"}
    thumbs = {"01-teff-met": "figures/06_gge_which_won_where.png", "02-goat-breeding-fattening": "figures/07_partial_budget.png"}
    cards = "".join(f'<a class="card" href="{m["url"]}"><img src="{m["url"]}{thumbs.get(m["name"], "")}" alt="">'
                    f'<div class="t"><span class="n">MODULE {i + 1}</span><h2>{html.escape(m["title"].split("·")[-1].strip())}</h2>'
                    f'<h3 lang="am">{am.get(m["name"], "")}</h3><p>{html.escape(m["desc"])}</p></div></a>'
                    for i, m in enumerate(mods))
    stages = [("1 · Know the resources", "Catalogue: 99 livestock breeds and populations of 8 species, and the national crop variety register (scraper included).", True),
              ("2 · Design toolkit", "CRD, RCBD, Latin square, split-plot, alpha-lattice, augmented designs, on-farm trials, power.", False),
              ("3 · Crop breeding", "Multi-location variety trials (Module 1) · germplasm characterisation · participatory selection · seed systems.", True),
              ("4 · Livestock breeding", "Community-based goat breeding and fattening (Module 2) · dairy crossbreeding · village poultry · sheep CBBPs.", True),
              ("5 · Genomics and data", "Genotyping, GWAS and genomic selection with PLINK and R.", False),
              ("6 · The company", "Business models, variety release and protection, finance and pitching.", False)]
    road = "".join(f'<div class="stage{" ready" if r else ""}"><b>{a}</b><span>{b}</span></div>' for a, b, r in stages)
    desc = ("A practical curriculum for African breeders and agri-entrepreneurs: field designs, every ANOVA, G × E, "
            "breeding values and the business that follows. English with Amharic summaries.")
    page = HEAD.format(title="Breed to Business · ከዝርያ እስከ ንግድ", desc=desc, url=SITE,
                       img=f"{SITE}modules/01-teff-met/figures/06_gge_which_won_where.png", css=CSS)
    page += f'''<header class="hero"><div class="wrap"><p class="kicker">Curriculum · ሥርዓተ ትምህርት · Ethiopia and Africa</p>
<h1>Breed to Business<span class="am">ከዝርያ እስከ ንግድ</span></h1>
<p class="dek">Ethiopia's plant and animal genetic resources, from field design to company. Each module starts from a real decision on African land, lays out the trial, runs every analysis, draws the charts you need to decide, and ends with the business the result makes possible.</p>
<p class="dek am-block" lang="am">የኢትዮጵያ የዕፅዋትና የእንስሳት የዘረመል ሀብቶች፣ ከማሳ ዲዛይን እስከ ኩባንያ። እያንዳንዱ ሞጁል በአፍሪካ መሬት ላይ ካለ እውነተኛ ውሳኔ ይጀምራል፣ ሙከራውን ያቅዳል፣ ሁሉንም ትንተና ያካሂዳል፣ ለውሳኔ የሚያስፈልጉ ሥዕሎችን ያዘጋጃል፣ ውጤቱ በሚፈጥረው ንግድ ይደመደማል።</p>
</div></header><main class="wrap">
<h2 style="font:800 26px var(--display);margin-top:30px">Start here: the catalogue</h2>
<a class="card" href="catalogue/" style="grid-template-columns:1fr"><div class="t"><span class="n">CATALOGUE</span><h2>Ethiopia's livestock breeds and crop varieties</h2><h3 lang="am">የኢትዮጵያ የእንስሳትና የሰብል ዝርያዎች</h3><p>Cattle, sheep, goats, chickens, camels, horses, donkeys and honeybees, plus the national Crop Variety Register. Searchable, every entry sourced, downloadable as CSV.</p></div></a>
<h2 style="font:800 26px var(--display);margin-top:30px">Modules ready now</h2><div class="cards">{cards}</div>
<h2 style="font:800 26px var(--display)">The road: from the ground to a company</h2><div class="road">{road}</div>
<p>Everything is reproducible: <code>pip install -r requirements.txt</code>, then <code>python modules/01-teff-met/run.py</code>. Code, field books and data are on <a href="{REPO}">GitHub</a>.</p>
</main>''' + AUTHOR
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)


def catalogue_page():
    cdir = os.path.join(ROOT, "catalogue")
    lv = list(csv.DictReader(open(os.path.join(cdir, "livestock_breeds.csv"), encoding="utf-8")))
    cr = list(csv.DictReader(open(os.path.join(cdir, "crop_varieties.csv"), encoding="utf-8")))
    src = list(csv.DictReader(open(os.path.join(cdir, "sources.csv"), encoding="utf-8")))
    readme = markdown.markdown(open(os.path.join(cdir, "README.md"), encoding="utf-8").read(), extensions=["tables", "fenced_code"])
    readme = re.sub(r'href="(?!http|#)([^"]+)"', lambda m: f'href="{REPO}/blob/main/catalogue/{m.group(1)}"', readme)
    crop_keys = ["crop", "variety", "register_issue", "year_of_release", "altitude_masl", "rainfall_mm", "days_to_maturity",
                 "on_farm_yield_qt_ha", "breeder_maintainer", "seed_color", "pest_reaction", "url"]
    data = json.dumps({"lv": lv, "cr": [{k: r.get(k, "") for k in crop_keys} for r in cr],
                       "src": {x["source_id"]: x["url"] for x in src}}, ensure_ascii=False)
    css = CSS + """
.ctl{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:14px 0}
.ctl input{font:16px var(--body);padding:9px 12px;border:1px solid var(--rule);border-radius:10px;background:var(--panel);color:var(--ink);min-width:260px}
.ctl button{font:600 13.5px var(--display);border:1px solid var(--rule);background:var(--panel);color:var(--ink);padding:8px 12px;border-radius:999px;cursor:pointer}
.ctl button[aria-pressed=true]{background:var(--ink);color:var(--paper)}
.tw{overflow-x:auto;border:1px solid var(--rule);border-radius:12px;background:var(--panel);max-height:70vh}
table.cat{border-collapse:collapse;width:100%;font-size:14.5px}
table.cat th{position:sticky;top:0;background:var(--paper);font:700 12px var(--mono);text-transform:uppercase;color:var(--muted);text-align:left;padding:9px 10px;border-bottom:1px solid var(--rule)}
table.cat td{padding:8px 10px;border-bottom:1px solid var(--rule);vertical-align:top}
table.cat td.b{font-weight:600}
.count{font:600 14px var(--mono);color:var(--copper)}
.stat-row{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}
.stat-row div{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:10px 14px}
.stat-row b{display:block;font:800 26px var(--display);color:var(--copper)}
"""
    from collections import Counter
    cnt = Counter(r["species"] for r in lv)
    stats = "".join(f'<div><b>{n}</b>{k}</div>' for k, n in cnt.items())
    page = HEAD.format(title="Catalogue: Ethiopia's crop varieties and livestock breeds · Breed to Business",
                       desc=f"Searchable catalogue of {len(lv)} Ethiopian livestock breeds and populations and the national crop variety register, each entry with its source.",
                       url=SITE + "catalogue/", img=SITE + "modules/01-teff-met/figures/06_gge_which_won_where.png", css=css)
    page += f"""<header class="hero"><div class="wrap"><a class="home" href="../">← Breed to Business · ከዝርያ እስከ ንግድ</a>
<p class="kicker">Catalogue · ካታሎግ · <a href="{REPO}/tree/main/catalogue">CSV files on GitHub</a></p>
<h1>Ethiopia's livestock breeds and crop varieties<span class="am">የኢትዮጵያ የእንስሳትና የሰብል ዝርያዎች</span></h1>
<p class="dek">Every entry cites its source. Search by name, synonym, region or trait.</p></div></header>
<main class="wrap">
<h2 style="font:800 26px var(--display);margin-top:28px">Livestock breeds and populations · የእንስሳት ዝርያዎች</h2>
<div class="stat-row">{stats}</div>
<div class="ctl" id="lv-ctl"><input id="lv-q" type="search" placeholder="Search breed, synonym, region…" aria-label="Search livestock"><span class="count" id="lv-n"></span></div>
<div class="tw"><table class="cat"><thead><tr><th>Species</th><th>Breed</th><th>Synonyms</th><th>Group</th><th>Region / agro-ecology</th><th>Notes</th><th>Sources</th></tr></thead><tbody id="lv-b"></tbody></table></div>
<h2 style="font:800 26px var(--display);margin-top:40px">Registered crop varieties · የተመዘገቡ የሰብል ዝርያዎች</h2>
<p>From the national Crop Variety Register on the Ministry of Agriculture seed portal. <b>{len(cr)} varieties loaded.</b> The full register (about 1,500 varieties of about 150 crops) loads after running <code>tools/scrape_ethioseed.py</code>.</p>
<div class="ctl" id="cr-ctl"><input id="cr-q" type="search" placeholder="Search crop, variety, breeder, trait…" aria-label="Search crops"><span class="count" id="cr-n"></span></div>
<div class="tw"><table class="cat"><thead><tr><th>Crop</th><th>Variety</th><th>Issue</th><th>Released</th><th>Altitude m</th><th>Rainfall mm</th><th>Maturity days</th><th>On-farm yield qt/ha</th><th>Breeder / maintainer</th><th>Seed colour</th><th>Disease reaction</th></tr></thead><tbody id="cr-b"></tbody></table></div>
<section class="md" style="margin-top:30px">{readme}</section>
</main>
<script>
var D = {data};
function esc(s){{return (s||"").replace(/[&<>"]/g,function(c){{return {{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c];}});}}
function srcLinks(s){{return s.split("; ").map(function(id){{return D.src[id]?'<a href="'+D.src[id]+'">'+id+'</a>':id;}}).join(", ");}}
function setup(kind, rows, keyField, render, cols){{
  var cats=[];rows.forEach(function(r){{if(cats.indexOf(r[keyField])<0)cats.push(r[keyField]);}});
  var ctl=document.getElementById(kind+"-ctl"), cur="all";
  [["all","All · ሁሉም"]].concat(cats.map(function(c){{return [c,c];}})).forEach(function(c){{
    var b=document.createElement("button");b.type="button";b.textContent=c[1];b.setAttribute("aria-pressed",c[0]==="all");
    b.onclick=function(){{cur=c[0];ctl.querySelectorAll("button").forEach(function(x){{x.setAttribute("aria-pressed",x===b);}});draw();}};
    ctl.insertBefore(b,document.getElementById(kind+"-n"));}});
  var q=document.getElementById(kind+"-q");q.oninput=draw;
  function draw(){{var t=q.value.toLowerCase(),out=rows.filter(function(r){{return (cur==="all"||r[keyField]===cur)&&(!t||cols.some(function(k){{return (r[k]||"").toLowerCase().indexOf(t)>=0;}}));}});
    document.getElementById(kind+"-b").innerHTML=out.map(render).join("");document.getElementById(kind+"-n").textContent=out.length+" shown";}}
  draw();
}}
setup("lv",D.lv,"species",function(r){{return "<tr><td>"+esc(r.species)+"</td><td class=b>"+esc(r.breed)+"</td><td>"+esc(r.synonyms)+"</td><td>"+esc(r.breed_group)+"</td><td>"+esc(r.region_agroecology)+"</td><td>"+esc(r.notes)+"</td><td>"+srcLinks(r.sources)+"</td></tr>";}},["breed","synonyms","breed_group","region_agroecology","notes","species"]);
setup("cr",D.cr,"crop",function(r){{return "<tr><td>"+esc(r.crop)+"</td><td class=b><a href=\\""+esc(r.url)+"\\">"+esc(r.variety)+"</a></td><td>"+esc(r.register_issue)+"</td><td>"+esc(r.year_of_release)+"</td><td>"+esc(r.altitude_masl)+"</td><td>"+esc(r.rainfall_mm)+"</td><td>"+esc(r.days_to_maturity)+"</td><td>"+esc(r.on_farm_yield_qt_ha)+"</td><td>"+esc(r.breeder_maintainer)+"</td><td>"+esc(r.seed_color)+"</td><td>"+esc(r.pest_reaction)+"</td></tr>";}},["crop","variety","breeder_maintainer","pest_reaction","year_of_release","register_issue"]);
</script>""" + AUTHOR
    open(os.path.join(cdir, "index.html"), "w", encoding="utf-8").write(page)
    return len(lv), len(cr)


if __name__ == "__main__":
    mods = [module_page(f) for f in sorted(glob.glob(os.path.join(ROOT, "modules", "*"))) if os.path.isdir(f)]
    home(mods)
    print("built", [m["name"] for m in mods], "catalogue", catalogue_page())
