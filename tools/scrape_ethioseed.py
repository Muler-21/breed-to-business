"""Download Ethiopia's registered crop varieties from the Ministry of Agriculture
seed portal (ethioseed.moa.gov.et) into catalogue/crop_varieties.csv.

Run it on your own computer (the portal is public, and it is the online form of
the national Crop Variety Register):

    python tools/scrape_ethioseed.py                  # ids 1..2500
    python tools/scrape_ethioseed.py --start 1 --end 3000 --delay 2

It is polite by design: it reads robots.txt, waits between requests (default
1.5 s), identifies itself, caches every page so a stopped run resumes where it
left off, and never re-downloads a cached page. Only the Python standard
library is used.
"""
import argparse, csv, html, os, re, sys, time, urllib.request, urllib.robotparser, urllib.error

BASE = "https://ethioseed.moa.gov.et"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "catalogue", "_cache_ethioseed")
OUT = os.path.join(ROOT, "catalogue", "crop_varieties.csv")
UA = "breed-to-business catalogue builder (educational; github.com/Muler-21/breed-to-business)"

# (output column, regex for the label as it appears on the page)
FIELDS = [
    ("es_code", r"ES Code"),
    ("variety", r"Registered Variety Name"),
    ("register_issue", r"(?:Variety )?Released in Issue No\.?"),
    ("common_name", r"Common Name"),
    ("scientific_name_or_pedigree", r"Scientific Name"),
    ("released_for", r"Released For \(yield, drought, pest resistance\.\.\.\)"),
    ("adaptation_area", r"Adaptation Area"),
    ("altitude_masl", r"Altitude \(m\.a\.s\.l\)"),
    ("rainfall_mm", r"Rainfall \(mm\)"),
    ("soil_type", r"Soil Type"),
    ("nutritional_merit", r"Nutritional Merit"),
    ("year_of_release", r"Year of Release"),
    ("breeder_maintainer", r"Breeder Seed Maintainer"),
    ("planting_method", r"Planting Method"),
    ("seed_rate_kg_ha", r"Seed Rate \(kg/ha\)"),
    ("planting_dates", r"Planting Dates"),
    ("p2o5_kg_ha", r"P2O5 Fertilizer Rate \(kg/ha\)"),
    ("n_kg_ha", r"N Fertilizer Rate \(kg/ha\)"),
    ("days_to_heading", r"Days to (?:heading/Flowering|Heading)"),
    ("days_to_maturity", r"Days to Maturity"),
    ("panicle_length_cm", r"Panicle Length \(cm\)"),
    ("thousand_seed_weight_g", r"1000 Seed Weight \(g\)"),
    ("seed_color", r"Seed Color"),
    ("flower_color", r"Flower Color"),
    ("leaf_arrangement", r"Leaf Arrangement"),
    ("pest_reaction", r"Crop Pest Reaction"),
    ("on_farm_yield_qt_ha", r"On Farm Yield Amount \(qt/ha\)"),
    ("on_station_yield_qt_ha", r"On station Yield Amount \(qt/ha\)"),
    ("status", r"Variety (?:Maintenance )?Status"),
    ("source_type", r"Variety Source"),
    ("date_added", r"date added"),
]
STOP = r"(?:date modified|National .{0,120}?Breeder Seed Stock|Data is for current budget year|Variety Image|seed \d+\b)"
COLUMNS = ["portal_id", "crop"] + [c for c, _ in FIELDS] + ["url"]


def page_text(raw):
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|td|th|li|h\d|dt|dd|span|label)>", "\n", raw)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"[ \t\r\f\v]+", " ", txt)


def parse(txt):
    """Find each label and take the text up to the next known label."""
    labels = [(c, re.compile(r"(?<![A-Za-z])" + rx + r"\s*:?", re.I)) for c, rx in FIELDS]
    hits = []
    for c, rx in labels:
        m = rx.search(txt)
        if m:
            hits.append((m.start(), m.end(), c))
    hits.sort()
    stop = re.compile(STOP, re.I)
    rec = {}
    for i, (s, e, c) in enumerate(hits):
        nxt = hits[i + 1][0] if i + 1 < len(hits) else len(txt)
        seg = txt[e:nxt]
        m = stop.search(seg)
        if m:
            seg = seg[:m.start()]
        val = re.sub(r"\s+", " ", seg).strip(" :\n")
        rec[c] = "" if val.lower() in ("none", "-", "non", "") else val
    cn = rec.get("common_name", "")
    rec["crop"] = cn.split(" - ")[0].strip() if " - " in cn else ""
    return rec


def fetch(i, delay, rp):
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, f"{i}.html")
    if os.path.exists(fn):
        return open(fn, encoding="utf-8", errors="replace").read()
    url = f"{BASE}/seed-variety-details/{i}/"
    if rp and not rp.can_fetch(UA, url):
        print("robots.txt disallows", url); return None
    time.sleep(delay)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            open(fn, "w").write("")   # remember missing ids
            return ""
        print(i, "HTTP", e.code); return None
    except Exception as e:
        print(i, "error", e); return None
    open(fn, "w", encoding="utf-8").write(raw)
    return raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=2500)
    ap.add_argument("--delay", type=float, default=1.5)
    ap.add_argument("--stop-after-missing", type=int, default=300, help="stop after this many empty ids in a row")
    a = ap.parse_args()
    rp = urllib.robotparser.RobotFileParser(BASE + "/robots.txt")
    try:
        rp.read()
    except Exception:
        rp = None
    rows, missing = [], 0
    for i in range(a.start, a.end + 1):
        raw = fetch(i, a.delay, rp)
        if not raw or "Registered Variety Name" not in raw:
            missing += 1
            if missing >= a.stop_after_missing:
                print("stopping: no varieties in the last", missing, "ids"); break
            continue
        missing = 0
        rec = parse(page_text(raw))
        rec["portal_id"] = i
        rec["url"] = f"{BASE}/seed-variety-details/{i}/"
        rows.append(rec)
        if len(rows) % 50 == 0:
            print(len(rows), "varieties so far (id", i, ")")
    if not rows:
        print("No variety pages could be fetched: the portal may be unreachable from this network.",
              "The existing", OUT, "was left unchanged.")
        return 1
    # merge with what is already in the table, so a partial run never deletes verified records
    old = {}
    if os.path.exists(OUT):
        for r in csv.DictReader(open(OUT, encoding="utf-8")):
            old[str(r.get("portal_id"))] = r
    for r in rows:
        old[str(r["portal_id"])] = r
    merged = sorted(old.values(), key=lambda r: int(r["portal_id"]))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader(); w.writerows(merged)
    print("wrote", OUT, len(merged), "varieties (", len(rows), "fetched in this run )")
    return 0

if __name__ == "__main__":
    sys.exit(main())
