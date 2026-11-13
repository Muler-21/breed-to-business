"""Build the GitHub Pages site: index.html at the root and one page per module,
made from each module's README.md. Run after the module scripts:
    python tools/build_site.py
"""
import os, re, glob, html
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
    stages = [("1 · Know the resources", "Catalogue of Ethiopian crop varieties and livestock breeds, with sources.", False),
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
<h2 style="font:800 26px var(--display);margin-top:30px">Modules ready now</h2><div class="cards">{cards}</div>
<h2 style="font:800 26px var(--display)">The road: from the ground to a company</h2><div class="road">{road}</div>
<p>Everything is reproducible: <code>pip install -r requirements.txt</code>, then <code>python modules/01-teff-met/run.py</code>. Code, field books and data are on <a href="{REPO}">GitHub</a>.</p>
</main>''' + AUTHOR
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)


if __name__ == "__main__":
    mods = [module_page(f) for f in sorted(glob.glob(os.path.join(ROOT, "modules", "*"))) if os.path.isdir(f)]
    home(mods)
    print("built", [m["name"] for m in mods])
