"""Builds the FuelStorageGuide.com static site into ./site"""
import hashlib
import json
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent / "tools"))
from diagrams import WATER_TANK_SVG, TRANSFER_RULE_SVG
from diagrams2 import OVERFILL_SVG, ASV_SVG, LLD_SVG, NOZZLE_SVG, SPILL_SVG
from pathlib import Path

SITE = Path(__file__).parent / "site"
DOMAIN = "https://fuelstorageguide.com"
UPDATED = "2026-10-28"
UPDATED_HUMAN = "October 28, 2026"
# Pages first published after the launch date: (ISO date, human date)
DATES = {
    "/how-long-does-diesel-last/": ("2026-10-29", "October 29, 2026"),
    "/fuel-quality/": ("2026-10-29", "October 29, 2026"),
    "/anti-siphon-valve/": ("2026-10-30", "October 30, 2026"),
    "/aboveground-fuel-tanks/": ("2026-10-30", "October 30, 2026"),
    "/spill-bucket-testing/": ("2026-10-30", "October 30, 2026"),
    "/line-leak-detector/": ("2026-10-30", "October 30, 2026"),
    "/ust-overfill-prevention/": ("2026-10-30", "October 30, 2026"),
    "/underground-storage-tanks/": ("2026-10-30", "October 30, 2026"),
    "/fuel-nozzle/": ("2026-10-30", "October 30, 2026"),
    "/fuel-tank-secondary-containment/": ("2026-10-31", "October 31, 2026"),
    "/ust-walkthrough-inspection/": ("2026-10-31", "October 31, 2026"),
    "/test-diesel-fuel-quality/": ("2026-10-31", "October 31, 2026"),
    "/diesel-tank-cleaning/": ("2026-10-31", "October 31, 2026"),
    "/diesel-fuel-stabilizer/": ("2026-10-31", "October 31, 2026"),
}

# Who gets credit in bylines and structured data. While this is None, guides are credited
# to the site itself. Set it to the technician's real name to switch to a named Person author.
AUTHOR_NAME = "Austin"

ORG_ID = DOMAIN + "/#organization"
ORG = {
    "@type": "Organization", "@id": ORG_ID, "name": "FuelStorageGuide", "url": DOMAIN + "/",
    "logo": {"@type": "ImageObject", "url": DOMAIN + "/logo.png", "width": 512, "height": 512},
    "description": "Practical, sourced guides for farms, contractors, and fleets that store their own fuel, "
                   "written by a working fuel-system technician.",
}
if AUTHOR_NAME:
    AUTHOR = {"@type": "Person", "@id": DOMAIN + "/about/#author", "name": AUTHOR_NAME,
              "jobTitle": "Fuel-system technician", "url": DOMAIN + "/about/", "worksFor": {"@id": ORG_ID}}
else:
    AUTHOR = ORG

# Changes whenever styles.css changes, so the stylesheet can be cached for a year.
CSS_VERSION = hashlib.sha256((SITE / "styles.css").read_bytes()).hexdigest()[:10]

CRC = "https://crcao.org/wp-content/uploads/2019/05/CRC-671.pdf"
CENEX = "https://www.cenex.com/expert-advice-and-insights/Diesel-Gelling-and-How-to-Stop-It-This-Winter"
EPRI = "https://restservice.epri.com/publicdownload/TR-104843/0/Product"
GOLD = "https://www.goldeagle.com/tips-tools/signs-winter-fuel-trouble-five-things-be-aware-diesel-tanks/"
FILLRITE = "https://www.fillrite.com/filters-series-filters"
POWER = "https://powerservice.com/wp-content/uploads/2022/01/PSP1-26415-Diesel-911-Learning-Center-Website-Article-2.pdf"


def src(url, label):
    return f'(<a href="{url}" rel="noopener">{label}</a>)'


AMAZON_TAG = "fuelstoragegu-20"
def amz(query, label):
    from urllib.parse import quote_plus
    url = f"https://www.amazon.com/s?k={quote_plus(query)}&tag={AMAZON_TAG}"
    return f'<a href="{url}" rel="sponsored nofollow noopener" target="_blank">{label}</a>'

AFF_NOTE = ('<p class="aff-note">This guide has affiliate links. As an Amazon Associate, FuelStorageGuide earns from qualifying purchases, '
            'at no extra cost to you. <a href="/affiliate-disclosure/">How we pick products</a>.</p>')


NAV = [("/fuel-quality/", "Fuel quality"), ("/aboveground-fuel-tanks/", "Aboveground tanks"),
       ("/underground-storage-tanks/", "Underground tanks"), ("/about/", "About")]

# Pages are collected here and written at the end of the build, once every topic hub's
# guide list exists (articles use those lists for their "related guides" box).
PAGES = []


def page(path, title, description, body, current=None, schema=None, og_type="website"):
    PAGES.append((path, title, description, body, current, schema, og_type))


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", strip_tags(text).lower()).strip("-")


AUTHOR_BOX = """
  <aside class="author-box" aria-label="About the author">
    <div class="author-badge" aria-hidden="true"><svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="19" fill="#1d6a48"/><path d="M25.5 10.5a5.5 5.5 0 0 0-6.9 6.9l-7.4 7.4a2.1 2.1 0 0 0 3 3l7.4-7.4a5.5 5.5 0 0 0 6.9-6.9l-3.2 3.2-2.9-.6-.6-2.9z" fill="#f0c02b"/></svg></div>
    <div>
      <p class="label">Who writes these guides</p>
      <p>Austin, a working fuel-system technician with eight years in the trade: inspecting and servicing underground and aboveground tanks, dispensers, piping, valves, leak detectors, and aviation fuel systems. Every number on this page links to its source, and anything that differs in the field gets called out. <a href="/about/">More about the site</a>.</p>
    </div>
  </aside>
"""


def enhance_article(body, path):
    """Adds heading anchors, an on-this-page list, the author box, and related guides to an article."""
    hubs = {FQ_PATH: ("Fuel quality", FQ_GUIDES), AST_PATH: ("Aboveground tanks", AST_GUIDES),
            UST_PATH: ("Underground tanks", UST_GUIDES)}
    toc = []

    def anchor(m):
        attrs, text = m.group(1), m.group(2)
        if "id=" in attrs:
            hid = re.search(r'id="([^"]+)"', attrs).group(1)
        else:
            hid = slugify(text)
            attrs += f' id="{hid}"'
        toc.append((hid, strip_tags(text)))
        return f"<h2{attrs}>{text}</h2>"

    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", anchor, body)
    links = "".join(f'<li><a href="#{h}">{t}</a></li>' for h, t in toc)
    toc_inline = f'<details class="toc toc-inline"><summary>On this page</summary><ol>{links}</ol></details>'
    # Inline list goes right after the answer box (or the opening paragraph when there isn't one).
    if '<div class="answer">' in body:
        i = body.index("</div>", body.index('<div class="answer">')) + len("</div>")
    else:
        i = body.index("</p>", body.index('class="meta"')) + len("</p>")
    body = body[:i] + "\n  " + toc_inline + body[i:]
    # Lead with the answer: the affiliate note moves below the answer box, still above the first product link
    if AFF_NOTE in body and '<div class="answer">' in body:
        body = body.replace(AFF_NOTE, "", 1)
        i = body.index("</div>", body.index('<div class="answer">')) + len("</div>")
        body = body[:i] + "\n  " + AFF_NOTE + body[i:]
    # Byline
    who = f"By {AUTHOR_NAME}, fuel-system technician" if AUTHOR_NAME else "By a fuel-system technician"
    body = re.sub(r'<p class="meta">Written by a fuel-system technician\. (Updated [^<]+)</p>',
                  rf'<p class="meta byline"><span class="byline-who">{who}</span>'
                  r'<span class="byline-sep" aria-hidden="true">/</span><span>8 years in the trade</span>'
                  r'<span class="byline-sep" aria-hidden="true">/</span><span>\1</span></p>', body)
    # Author box before the sources list
    body = body.replace("<h2 id=\"sources\">Sources</h2>", AUTHOR_BOX + "\n  <h2 id=\"sources\">Sources</h2>", 1)
    if AUTHOR_BOX not in body:
        body = body.replace("</article>", AUTHOR_BOX + "</article>", 1)
    # Related guides from the same topic hub
    related = ""
    m = re.search(r'<p class="crumbs"><a href="([^"]+)">', body)
    if m and m.group(1) in hubs:
        hub_path = m.group(1)
        name, guides = hubs[hub_path]
        # The three guides after this one in the hub's list (wrapping), so every guide gets linked
        idx = next((n for n, g in enumerate(guides) if g[0] == path), -1)
        picks = [guides[(idx + k) % len(guides)] for k in range(1, len(guides))][:3]
        cards = "".join(f'<li><a class="guide" href="{p}"><span class="card-title">{t}</span><p>{d}</p></a></li>'
                        for p, t, d in picks)
        related = (f'<section class="related" aria-labelledby="related-title"><div class="related-inner">'
                   f'<p class="label">Keep reading</p><h2 id="related-title">More {name.lower()} guides</h2>'
                   f'<ul class="guide-list related-list">{cards}</ul>'
                   f'<p><a class="more-link" href="{hub_path}">All {name.lower()} guides</a></p></div></section>')
    aside = f'<aside class="toc-side" aria-label="On this page"><nav class="toc"><p class="label">On this page</p><ol>{links}</ol></nav></aside>'
    return f'<div class="article-layout">{body}{aside}</div>{related}'


def render(path, title, description, body, current=None, schema=None, og_type="website"):
    canonical = DOMAIN + path
    if body.lstrip().startswith("<article"):
        body = enhance_article(body, path)
        hub = re.search(r'<p class="crumbs"><a href="([^"]+)">', body)
        current = current or (hub.group(1) if hub else None)
    if path in DATES:
        iso, human = DATES[path]
        body = body.replace(f"Updated {UPDATED_HUMAN}.", f"Updated {human}.")
        if schema:
            schema = json.loads(json.dumps(schema).replace(f'"{UPDATED}"', f'"{iso}"'))
    m = re.search(r'<p class="crumbs"><a href="([^"]+)">([^<]+)</a></p>', body)
    if m:
        h1 = re.search(r"<h1>(.*?)</h1>", body)
        crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": m.group(2), "item": DOMAIN + m.group(1)},
            {"@type": "ListItem", "position": 3, "name": strip_tags(h1.group(1)) if h1 else title, "item": canonical}]}
        schema = (schema or []) + [crumbs]
    elif schema and any(s.get("@type") == "CollectionPage" for s in schema):
        crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": strip_tags(title.split(":")[0]), "item": canonical}]}
        schema = schema + [crumbs]
    slug = path.strip("/").replace(".html", "") or "home"
    og_file = SITE / "og" / f"{slug}.png"
    og_image = f"{DOMAIN}/og/{slug}.png" if og_file.exists() else f"{DOMAIN}/og/home.png"
    if schema:
        # Every article points at the shared site and author entities and carries its share image
        schema = [dict(s, **{"@id": s.get("@id", canonical + "#article"), "author": AUTHOR,
                             "publisher": ORG, "image": og_image})
                  if s.get("@type") == "Article" else s for s in schema]
    # Quotes inside attribute values would cut the value short (e.g. 'Diesel "algae" is...')
    attr_title, attr_desc = title.replace('"', "&quot;"), description.replace('"', "&quot;")
    if current is None and any(path == h for h, _ in NAV):
        current = path
    nav = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>'
        for href, label in NAV
    )
    schema_tag = ""
    if schema:
        schema_tag = "\n".join(
            f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'
            for s in schema
        )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{attr_desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{attr_title}">
<meta property="og:description" content="{attr_desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="FuelStorageGuide">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og_image}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/barlow-condensed-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/source-serif-4-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css?v={CSS_VERSION}">
{schema_tag}
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="site-header">
  <div class="hazard" aria-hidden="true"></div>
  <div class="header-inner">
    <a class="wordmark" href="/" aria-label="FuelStorageGuide home"><span class="wm-fuel">Fuel</span><span>StorageGuide</span></a>
    <nav class="site-nav" aria-label="Main">{nav}</nav>
  </div>
</header>
<main id="content">
{body}
</main>
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <a class="wordmark" href="/" aria-label="FuelStorageGuide home"><span class="wm-fuel">Fuel</span><span>StorageGuide</span></a>
      <p>Practical guidance on stored fuel, written by a working fuel-system technician. As an Amazon Associate, we earn from qualifying purchases.</p>
    </div>
    <nav aria-label="Footer">
      <a href="/fuel-quality/">Fuel quality</a>
      <a href="/aboveground-fuel-tanks/">Aboveground tanks</a>
      <a href="/underground-storage-tanks/">Underground tanks</a>
      <a href="/about/">About</a>
      <a href="/contact/">Contact</a>
      <a href="/privacy/">Privacy</a>
      <a href="/affiliate-disclosure/">Affiliate disclosure</a>
    </nav>
  </div>
</footer>
</body>
</html>
"""
    out = SITE / path.lstrip("/") / "index.html" if path.endswith("/") else SITE / path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


# ---------------- Article: diesel gelling ----------------
GEL_PATH = "/diesel-gelling-temperature/"
ADD_PATH = "/winter-diesel-additive/"
BIO_PATH = "/diesel-biocide/"
GEL_TITLE = "Diesel Gelling Temperature: When It Happens and How to Prevent It"
GEL_DESC = ("#2 diesel starts clouding around 10–20°F. Here's when it gels, why bulk tanks "
            "are at higher risk, and how to keep your stored diesel flowing all winter.")

faq = [
    ("At what temperature does diesel gel?",
     f"Untreated #2 diesel usually starts clouding somewhere around 10–20°F, depending on the batch; some fuels cloud as high as +20°F {src(GOLD, 'Gold Eagle')}. Without additives, filters can plug close to that temperature, long before the fuel stops pouring."),
    ("Does #1 diesel gel?",
     f"Much later. #1 has very little wax. In one EPRI example, a #1 fuel had a cloud point of −26°F, compared with +12°F for the #2 it was blended with {src(EPRI, 'EPRI')}."),
    ("Can I add anti-gel after the fuel has gelled?",
     "Not regular anti-gel. It only works when mixed in above the cloud point. Use a product made for gelled fuel, and warm the filter and lines."),
    ("Does red (off-road) diesel gel differently?",
     f"The red dye marks fuel for tax purposes {src(EPRI, 'EPRI')}. Cold behavior comes from the grade and whether the fuel was winterized or blended, so ask your supplier the same questions for off-road fuel."),
]

faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in faq)

import re
def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).replace("  ", " ").strip()

gel_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/fuel-quality/">Fuel quality</a></p>
  <h1>Diesel gelling: when it happens and how to prevent it</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>
  {AFF_NOTE}

  <div class="answer">
    <p><strong>Untreated #2 diesel starts to cloud around 14°F and can plug a fuel filter within a few degrees of that.</strong> It doesn't need to freeze solid to stop you. Wax crystals catch on the filter long before the fuel stops pouring.</p>
  </div>

  <p>If you store diesel in a farm tank, skid tank, or transfer tank, you're at more risk than someone fueling at a truck stop. The fuel in your tank is whatever was delivered, and a load bought in September is usually summer-grade #2 with no winter treatment. This guide covers when gelling happens, why bulk tanks are different, and what to do before the first cold snap.</p>

  <h2>Cloud point, CFPP, and pour point</h2>
  <p><strong>The number that matters for a fuel tank is the cloud point, not the "freezing" point.</strong> #2 diesel contains paraffin wax. As it cools, the wax forms crystals, and three temperatures describe how bad it gets.</p>

  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Stage</th><th scope="col">What happens</th><th scope="col">Typical untreated #2 diesel</th></tr></thead>
    <tbody>
      <tr><td>Cloud point</td><td>Wax crystals first appear; fuel looks hazy</td><td>About 14°F {src(CENEX, 'Cenex')}. Major U.S. pipelines cap winter diesel at 15°F and summer diesel at 20°F {src(CRC, 'CRC')}</td></tr>
      <tr><td>Cold filter plugging point (CFPP)</td><td>Crystals build up fast enough to block a 45-micron test screen</td><td>Near the cloud point when no additive is used {src(CRC, 'CRC')}</td></tr>
      <tr><td>Pour point</td><td>Fuel gels and stops pouring</td><td>Lower still, but it says little about when equipment quits; pipelines cap winter diesel at 0°F {src(CRC, 'CRC')}</td></tr>
    </tbody>
  </table>
  </div>

  <p>Two things trip people up:</p>
  <ul>
    <li><strong>Your filters are finer than the test screen.</strong> CFPP is measured with a 45-micron screen. Fill-Rite's standard transfer pump filters are 10 micron, with 30- and 2-micron options {src(FILLRITE, 'Fill-Rite')}, and engine fuel filters run from about 20 microns down to 2 {src(CRC, 'CRC')}. Finer filters can plug at a warmer temperature than the fuel's rated CFPP.</li>
    <li><strong>You can't change the cloud point with a bottle.</strong> Most anti-gel additives lower the cloud point only 1–3°C, if at all. They work by changing the size and shape of the wax crystals so fuel keeps passing through the filter {src(CRC, 'CRC')}. Blending in #1 diesel, which has much less wax, is what actually lowers the cloud point.</li>
  </ul>

  <h2>Why bulk tanks gel before vehicles do</h2>
  <p><strong>A storage tank sits outside, holds fuel bought months ago, and pushes it through a cold filter with nothing warming it up.</strong> A running engine recirculates warm fuel; a farm tank doesn't.</p>
  <ul>
    <li><strong>Small tanks cool down fast.</strong> Industry guidance says tanks under 30,000 gallons can produce a lot of wax just from normal day-night temperature swings. For aboveground farm tanks, it recommends blending and additives that bring the cloud point below your expected lows {src(CRC, 'CRC')}.</li>
    <li><strong>The fuel may be summer grade.</strong> Fuel is blended for the season it's sold in. Diesel bought in summer or early fall won't have the cloud point of fuel made for January {src(EPRI, 'EPRI')}. ASTM's monthly low-temperature tables are guidance, not a legal requirement, and cold performance is something you agree on with your supplier {src(CRC, 'CRC')}.</li>
    <li><strong>Lines and filters gel first.</strong> Hoses, pipes, and filters hold little fuel and cool faster than the tank. Fuel can gel in the line or filter while the tank is still liquid {src(CRC, 'CRC')}.</li>
    <li><strong>Water turns to ice.</strong> Ice can block a tank outlet or a dispenser filter, and aboveground tanks are especially vulnerable. Ice and wax plugs look the same, and sometimes it's both {src(CRC, 'CRC')}.</li>
    <li><strong>Wax can settle.</strong> Fuel stored below its cloud point can separate into a waxy bottom layer and a thinner top layer, so what comes out of the tank changes as the level drops {src(CRC, 'CRC')}.</li>
    <li><strong>Topping off changes the mix.</strong> Adding winter fuel to a half-full tank of summer fuel gives you something in between, and dilutes any additive {src(EPRI, 'EPRI')}.</li>
  </ul>

  <h2>How to keep stored diesel from gelling</h2>
  <p><strong>Treat or blend the fuel before it gets cold, and keep water out of the tank.</strong> Additives can't undo wax that has already formed, so timing matters more than which brand you buy.</p>
  <ol>
    <li><strong>Order winter fuel for winter.</strong> Ask your supplier whether deliveries from late fall on are winterized or blended, and what cloud point they're treated to. If you still have summer fuel in the tank, plan to treat it.</li>
    <li><strong>Add anti-gel while the fuel is still warm</strong> (more in <a href="{ADD_PATH}">winter diesel additives</a>). Anti-gel has to be in the fuel before wax starts forming, because part of the additive works by joining the first wax crystals as they form {src(CRC, 'CRC')}. Additive makers say the same: add it before the fuel reaches its cloud point {src(GOLD, 'Gold Eagle')}. The easiest way is to pour it in right before a delivery so the incoming fuel mixes it. Cenex puts the typical limit of these additives at about 0°F {src(CENEX, 'Cenex')}.</li>
    <li><strong>Blend in #1 diesel as it gets colder.</strong> Cenex's schedule: below 35°F, about 70% #2 and 30% #1 plus an anti-gel; deeper into winter, 30% #2 and 70% #1; below −30°F, straight #1 {src(CENEX, 'Cenex')}.</li>
    <li><strong>Get the water out before winter.</strong> Check the tank bottom with water-finding paste, drain or pump off any water, and change the dispenser filter in the fall. Routinely draining water bottoms is the best defense against ice {src(CRC, 'CRC')}. A desiccant breather on the vent cuts down on condensation.</li>
    <li><strong>Protect the filter and short lines.</strong> Insulation and heat tracing work well on short runs of ¼″ to 1″ line, and a filter heater protects the weakest point {src(CRC, 'CRC')}. Never bypass or remove the filter to keep fuel moving; that sends dirt straight to your engines.</li>
    <li><strong>Don't add gasoline.</strong> It lowers the flash point and creates a fire hazard in the tank. Use #1 diesel or a kerosene-type fuel for blending instead {src(EPRI, 'EPRI')}.</li>
  </ol>

  <h2>If your fuel already gelled</h2>
  <p><strong>Start with the filter, warm what you can safely, and don't count on a regular anti-gel to fix it.</strong> Most of the time the tank is cloudy but the filter is what's actually blocked.</p>
  <ul>
    <li><strong>Swap the dispenser filter first.</strong> A plugged filter is often packed with wax or ice. Replace it with a fresh one and watch whether it plugs again {src(CRC, 'CRC')}. Don't run without a filter.</li>
    <li><strong>Use a product made for gelled fuel.</strong> Regular anti-gel is a preventive and won't fix wax that has already formed. Emergency products such as Power Service Diesel 9-1-1 are made to reliquefy gelled fuel and de-ice frozen filters. Follow the label, then treat the fuel with an anti-gel so it doesn't gel again {src(POWER, 'Power Service')}.</li>
    <li><strong>Warm safely.</strong> Use a heated building, a tank or filter heater, or heat tracing. Never use an open flame or torch on a tank, pump, or fuel line.</li>
    <li><strong>Let the tank come back above the cloud point before trusting it.</strong> Wax that settled to the bottom leaves the fuel uneven until it redissolves {src(CRC, 'CRC')}.</li>
    <li><strong>Then fix the cause.</strong> Once it's flowing, treat or blend the fuel so it doesn't happen on the next cold night.</li>
  </ul>

  <h2>What to keep on hand</h2>
  <ul>
    <li>Anti-gel additive for diesel, added before the cold: {amz("diesel anti gel additive", "anti-gel on Amazon")}</li>
    <li>An emergency re-liquefier for fuel that already gelled: {amz("Power Service Diesel 9-1-1", "Power Service Diesel 9-1-1 on Amazon")}</li>
    <li>A spare dispenser filter: {amz("Fill-Rite 10 micron fuel filter", "Fill-Rite filters on Amazon")}</li>
    <li>Water-finding paste, to check for water before winter: {amz("Kolor Kut water finding paste", "Kolor Kut paste on Amazon")}</li>
  </ul>

  <h2>Winter checklist for tank owners</h2>
  <p>Do these before overnight lows reach the mid-30s:</p>
  <ul class="checklist">
    <li>Check the tank bottom for water with water-finding paste and remove any you find</li>
    <li>Change the dispenser filter</li>
    <li>Ask your supplier whether upcoming deliveries are winterized or blended, and to what cloud point</li>
    <li>Add anti-gel to any summer fuel still in the tank, before it gets cold</li>
    <li>Keep a spare filter and an emergency re-liquefier on hand</li>
    <li>Check that the vent cap and fill cap seal, so snow and rain stay out</li>
    <li>Plan when you'll switch to a #1 blend as temperatures drop</li>
  </ul>

  <section class="faq">
  <h2>FAQ</h2>
  {faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{CRC}" rel="noopener">Coordinating Research Council: Diesel Fuel Low Temperature Operability Guide (CRC Report 671, 2016)</a></li>
    <li><a href="{CENEX}" rel="noopener">Cenex: Diesel gelling and how to stop it this winter</a></li>
    <li><a href="{EPRI}" rel="noopener">EPRI / Southwest Research Institute: Winterizing Diesel Fuel (TR-104843, 1994)</a></li>
    <li><a href="{GOLD}" rel="noopener">Gold Eagle: Five things to be aware of with diesel fuel tanks</a></li>
    <li><a href="{FILLRITE}" rel="noopener">Fill-Rite: Fuel transfer filters</a></li>
    <li><a href="{POWER}" rel="noopener">Power Service: Diesel 9-1-1</a></li>
  </ul>
  <p class="note">This guide is general information. Follow your equipment manufacturer's instructions and product labels, and check with your fuel supplier about the fuel you actually have.</p>
</article>
"""

gel_schema = [
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": GEL_TITLE,
        "description": GEL_DESC,
        "datePublished": UPDATED,
        "dateModified": UPDATED,
        "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
        "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
        "mainEntityOfPage": DOMAIN + GEL_PATH,
    },
    {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in faq
        ],
    },
]

page(GEL_PATH, GEL_TITLE, GEL_DESC, gel_body, schema=gel_schema, og_type="article")

# ---------------- Article: SPCC ----------------
ECFR = "https://www.ecfr.gov/current/title-40/chapter-I/subchapter-D/part-112"
C1121 = "https://www.law.cornell.edu/cfr/text/40/112.1"
C1122 = "https://www.law.cornell.edu/cfr/text/40/112.2"
WRRDA = "https://www.epa.gov/sites/production/files/2015-06/documents/final_wrrda_fact_sheet_4-24-15.pdf"
STUDY = "https://www.epa.gov/sites/default/files/2016-02/documents/wrrda_farm_study_2015-06-30.pdf"
BASICS = "https://www.epa.gov/sites/default/files/2014-05/documents/spcc_basics.pdf"
TIERS = "https://epa.gov/oil-spills-prevention-and-preparedness-regulations/difference-between-spcc-tier-i-and-tier-ii"
FARMFAQ = "https://www.epa.gov/node/34641"
HRPT = "https://www.govinfo.gov/content/pkg/CRPT-119hrpt180/pdf/CRPT-119hrpt180.pdf"
BDLAW = "https://www.bdlaw.com/publications/house-approves-sweeping-clean-water-act-reforms/"
LEGIS = "https://legislate.dev/bills/119/hr-3898"
SD = "https://danr.sd.gov/Agriculture/Inspection/StorageTanks/SPCCFarmTanks.aspx"
CA = "https://osfm.fire.ca.gov/what-we-do/pipeline-safety-and-cupa/certified-unified-program-agency/aboveground-petroleum-storage-act/farms"
MN = "https://www.pca.state.mn.us/waste/aboveground-storage-tank-systems"
MI = "https://www.michigan.gov/documents/deq/wrd-policy-036-part-5-rules-oil_454799_7.pdf"

SPCC_PATH = "/do-i-need-an-spcc-plan/"
SC_PATH = "/fuel-tank-secondary-containment/"
SPCC_TITLE = "Do I Need an SPCC Plan? A Plain-English Guide for Farms and Small Businesses"
SPCC_DESC = ("If you store more than 1,320 gallons of oil aboveground and a spill could reach water, "
             "you probably need an SPCC plan. Check your site in a minute, with the farm rules included.")

spcc_faq = [
    ("Do I send my SPCC plan to EPA?",
     f"No. You keep it at the site if it's attended at least four hours a day, and make it available if EPA asks to review it {src(ECFR, '40 CFR 112.3(e)')}. Some states, such as Michigan, can also ask for a copy."),
    ("Does a double-walled tank mean I don't need a plan?",
     "No. A double-walled tank still counts toward your capacity. It can help meet the containment requirement, but the rest of the plan still applies."),
    ("Can I write the plan myself?",
     f"If you have 10,000 gallons or less, no single container over 5,000 gallons, and no reportable spill history, you can use EPA's Tier I template and sign it yourself {src(ECFR, '40 CFR 112.6')}. Farms between 6,000 and 20,000 gallons with no tank over 10,000 gallons and no spill history can also self-certify {src(WRRDA, 'EPA WRRDA fact sheet')}."),
    ("Does vegetable oil count?",
     f"Yes. Vegetable oils and animal fats count as oil under the rule {src(C1122, '40 CFR 112.2')}."),
]
spcc_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in spcc_faq)

checker = """
<section class="checker" aria-labelledby="checker-title">
  <h2 id="checker-title">Check your site</h2>
  <p>Answer five questions. This covers the federal rule for aboveground storage only. Read the steps below to count your capacity correctly.</p>
  <form id="spcc-check" novalidate>
    <fieldset>
      <legend>Is this a farm?</legend>
      <p class="hint">Land used to grow crops or raise animals that sells at least $1,000 of farm products a year.</p>
      <label><input type="radio" name="farm" value="yes"> Yes</label>
      <label><input type="radio" name="farm" value="no"> No</label>
    </fieldset>
    <div class="field">
      <label for="cap">Total aboveground capacity, in gallons</label>
      <p class="hint" id="cap-hint">Add the sizes of every oil container 55 gallons or larger, full or not.</p>
      <input id="cap" name="cap" type="number" inputmode="numeric" min="0" step="1" aria-describedby="cap-hint">
    </div>
    <div class="field">
      <label for="big">Largest single container, in gallons</label>
      <input id="big" name="big" type="number" inputmode="numeric" min="0" step="1">
    </div>
    <fieldset>
      <legend>Could a spill reach a creek, river, lake, wetland, or a ditch or drain that leads to one?</legend>
      <p class="hint">Decide as if your dike or containment weren't there.</p>
      <label><input type="radio" name="water" value="yes"> Yes</label>
      <label><input type="radio" name="water" value="no"> No</label>
      <label><input type="radio" name="water" value="unsure"> Not sure</label>
    </fieldset>
    <fieldset>
      <legend>In the last three years, any spill to water over 1,000 gallons, or two over 42 gallons within 12 months?</legend>
      <label><input type="radio" name="hist" value="yes"> Yes</label>
      <label><input type="radio" name="hist" value="no"> No</label>
    </fieldset>
    <button class="btn" type="submit">Check my site</button>
  </form>
  <div id="spcc-result" class="result" role="status" aria-live="polite" hidden></div>
</section>
<script>
(function () {
  var form = document.getElementById('spcc-check');
  var out = document.getElementById('spcc-result');
  function val(n) { var el = form.querySelector('input[name="' + n + '"]:checked'); return el ? el.value : null; }
  function show(title, body, kind) {
    out.hidden = false;
    out.className = 'result ' + kind;
    out.innerHTML = '<p class="result-title">' + title + '</p><p>' + body + '</p>';
    out.focus && out.focus();
  }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var farm = val('farm'), water = val('water'), hist = val('hist');
    var cap = parseFloat(form.cap.value), big = parseFloat(form.big.value);
    if (!farm || !water || !hist || isNaN(cap) || isNaN(big)) {
      show('Answer all five questions', 'Fill in each question above, then check again.', 'warn'); return;
    }
    if (big > cap) {
      show('Check your numbers', 'The largest container can\\'t be bigger than your total capacity.', 'warn'); return;
    }
    var state = ' Your state may still have its own tank rules.';
    if (water === 'no') {
      show('No federal SPCC plan needed', 'If a spill truly couldn\\'t reach water, the federal rule doesn\\'t require a plan. Write down how you decided, and clean up any spill.' + state, 'ok'); return;
    }
    var note = water === 'unsure' ? ' Because you weren\\'t sure a spill couldn\\'t reach water, this assumes it could.' : '';
    var tag, title, body;
    if (farm === 'yes') {
      if (cap < 2500) { title = 'No federal SPCC plan needed'; body = 'Farms under 2,500 gallons are exempt.'; tag = 'ok'; }
      else if (hist === 'no' && cap <= 6000) { title = 'No federal SPCC plan needed'; body = 'Farms from 2,500 to 6,000 gallons with no reportable spill history are exempt.'; tag = 'ok'; }
      else if (hist === 'no' && cap < 20000 && big <= 10000) { title = 'You need a plan, and you can self-certify it'; body = 'Farms over 6,000 and under 20,000 gallons, with no tank over 10,000 gallons and no spill history, can write and sign their own plan.'; tag = 'plan'; }
      else { title = 'You need a plan certified by a Professional Engineer'; body = 'A tank over 10,000 gallons, 20,000 gallons or more in total, or a reportable spill history means a licensed engineer must review and certify the plan.'; tag = 'pe'; }
      body += ' Farm thresholds come from a 2014 law and could change; see below.';
    } else {
      if (cap <= 1320) { title = 'No federal SPCC plan needed'; body = 'Sites with 1,320 gallons or less of aboveground capacity are below the threshold.'; tag = 'ok'; }
      else if (hist === 'no' && cap <= 10000 && big <= 5000) { title = 'Tier I: you can use EPA\\'s template'; body = 'You can fill in and self-certify the Tier I template from Appendix G of the rule.'; tag = 'plan'; }
      else if (hist === 'no' && cap <= 10000) { title = 'Tier II: you can self-certify a full plan'; body = 'With a container over 5,000 gallons, you write a full plan but can certify it yourself.'; tag = 'plan'; }
      else { title = 'You need a plan certified by a Professional Engineer'; body = 'Over 10,000 gallons, or a reportable spill history, means a licensed engineer must review and certify the plan.'; tag = 'pe'; }
    }
    show(title, body + note + (tag === 'ok' ? state : ''), tag);
  });
})();
</script>
"""

spcc_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/aboveground-fuel-tanks/">Aboveground tanks</a></p>
  <h1>Do I need an SPCC plan?</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>

  <div class="answer">
    <p><strong>You need an SPCC plan if you store more than 1,320 gallons of oil aboveground, counting only containers of 55 gallons or more, and a spill from your site could reasonably reach a creek, river, lake, wetland, or ditch that drains to one.</strong> Farms get higher thresholds.</p>
  </div>

  <p>That comes from the federal Spill Prevention, Control, and Countermeasure (SPCC) rule, 40 CFR Part 112 {src(C1121, 'eCFR')}. A second trigger covers completely buried storage over 42,000 gallons, but buried tanks already regulated as underground storage tanks don't count toward it.</p>
  <p>Two details trip people up right away:</p>
  <ul>
    <li><strong>It's about capacity, not how much is in the tank.</strong> A 1,000-gallon tank that's half full counts as 1,000 gallons. The rule defines storage capacity as the container's shell capacity {src(C1122, '40 CFR 112.2')}.</li>
    <li><strong>"Oil" means more than fuel.</strong> Diesel, gasoline, motor and hydraulic oil, used oil, and even vegetable oils and animal fats all count {src(C1122, '40 CFR 112.2')}.</li>
  </ul>

  {checker}

  <h2>Step 1: Add up your aboveground capacity</h2>
  <p><strong>List every container that holds oil and is 55 gallons or bigger, and add up the sizes stamped on them.</strong> Under 55 gallons doesn't count {src(C1121, '40 CFR 112.1(d)(5)')}.</p>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Counts toward the total</th><th scope="col">Doesn't count</th></tr></thead>
    <tbody>
      <tr><td>Fuel tanks, skid tanks, and transfer tanks</td><td>Containers under 55 gallons</td></tr>
      <tr><td>Drums and totes of motor oil, hydraulic oil, or grease</td><td>A vehicle's or tractor's own fuel tank ("motive power container")</td></tr>
      <tr><td>Used oil tanks and drums</td><td>Tanks that are permanently closed: emptied, lines disconnected and blanked off, and posted with a closure sign</td></tr>
      <tr><td>Fuel trailers, nurse tanks, and fuel trucks used on your own site {src(FARMFAQ, 'EPA farm FAQ')}</td><td>Heating oil tanks used only at a single-family home</td></tr>
      <tr><td>Tanks you only fill seasonally or keep on standby</td><td>Pesticide application equipment and mix containers</td></tr>
      <tr><td></td><td>Milk containers; hot-mix asphalt</td></tr>
      <tr><td></td><td>Buried tanks already regulated as underground storage tanks</td></tr>
    </tbody>
  </table>
  </div>
  <p class="source-line">Sources: <a href="{C1121}" rel="noopener">40 CFR 112.1(b) and (d)</a>, <a href="{C1122}" rel="noopener">40 CFR 112.2</a>.</p>
  <p><strong>Example.</strong> A contractor's yard has a 1,000-gallon diesel tank, a 500-gallon gasoline tank, a 275-gallon used oil tank, and two 55-gallon drums of hydraulic oil. That's 1,885 gallons. Even if every tank is half empty, it's over 1,320, so the yard moves on to Step 2.</p>

  <h2>Step 2: Could a spill reach water?</h2>
  <p><strong>If your total is over the threshold, the plan is required only if a spill could reasonably reach "navigable waters or adjoining shorelines."</strong> In practice, that includes creeks, rivers, lakes, and wetlands, and ditches or storm drains that lead to them.</p>
  <ul>
    <li><strong>You make the call, based on location.</strong> EPA says the owner decides using things like distance to water, the slope of the land, and how the site drains {src(BASICS, 'EPA: SPCC basics')}.</li>
    <li><strong>Ignore your containment when you decide.</strong> The question is where oil would go if it got out, not whether your dike would hold it {src(BASICS, 'EPA: SPCC basics')}.</li>
    <li><strong>Write it down.</strong> Documenting the decision isn't required, but EPA recommends it. If you decide a spill couldn't reach water, you don't need a plan, but you still have to clean up any spill {src(FARMFAQ, 'EPA farm FAQ')}.</li>
  </ul>

  <h2>Farms: higher thresholds</h2>
  <p><strong>A 2014 law, the Water Resources Reform and Development Act (WRRDA), gave farms their own, higher thresholds.</strong> A farm here means land used to grow crops or raise animals, including fish, that sold or would normally sell at least $1,000 of agricultural products a year {src(C1122, '40 CFR 112.2')}.</p>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Farm's aggregate aboveground capacity</th><th scope="col">What's required</th></tr></thead>
    <tbody>
      <tr><td>Under 2,500 gallons</td><td>No SPCC plan</td></tr>
      <tr><td>2,500 to 6,000 gallons, no reportable discharge history</td><td>No SPCC plan</td></tr>
      <tr><td>Over 6,000 and under 20,000 gallons, no single tank over 10,000 gallons, no reportable discharge history</td><td>Plan required; the farmer can self-certify it</td></tr>
      <tr><td>Any tank over 10,000 gallons, 20,000 gallons or more total, or a reportable discharge history</td><td>Plan certified by a Professional Engineer</td></tr>
    </tbody>
  </table>
  </div>
  <p class="source-line">Source: <a href="{WRRDA}" rel="noopener">EPA: SPCC Program, Farms and WRRDA</a>.</p>
  <p><strong>Farms can also leave out:</strong></p>
  <ul>
    <li>Containers of 1,000 gallons or less on separate parcels</li>
    <li>Containers holding animal feed ingredients approved for livestock feed</li>
    <li>The same exclusions everyone gets: home heating oil, pesticide application equipment, milk containers, and buried tanks under UST rules</li>
  </ul>
  <p class="source-line">Source: <a href="{WRRDA}" rel="noopener">EPA WRRDA fact sheet</a>.</p>
  <p>EPA also says storage is figured separately for central fueling and for each parcel, tract, or field, rather than adding up every location you farm {src(FARMFAQ, 'EPA farm FAQ')}. Fuel trailers and trucks used only on the farm still count {src(FARMFAQ, 'EPA farm FAQ')}.</p>
  <p><strong>"Reportable discharge history" means</strong> a single spill of more than 1,000 gallons to water, or two spills of more than 42 gallons each within any 12 months, during the three years before you certify the plan. Spills caused by natural disasters, war, or terrorism don't count {src(ECFR, '40 CFR 112.3(g)')}.</p>
  <p><strong>These numbers could change.</strong> The farm thresholds come from the 2014 law, not the regulation text. EPA's 2015 study recommended dropping the 6,000-gallon tier and using 2,500 gallons for farms {src(STUDY, 'EPA farm study')}, but we found no final rule making that change. Going the other way, the House passed the PERMIT Act (H.R. 3898) in December 2025, which would raise the farm thresholds, including 20,000 to 42,000 gallons and 2,500 to 3,000 (<a href="{HRPT}" rel="noopener">House Report 119-180</a>; <a href="{BDLAW}" rel="noopener">Beveridge &amp; Diamond</a>). As of October 28, 2026, it hadn't passed the Senate {src(LEGIS, 'Legislate')}. This guide will be updated if either changes.</p>

  <h2>Which kind of plan you need</h2>
  <p><strong>If you need a plan and have 10,000 gallons or less with no reportable spill history, you can usually write and certify it yourself.</strong> EPA calls these "qualified facilities" {src(ECFR, '40 CFR 112.3(g)')}.</p>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Non-farm site</th><th scope="col">Plan type</th></tr></thead>
    <tbody>
      <tr><td>10,000 gallons or less, no container over 5,000 gallons, no spill history</td><td>Tier I: fill in and self-certify EPA's template</td></tr>
      <tr><td>10,000 gallons or less, a container over 5,000 gallons, no spill history</td><td>Tier II: write a full plan and self-certify it</td></tr>
      <tr><td>Over 10,000 gallons, or a reportable spill history</td><td>A licensed Professional Engineer reviews and certifies the plan</td></tr>
    </tbody>
  </table>
  </div>
  <p>The Tier I template is Appendix G of the rule {src(ECFR, '40 CFR 112.6(a)')}, and the engineer requirement is in {src(ECFR, '40 CFR 112.3(d)')[1:-1]}. Any site can choose an engineer-certified plan even if it qualifies to self-certify {src(BASICS, 'EPA: SPCC basics')}.</p>

  <h2>What the plan has to cover</h2>
  <p><strong>An SPCC plan isn't just paperwork. It describes the equipment and routines that keep oil in the tank, and you have to actually follow it.</strong> The main pieces for a typical tank site:</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Requirement</th><th scope="col">What it means in practice</th><th scope="col">Rule</th></tr></thead>
    <tbody>
      <tr><td>Secondary containment</td><td>A dike, berm, double-wall tank, or similar that holds the entire contents of the largest container, plus room for rain. See <a href="{SC_PATH}">secondary containment</a> for sizing</td><td><a href="{ECFR}" rel="noopener">112.8(c)(2)</a></td></tr>
      <tr><td>Containment where you transfer fuel</td><td>Spill protection sized for a likely spill at fill points, loading areas, and mobile refuelers</td><td><a href="{BASICS}" rel="noopener">EPA basics</a></td></tr>
      <tr><td>Overfill prevention</td><td>At least one of: a high-level alarm, a high-level pump cutoff, direct communication between whoever is gauging and whoever is pumping, or a fast-response level gauge someone watches during the fill</td><td><a href="{ECFR}" rel="noopener">112.8(c)(8)</a></td></tr>
      <tr><td>Inspections</td><td>Inspect or test each tank on a regular schedule using an industry standard, check supports and foundations, and keep records</td><td><a href="{ECFR}" rel="noopener">112.8(c)(6)</a></td></tr>
      <tr><td>Fix leaks</td><td>Promptly fix visible leaks from seams, gaskets, piping, pumps, and valves, and remove oil that collects in the dike</td><td><a href="{ECFR}" rel="noopener">112.8(c)(10)</a></td></tr>
      <tr><td>Training</td><td>Train the people who handle oil, name one person accountable for spill prevention, and hold a spill prevention briefing at least once a year</td><td><a href="{ECFR}" rel="noopener">112.7(f)</a></td></tr>
      <tr><td>Keep it on site</td><td>Keep a full copy at the site if it's normally attended at least four hours a day</td><td><a href="{ECFR}" rel="noopener">112.3(e)</a></td></tr>
      <tr><td>Keep it current</td><td>Amend the plan within six months of a change that affects spill risk, such as adding a tank, and put the change in place within six months after that. Review the whole plan at least once every five years</td><td><a href="{ECFR}" rel="noopener">112.5</a></td></tr>
    </tbody>
  </table>
  </div>
  <p>Tier I sites using EPA's template can meet some of these in simpler ways, such as alternative overfill and containment measures spelled out in the rule {src(ECFR, '40 CFR 112.6(a)(3)')}.</p>

  <h2>Your state may add its own rules</h2>
  <p><strong>The SPCC rule is federal and enforced by EPA, but many states have their own tank rules on top of it, and some apply even when you don't need a federal plan.</strong> EPA can't hand the SPCC program itself to a state {src(SD, 'South Dakota DANR')}, so state rules are a separate layer. A few examples:</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">State</th><th scope="col">What's different</th></tr></thead>
    <tbody>
      <tr><td>California</td><td>Covers farms that store at least 1,320 gallons of petroleum aboveground, no matter how far they are from water. Covered farms file an annual tank facility statement, and farms under the conditional exemption must inspect tanks daily {src(CA, 'CAL FIRE OSFM')}.</td></tr>
      <tr><td>Minnesota</td><td>Commercial aboveground tanks of 500 gallons or more must be reported to the state pollution control agency. Farm tanks are listed as exempt {src(MN, 'MPCA')}.</td></tr>
      <tr><td>Michigan</td><td>The state's Part 5 spill rules require a Pollution Incident Prevention Plan for regulated amounts of oil. A site with an SPCC plan and no other regulated materials doesn't need a separate one for oil, but must hand over its SPCC plan within 30 days if the state or local officials ask {src(MI, 'Michigan DEQ')}.</td></tr>
    </tbody>
  </table>
  </div>
  <p>Your state environmental agency, state fire marshal, and local fire department may also have rules on tank placement, setbacks, and permits. Check with them before installing a new tank.</p>

  <h2>Common mistakes</h2>
  <ul>
    <li><strong>Counting gallons in the tank instead of tank size.</strong> The rule uses shell capacity {src(C1122, '40 CFR 112.2')}.</li>
    <li><strong>Forgetting the small stuff.</strong> Drums, totes, used oil tanks, and fuel trailers all count once they're 55 gallons or bigger.</li>
    <li><strong>Assuming the fuel supplier handles it.</strong> EPA holds the tank owner or operator responsible, not the company that fills the tank {src(FARMFAQ, 'EPA farm FAQ')}.</li>
    <li><strong>Writing a plan and filing it away.</strong> The plan only counts if you follow it: inspections, training, containment, and keeping it on site.</li>
    <li><strong>Not updating after a change.</strong> Adding a tank or changing piping can mean amending the plan within six months {src(ECFR, '40 CFR 112.5')}.</li>
  </ul>

  <section class="faq">
  <h2>FAQ</h2>
  {spcc_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{ECFR}" rel="noopener">40 CFR Part 112, full text (eCFR)</a></li>
    <li><a href="{C1121}" rel="noopener">40 CFR 112.1, applicability and exemptions (Cornell LII)</a></li>
    <li><a href="{C1122}" rel="noopener">40 CFR 112.2, definitions (Cornell LII)</a></li>
    <li><a href="{WRRDA}" rel="noopener">EPA: SPCC Program, Farms and the Water Resources Reform and Development Act (2015)</a></li>
    <li><a href="{STUDY}" rel="noopener">EPA: Oil Storage on U.S. Farms, WRRDA study (2015)</a></li>
    <li><a href="{BASICS}" rel="noopener">EPA: SPCC rule basics</a></li>
    <li><a href="{TIERS}" rel="noopener">EPA: Tier I vs. Tier II qualified facilities</a></li>
    <li><a href="{FARMFAQ}" rel="noopener">EPA: SPCC frequently asked questions for farms</a></li>
    <li><a href="{HRPT}" rel="noopener">U.S. House Report 119-180, PERMIT Act (2025)</a></li>
    <li><a href="{BDLAW}" rel="noopener">Beveridge &amp; Diamond: House approves Clean Water Act reforms</a></li>
    <li><a href="{SD}" rel="noopener">South Dakota DANR: SPCC for farm tanks</a></li>
    <li><a href="{CA}" rel="noopener">CAL FIRE OSFM: APSA for farms</a></li>
    <li><a href="{MN}" rel="noopener">Minnesota Pollution Control Agency: Aboveground storage tank systems</a></li>
    <li><a href="{MI}" rel="noopener">Michigan DEQ: Part 5 rules and oil storage</a></li>
  </ul>
  <p class="note">This guide is general information, not legal advice. For a specific site, check with EPA's regional office, your state environmental agency, or a Professional Engineer familiar with SPCC.</p>
</article>
"""

spcc_schema = [
    {
        "@context": "https://schema.org", "@type": "Article",
        "headline": SPCC_TITLE, "description": SPCC_DESC,
        "datePublished": UPDATED, "dateModified": UPDATED,
        "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
        "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
        "mainEntityOfPage": DOMAIN + SPCC_PATH,
    },
    {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in spcc_faq],
    },
]
page(SPCC_PATH, SPCC_TITLE, SPCC_DESC, spcc_body, schema=spcc_schema, og_type="article")

# ---------------- Article: secondary containment ----------------
C1127 = "https://www.law.cornell.edu/cfr/text/40/112.7"
C1128 = "https://www.law.cornell.edu/cfr/text/40/112.8"
EPACH4 = "https://www.epa.gov/sites/default/files/2014-04/documents/4_secondarycontainment_impracticability_2014.pdf"
NOAA = "https://hdsc.nws.noaa.gov/pfds/"
CAZ = "https://www.cazfire.gov/DocumentCenter/View/133/Above-Ground-Fuel-Tank-Checklist-PDF"

SC_TITLE = "Fuel Tank Secondary Containment: Sizing, Dikes, Double-Wall"
SC_DESC = ("How big a fuel tank dike has to be, when a double-wall tank counts as containment, "
           "and what the 110% rule really means under the federal SPCC rule.")

sc_faq = [
    ("Does a double-wall tank need a dike around it?",
     f"Usually not for the tank itself. The outer wall can be the containment for a leak from the inner tank {src(EPACH4, 'EPA SPCC guidance, ch. 4')}. "
     "You still need to deal with spills at the fill point, the hose and nozzle, and overfills through the vent."),
    ("Is 110% required?",
     f"Not by the federal rule. It requires the full capacity of the largest container plus enough freeboard for rain, and leaves the rain amount to the plan {src(EPACH4, 'EPA SPCC guidance, ch. 4')}. "
     "Your state, fire code, or plan certifier may set a number."),
    ("Do I need containment if I don't need an SPCC plan?",
     "Not under the federal SPCC rule, since containment is a requirement of the plan. State rules and your fire code can still require it, and a dike or double-wall tank is cheap insurance against a cleanup bill."),
    ("Can I just drain the rainwater out of my dike?",
     f"Only if the drain valve is normally kept sealed closed, you check the water for oil first, and you keep a record each time {src(C1128, '40 CFR 112.8(c)(3)')}."),
]
sc_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in sc_faq)

sc_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/aboveground-fuel-tanks/">Aboveground tanks</a></p>
  <h1>Fuel tank secondary containment: sizing, dikes, and double-wall tanks</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>

  <div class="answer">
    <p><strong>If your site needs an SPCC plan, every bulk fuel tank needs secondary containment that holds the entire capacity of the largest tank, plus enough extra room ("freeboard") for rain.</strong> A dike, a containment basin, or a double-wall tank can all do the job. The federal rule doesn't say 110%; that's a rule of thumb.</p>
  </div>

  <p>Secondary containment is the second barrier: if the tank (the primary container) leaks or splits, the containment catches the fuel before it reaches soil or water. The requirement comes from the federal Spill Prevention, Control, and Countermeasure (SPCC) rule, so it applies once your site needs an SPCC plan. Not sure whether you do? Start with <a href="{SPCC_PATH}">Do I need an SPCC plan?</a></p>

  <h2>What the rule requires</h2>
  <p><strong>The SPCC rule has two containment requirements, and most fuel sites need both.</strong></p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Requirement</th><th scope="col">What it covers</th><th scope="col">How big</th></tr></thead>
    <tbody>
      <tr><td>Sized containment {src(C1128, '40 CFR 112.8(c)(2)')}</td><td>Bulk storage tanks: your fuel tanks, used oil tanks, and other stationary containers</td><td>The entire capacity of the largest single container, plus sufficient freeboard to contain precipitation</td></tr>
      <tr><td>Sized containment for mobile containers {src(C1128, '40 CFR 112.8(c)(11)')}</td><td>Drums, totes, and skid tanks that get moved around (mobile refuelers and tank trucks excepted)</td><td>The largest single compartment or container, plus freeboard for precipitation</td></tr>
      <tr><td>General containment {src(C1127, '40 CFR 112.7(c)')}</td><td>Everywhere else oil could spill: fill points, transfer areas, hoses and nozzles, mobile refuelers</td><td>The most likely spill, based on the typical way things fail there</td></tr>
    </tbody>
  </table>
  </div>
  <p>The rule also says the containment, walls and floor, has to actually hold oil until cleanup: diked areas must be "sufficiently impervious to contain discharged oil" {src(C1128, '40 CFR 112.8(c)(2)')}, and a spill can't escape the system before cleanup {src(C1127, '40 CFR 112.7(c)')}.</p>
  <p><strong>"Largest single container" can be more than one tank.</strong> Tanks that are permanently manifolded together, so they work as a single storage unit, count as one container for sizing {src(EPACH4, 'EPA SPCC guidance, ch. 4')}.</p>

  <h2>The 110% rule and "sufficient freeboard"</h2>
  <p><strong>The federal rule never says 110%.</strong> EPA's own inspector guidance says the rule "does not specifically define the term 'sufficient freeboard,' nor does it describe how to calculate this volume" {src(EPACH4, 'EPA SPCC guidance, section 4.3.2')}.</p>
  <ul>
    <li><strong>Where 110% comes from.</strong> When EPA proposed using storm data, commenters suggested 110% of tank capacity as a simpler alternative {src(EPACH4, 'EPA SPCC guidance, section 4.3.2')}. It stuck as a rule of thumb.</li>
    <li><strong>What EPA said is "proper."</strong> In the 2002 rule preamble, EPA wrote that sufficient freeboard is the amount needed to hold the rain from a 25-year, 24-hour storm {src(EPACH4, 'EPA SPCC guidance, section 4.3.2')}.</li>
    <li><strong>Who decides.</strong> The Professional Engineer certifying the plan, or the owner for a self-certified plan, sets the freeboard and should write down how it was figured {src(EPACH4, 'EPA SPCC guidance, ch. 4')}.</li>
    <li><strong>Indoors or under a roof.</strong> When containment is inside a building, freeboard for rain usually doesn't apply {src(EPACH4, 'EPA SPCC guidance, ch. 4')}.</li>
  </ul>
  <p>Some fire codes use the same storm: a fire code checklist based on the International Fire Code sizes outdoor drainage for "a 24-hour rainfall as determined by a 25-year storm" {src(CAZ, 'Central Arizona Fire checklist, IFC 2012')}.</p>

  <h2>Sizing a dike: a worked example</h2>
  <p><strong>Rain falls on the whole dike, not just the tank, so a small dike can need more than 110%.</strong> Here's the math for a common farm setup. The storm number is only an example; look up yours in NOAA's precipitation frequency data {src(NOAA, 'NOAA Atlas 14')}.</p>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Step</th><th scope="col">Example</th></tr></thead>
    <tbody>
      <tr><td>The setup</td><td>One 1,000-gallon tank on a stand inside an 8 ft by 14 ft dike. The tank bottom sits above the top of the dike wall, so the tank takes up almost no room in the dike.</td></tr>
      <tr><td>1. Tank volume in cubic feet</td><td>1,000 gal &divide; 7.48 gal/ft&sup3; = 133.7 ft&sup3;</td></tr>
      <tr><td>2. Rain on the dike floor</td><td>Example 25-year, 24-hour storm of 4.5 in = 0.375 ft. 8 &times; 14 = 112 ft&sup2; &times; 0.375 ft = 42.0 ft&sup3; (about 314 gallons)</td></tr>
      <tr><td>3. Total volume needed</td><td>133.7 + 42.0 = 175.7 ft&sup3;</td></tr>
      <tr><td>4. Wall height</td><td>175.7 ft&sup3; &divide; 112 ft&sup2; = 1.57 ft, about 19 inches</td></tr>
      <tr><td>Compare: 110% of the tank</td><td>1,100 gal = 147.1 ft&sup3;, a 15.8-inch wall. That falls about 3 inches short of the storm-based number here</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Two adjustments for real sites:</strong></p>
  <ul>
    <li><strong>Subtract anything sitting in the dike below the wall top:</strong> other tanks, saddles, the foundation of a tank that sits on the floor. EPA's worked example subtracts the volume the tanks displace {src(EPACH4, 'EPA SPCC guidance, ch. 4')}. Size the dike for the largest tank, with the other tanks counted as taking up space.</li>
    <li><strong>Leave room for the water you haven't drained yet.</strong> Rain that sits in the dike takes up the space meant for fuel.</li>
  </ul>

  <h2>Your containment options</h2>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Option</th><th scope="col">How it works</th><th scope="col">Watch for</th></tr></thead>
    <tbody>
      <tr><td>Dike or berm</td><td>Concrete, block, or earth walls around one or more tanks; the rule names dikes, containment curbs, and pits {src(C1128, '40 CFR 112.8(c)(2)')}</td><td>Cracks, unsealed joints, earthen floors that let fuel soak in, and rainwater management</td></tr>
      <tr><td>Steel containment basin</td><td>A prefabricated steel tub the tank sits in</td><td>Rainwater fills it unless it's covered; rust at the seams</td></tr>
      <tr><td>Double-wall tank</td><td>A tank inside a tank; the outer wall is the containment</td><td>Still need protection at the fill point, hose, and vent (see below)</td></tr>
      <tr><td>Drainage to a catchment basin</td><td>Curbs and trenches that carry a spill to a holding pond or basin {src(C1128, '40 CFR 112.8(c)(2)')}</td><td>Usually for larger sites; the basin has to hold the largest tank</td></tr>
      <tr><td>Spill pallets and drip pans</td><td>For drums and totes; curbing and drip pans are listed containment methods {src(C1127, '40 CFR 112.7(c)')}</td><td>Pallet capacity has to cover the largest drum or tote on it</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Field note:</strong> Most of the farm and fleet setups I service use double-wall tanks rather than a single-wall tank in a dike.</p>

  <h2>Double-wall tanks</h2>
  <p><strong>A double-wall tank can be its own secondary containment.</strong> EPA describes it as "a tank within another tank," where the inner tank stores the fuel and the outer tank is the containment {src(EPACH4, 'EPA SPCC guidance, ch. 4')}. Because rain can't get into the space between the walls, double-wall tanks usually don't need extra freeboard {src(EPACH4, 'EPA SPCC guidance, ch. 4')}.</p>
  <p><strong>The catch is everything outside the outer wall.</strong> EPA notes a double-wall tank doesn't contain an overfill that comes out of the vent during a delivery {src(EPACH4, 'EPA SPCC guidance, ch. 4')}. Piping, pumps, and dispensers outside the tank also need their own general containment {src(EPACH4, 'EPA SPCC guidance, ch. 4')}. EPA treats a shop-built double-wall tank as covering the general containment requirement too when it has all of these:</p>
  <ul>
    <li>The tank was built in a shop, not in the field</li>
    <li>The inner tank is a UL-listed steel tank</li>
    <li>The outer tank is built to a recognized industry standard, such as API or STI</li>
    <li>It has an overfill alarm, plus an automatic flow restrictor or shutoff</li>
    <li>Every transfer is constantly watched</li>
  </ul>
  <p class="source-line">Source: <a href="{EPACH4}" rel="noopener">EPA SPCC Guidance for Regional Inspectors, chapter 4</a>. Without the overfill equipment, you can instead put active or passive containment where a vent overfill would land.</p>
  <p>Inspections still apply: the rule's routine checks for leaks and deterioration cover the inner tank of a double-wall tank {src(EPACH4, 'EPA SPCC guidance, ch. 4')}, and double-wall tanks usually have a port for checking the space between the walls.</p>
  <p><strong>Field note:</strong> When I check the space between the walls, condensation is the usual find. It's common, and it has to be sponged out. Fuel in there is a different story: it usually means the inner tank has failed, which I see on tanks after years of service.</p>
  <p>For protected tanks, fire code checklists also call for emergency venting on enclosed secondary containment {src(CAZ, 'Central Arizona Fire checklist')}. For tank construction types, see <a href="/aboveground-fuel-tanks/">aboveground fuel tanks</a>.</p>

  <h2>Fill points, hoses, and fuel trailers</h2>
  <p><strong>Containment around the tank doesn't cover where the fuel actually moves.</strong> Fill connections, the pump and hose, and areas where you fuel equipment fall under the general requirement: containment sized for the most likely spill {src(C1127, '40 CFR 112.7(c)')}. Methods the rule lists include curbing, drip pans, sumps, and sorbent materials {src(C1127, '40 CFR 112.7(c)')}.</p>
  <p>Mobile refuelers and tank trucks used only on your site are excepted from sized containment {src(C1128, '40 CFR 112.8(c)(11)')}, but still need general containment {src(EPACH4, 'EPA SPCC guidance, ch. 4')}. On farms, nurse tanks and fuel trailers count toward your SPCC capacity {src(FARMFAQ, 'EPA farm FAQ')}. Overfill protection is a separate SPCC requirement; the <a href="{SPCC_PATH}">SPCC guide</a> lists the options.</p>

  <h2>Keeping containment working</h2>
  <ul>
    <li><strong>Drain rainwater the right way.</strong> Keep the dike's drain or bypass valve normally sealed closed, check the water for oil before you open it, reseal it afterward, and keep a record each time {src(C1128, '40 CFR 112.8(c)(3)')}.</li>
    <li><strong>Inspect it.</strong> The rule calls for frequent inspection of the outside of each tank for deterioration, leaks, and "accumulation of oil inside diked areas" {src(C1128, '40 CFR 112.8(c)(6)')}.</li>
    <li><strong>Keep the floor and walls tight.</strong> Seal cracks and joints in concrete, and keep earthen dikes free of burrows and erosion. The containment has to be "sufficiently impervious" {src(C1128, '40 CFR 112.8(c)(2)')}.</li>
    <li><strong>Don't store junk in the dike.</strong> Anything sitting in it takes up volume you counted on for fuel.</li>
  </ul>
  <p><strong>Field note:</strong> The dike problem I run into most is rainwater that never got drained. The dike sits full, and in winter it freezes solid. A dike full of ice has no room left for a spill.</p>

  <h2>When containment isn't practical</h2>
  <p><strong>If a dike or other containment truly can't be built, the rule allows an alternative, but it's more work, not less.</strong> The plan has to explain why containment isn't practicable, and you have to:</p>
  <ul>
    <li>Periodically integrity test the tanks, and integrity and leak test the valves and piping</li>
    <li>Have an oil spill contingency plan</li>
    <li>Put a written commitment of people, equipment, and materials to clean up a spill in the plan</li>
  </ul>
  <p class="source-line">Source: <a href="{C1127}" rel="noopener">40 CFR 112.7(d)</a>. This route needs a Professional Engineer to certify that part of the plan, even at a self-certified site.</p>

  <section class="faq">
  <h2>FAQ</h2>
  {sc_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{C1127}" rel="noopener">40 CFR 112.7, general requirements including secondary containment and impracticability (Cornell LII)</a></li>
    <li><a href="{C1128}" rel="noopener">40 CFR 112.8, requirements for onshore facilities including bulk storage containers (Cornell LII)</a></li>
    <li><a href="{EPACH4}" rel="noopener">EPA: SPCC Guidance for Regional Inspectors, chapter 4, Secondary Containment and Impracticability (2013)</a></li>
    <li><a href="{FARMFAQ}" rel="noopener">EPA: SPCC frequently asked questions for farms</a></li>
    <li><a href="{NOAA}" rel="noopener">NOAA: Precipitation Frequency Data Server (Atlas 14)</a></li>
    <li><a href="{CAZ}" rel="noopener">Central Arizona Fire and Medical Authority: Above-ground fuel tank checklist (IFC 2012)</a></li>
  </ul>
  <p class="note">This guide is general information, not legal advice. Your state and local fire code can add their own containment rules. For a specific site, check with your state environmental agency, fire marshal, or a Professional Engineer familiar with SPCC.</p>
</article>
"""

sc_schema = [{"@context": "https://schema.org", "@type": "Article", "headline": SC_TITLE, "description": SC_DESC,
              "datePublished": UPDATED, "dateModified": UPDATED, "mainEntityOfPage": DOMAIN + SC_PATH}]
page(SC_PATH, SC_TITLE, SC_DESC, sc_body, schema=sc_schema, og_type="article")

# ---------------- Article: water in diesel ----------------
CRC672 = "https://www.cdfa.ca.gov/dms/programs/petroleum/CRC_DieselStorageSystem.pdf"
CENEXW = "https://www.cenex.com/expert-advice-and-insights/water-contaminated-diesel"
GILBERT = "https://neiwpcc.org/wp-content/uploads/2018/10/Gilbert.pdf"
EPA16 = "https://www.epa.gov/archive/epa/newsreleases/epa-research-shows-moderate-or-severe-corrosion-majority-diesel-fuel-underground.html"
DNET = "https://dieselnet.com/news/2016/07epa3.php"
STI = "https://sandiegocounty.gov/content/dam/sdc/deh/hmd/pdf/STI-SP001-Monthly-Inspection-Checklist-7th-Edition.pdf"
BELL = "https://www.bellperformance.com/hubfs/External%20Documents/Bell_Performs/Fuel_storage_tank_treatment_recs_and_procs_periodic_052014.pdf"
PSAIL = "https://www.practical-sailor.com/boat-maintenance/diesel-biocides-take-on-contaminated-boat-fuel"
VEEDER = "https://www.veeder.com/us/blog/why-does-water-need-be-removed-continuously"
FDUMP = "https://fueldump.co.uk/product/water-finding-paste/"
OTW = "https://oiltankwarehouse.co.uk/product/water-finding-paste/"
MODNR = "https://dnr.mo.gov/document-search/management-petroleum-storage-tank-wastes-pub2040/pub2040"

WATER_PATH = "/water-in-diesel-tank/"
WATER_TITLE = "Water in Your Diesel Tank: How It Gets There and How to Get It Out"
WATER_DESC = ("Water sinks to the bottom of a diesel tank, feeds microbes, and causes corrosion and "
              "plugged filters. How to check for it, get it out, and keep it from coming back.")

water_faq = [
    ("How much water is too much?",
     f"Any water you can detect. Industry guidance says \"no detectable water is desirable\" {src(CRC672, 'CRC Report 672')}. The diesel spec, ASTM D975, allows only 0.05% water and sediment in the fuel itself {src(GILBERT, 'Gilbert')}."),
    ("Can an additive take care of water instead of draining it?",
     f"No additive replaces getting free water off the bottom. Water you can measure with paste should be removed as soon as possible {src(CRC672, 'CRC Report 672')}. Water treatments and biocides are for what's left after you drain."),
    ("Is \"diesel algae\" really algae?",
     f"Not usually. The growth people call algae is microbes, such as bacteria and fungi, living in the water layer and feeding on the fuel (<a href=\"{CENEXW}\" rel=\"noopener\">Cenex</a>; <a href=\"{GILBERT}\" rel=\"noopener\">Gilbert</a>). Without water, they can't grow."),
    ("Where does water in a new tank come from?",
     f"Usually condensation and the top of the tank: vents, caps, and gaskets. It can also arrive with a delivery (<a href=\"{CRC}\" rel=\"noopener\">CRC Report 671</a>; <a href=\"{CRC672}\" rel=\"noopener\">CRC Report 672</a>)."),
]
water_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in water_faq)

water_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/fuel-quality/">Fuel quality</a></p>
  <h1>Water in your diesel tank: how it gets there and how to get it out</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>
  {AFF_NOTE}

  <div class="answer">
    <p><strong>Water is heavier than diesel, so it sinks and collects at the bottom of the tank, right where most pickups and drains are.</strong> The industry guide for diesel storage puts it simply: "No detectable water is desirable," and any water you find should come out as soon as possible {src(CRC672, 'CRC Report 672')}.</p>
  </div>

  <p>A little water rarely shows up as a sudden problem. It sits on the bottom, grows microbes, rusts the tank, and slowly plugs filters until equipment starts running rough. This guide covers how water gets in, how to check for it, how to get it out, and how to keep it out.</p>

  <h2>How water gets in</h2>
  <p><strong>Most water gets in through the top of the tank, or forms inside it as condensation.</strong> Very little comes from the refinery. Fuel picks up water the farther it travels through terminals, trucks, and storage {src(CRC, 'CRC Report 671')}.</p>
  <ul>
    <li><strong>Condensation.</strong> Tanks "breathe." As the air space inside warms during the day it pushes air out, and as it cools at night it pulls humid air in. Moisture condenses on the tank walls and runs down into the fuel {src(CRC, 'CRC Report 671')}. Long stretches with a low fuel level make it worse {src(CRC672, 'CRC Report 672')}.</li>
    <li><strong>Rain and snow.</strong> Water gets in through vent caps that don't seal, loose bungs and fill caps, broken gaskets, and snow or standing water around the fill {src(CRC672, 'CRC Report 672')}.</li>
    <li><strong>Deliveries.</strong> Water can come in with the load, and a delivery can stir up water already sitting on the bottom, especially when the fuel level is low or the outlet sits close to the bottom {src(CRC, 'CRC Report 671')}.</li>
  </ul>

  {WATER_TANK_SVG}

  <h2>Why a little water matters</h2>
  <p><strong>Water is where the trouble starts: microbes grow in it, it rusts the tank, and it freezes in winter.</strong></p>
  <ul>
    <li><strong>Microbes.</strong> Bacteria and fungi live in the water layer and feed on the diesel above it. They form slime, plug filters, and produce acids that corrode the tank (<a href="{CENEXW}" rel="noopener">Cenex</a>; <a href="{GILBERT}" rel="noopener">Gilbert, National Tanks Conference 2018</a>). One 2018 analysis of 3,855 tank bottom samples from across the lower 48 states found microbes in about 20% of them {src(GILBERT, 'Gilbert')}.</li>
    <li><strong>Corrosion.</strong> In a 2016 EPA study, 35 of 42 diesel tanks (83%) had moderate or severe internal corrosion, and fewer than a quarter of the owners knew it beforehand. EPA suspects microbes are a large part of the cause (<a href="{EPA16}" rel="noopener">EPA</a>; <a href="{DNET}" rel="noopener">DieselNet</a>). That study looked at underground tanks, but the same water and microbes live in aboveground tanks.</li>
    <li><strong>Ice.</strong> In cold weather, water can freeze and block a tank outlet or a dispenser filter. Aboveground tanks are especially exposed {src(CRC, 'CRC Report 671')}.</li>
    <li><strong>Equipment problems.</strong> Water that gets through shows up as rough starting, rough idle, hesitation, power loss, and white exhaust smoke {src(CENEXW, 'Cenex')}.</li>
  </ul>

  <h2>How to check for water</h2>
  <p><strong>Put water-finding paste on a gauge stick, lower it to the very bottom of the tank, and look for a color change.</strong> It's the fastest check and costs a few dollars.</p>
  <ol>
    <li><strong>Coat the bottom few inches of a clean gauge stick</strong> with a thin layer of paste. A weighted string works if you have no stick {src(FDUMP, 'Fuel Dump')}.</li>
    <li><strong>Lower it straight down until it touches bottom.</strong> Hold it there for about 30 seconds {src(BELL, 'Bell Performance')}.</li>
    <li><strong>Pull it up and read it.</strong> The paste turns from brown to bright red where it touched water. The height of the red band is the depth of the water layer {src(OTW, 'Oil Tank Warehouse')}.</li>
    <li><strong>Check the low end of the tank.</strong> Many tanks sit slightly tilted, so water collects at one end. Gauge as close to that end as your openings allow. Slope and fittings in the tank can affect the reading {src(CRC672, 'CRC Report 672')}.</li>
  </ol>
  <p><strong>Two other quick checks:</strong></p>
  <ul>
    <li><strong>Pull a sample in a clear jar</strong> from the dispenser nozzle or a bottom drain. Good fuel is "clear and bright," with no haze, particles, or layer of water on the bottom {src(CRC672, 'CRC Report 672')}. If you can't tell right away, let it sit overnight; water settles to the bottom {src(CENEXW, 'Cenex')}.</li>
    <li><strong>Look at your dispenser filter.</strong> Filters that plug quickly, slow flow, or rust or slime on a removed filter all point to water and microbes {src(CRC672, 'CRC Report 672')}.</li>
  </ul>
  <p><strong>How often?</strong> The industry's standard monthly inspection for aboveground tanks asks whether the tank is free of water {src(STI, 'STI SP001 monthly checklist')}. Guidance for busy fueling sites goes further: check with paste weekly and before and after deliveries {src(CRC672, 'CRC Report 672')}. For a farm or yard tank, monthly plus after every delivery is a reasonable minimum.</p>
  <p><strong>Seeing slime or dark sludge?</strong> That points to microbes. Inexpensive test kits can confirm it, and you should test water you remove from the tank {src(CRC672, 'CRC Report 672')}.</p>

  <h2>How to get the water out</h2>
  <p><strong>Pull it off the bottom, check again, and repeat until the paste stays brown.</strong> Then deal with any microbes and change the filter.</p>
  <ol>
    <li><strong>Drain or pump from the lowest point.</strong> If your tank has a bottom drain valve, open it into a clean container until fuel runs clear. Otherwise, pump from the bottom through a pipe or wand that reaches the low end. A self-priming pump suited to fuel and water handles the bulk of it {src(FDUMP, 'Fuel Dump')}.</li>
    <li><strong>Re-check with paste.</strong> Keep pumping and re-checking until there's too little water left to pump {src(FDUMP, 'Fuel Dump')}.</li>
    <li><strong>Test for microbes if you see slime or sludge.</strong> If the water tests positive, the usual sequence is: remove the water, add a biocide, let it work, remove the water bottom again, and retest over the following weeks {src(GILBERT, 'Gilbert')}. See <a href="{BIO_PATH}">diesel bugs and biocides</a> for the full process. Biocides are EPA-registered pesticides, so follow the label exactly {src(PSAIL, 'Practical Sailor')}.</li>
    <li><strong>Expect filters to plug for a while after a biocide treatment.</strong> Dead microbes come loose from the tank walls and get caught in filters (<a href="{PSAIL}" rel="noopener">Practical Sailor</a>; <a href="{CRC672}" rel="noopener">CRC Report 672</a>). Keep spares on hand.</li>
    <li><strong>Change the dispenser filter</strong> when you're done, and look at the old one for rust or slime.</li>
  </ol>
  <p><strong>Call for a tank cleaning when</strong> there's heavy sludge, the water keeps coming back, or filters keep plugging after treatment. A badly infected tank usually needs the bottom material removed mechanically, not just treated {src(PSAIL, 'Practical Sailor')}. Your fuel supplier can often pump the tank out {src(CENEXW, 'Cenex')}. See <a href="/diesel-tank-cleaning/">tank cleaning and fuel polishing</a>.</p>
  <p><strong>Don't dump the water on the ground.</strong> Water from a fuel tank bottom is petroleum-contaminated and can count as hazardous waste. Don't pour it on soil, into surface water, or down a storm drain or septic system. Keep it in a closed, labeled container and ask your state environmental agency or a waste hauler how to dispose of it {src(MODNR, 'Missouri DNR')}.</p>

  <h2>How to keep water out</h2>
  <p><strong>Seal the top of the tank, keep it from sitting half empty, and drain the bottom on a schedule.</strong> Removing water once doesn't fix the problem. The tank goes right back to growing microbes as soon as water returns {src(VEEDER, 'Veeder-Root')}, so routine draining is the best defense {src(CRC, 'CRC Report 671')}.</p>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Where water gets in</th><th scope="col">What to do</th></tr></thead>
    <tbody>
      <tr><td>Fill cap and bungs</td><td>Make sure caps close tight and gaskets aren't cracked; replace worn ones {src(CRC672, 'CRC Report 672')}</td></tr>
      <tr><td>Vent</td><td>Check that the vent cap seals against rain and blowing snow, and inspect vents after storms {src(STI, 'STI SP001 checklist')}. A desiccant vent cap dries the air the tank breathes in {src(GILBERT, 'Gilbert')}</td></tr>
      <tr><td>Condensation</td><td>Avoid letting the tank sit low for long stretches, especially going into fall and winter {src(CRC672, 'CRC Report 672')}</td></tr>
      <tr><td>Around the fill</td><td>Keep snow, ice, and standing water away from the fill opening {src(CRC672, 'CRC Report 672')}</td></tr>
      <tr><td>Deliveries</td><td>Check for water before and after each delivery {src(CRC672, 'CRC Report 672')}, and ask your supplier what they do about water in their own tanks and trucks</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Use a water-blocking filter on the dispenser.</strong> Filters that absorb or detect water stop it before it reaches your equipment and warn you something is wrong. Fill-Rite, for example, sells 10-micron water-detecting and Hydrosorb filters for transfer pumps {src(FILLRITE, 'Fill-Rite')}.</p>

  <h2>What you'll need</h2>
  <ul>
    <li>Water-finding paste and a clean gauge stick: {amz("Kolor Kut water finding paste", "Kolor Kut paste on Amazon")}</li>
    <li>A water-blocking or water-detecting dispenser filter: {amz("Fill-Rite Hydrosorb water filter", "Fill-Rite water filters on Amazon")}</li>
    <li>A clear sample jar for checking fuel: {amz("fuel sample bottle clear", "sample bottles on Amazon")}</li>
    <li>A desiccant vent breather, if your vent fits one: {amz("fuel tank desiccant breather", "desiccant breathers on Amazon")}</li>
    <li>A diesel biocide, only if you've confirmed microbes: {amz("diesel fuel biocide", "diesel biocides on Amazon")}</li>
  </ul>

  <h2>Water checklist for tank owners</h2>
  <ul class="checklist">
    <li>Check the tank bottom with water-finding paste at least monthly and after every delivery</li>
    <li>Pull a clear-jar sample now and then; it should be clear and bright</li>
    <li>Pump or drain any water from the low end, and re-check until the paste stays brown</li>
    <li>Store removed water in a closed, labeled container for proper disposal</li>
    <li>Check fill cap, bungs, gaskets, and vent cap for a tight seal, especially after storms</li>
    <li>Don't let the tank sit nearly empty for long stretches</li>
    <li>Use a water-blocking or water-detecting dispenser filter, and look at old filters for rust or slime</li>
  </ul>
  <p>Heading into winter? Water in the tank turns to ice, and cold also brings wax problems. See <a href="{GEL_PATH}">diesel gelling: when it happens and how to prevent it</a>.</p>

  <section class="faq">
  <h2>FAQ</h2>
  {water_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{CRC672}" rel="noopener">Coordinating Research Council: Preventive Maintenance Guide for Diesel Storage and Dispensing Systems (CRC Report 672, 2016)</a></li>
    <li><a href="{CRC}" rel="noopener">Coordinating Research Council: Diesel Fuel Low Temperature Operability Guide (CRC Report 671, 2016)</a></li>
    <li><a href="{EPA16}" rel="noopener">EPA: Research shows corrosion in most diesel underground storage tanks (2016)</a></li>
    <li><a href="{DNET}" rel="noopener">DieselNet: EPA finds corrosion in ULSD storage tanks (2016)</a></li>
    <li><a href="{GILBERT}" rel="noopener">Riley Gilbert, Underground Storage Tank Corrosion: Problems and Solutions, National Tanks Conference (2018)</a></li>
    <li><a href="{STI}" rel="noopener">Steel Tank Institute: SP001 monthly inspection checklist, 7th edition</a></li>
    <li><a href="{CENEXW}" rel="noopener">Cenex: Warning signs your diesel is water-contaminated</a></li>
    <li><a href="{BELL}" rel="noopener">Bell Performance: Fuel storage tank treatment procedures</a></li>
    <li><a href="{PSAIL}" rel="noopener">Practical Sailor: Diesel biocides take on contaminated fuel</a></li>
    <li><a href="{VEEDER}" rel="noopener">Veeder-Root: Why water needs to be removed continuously</a></li>
    <li><a href="{FILLRITE}" rel="noopener">Fill-Rite: Fuel transfer filters</a></li>
    <li><a href="{FDUMP}" rel="noopener">Fuel Dump: Kolor Kut water finding paste</a></li>
    <li><a href="{OTW}" rel="noopener">Oil Tank Warehouse: Water finding paste</a></li>
    <li><a href="{MODNR}" rel="noopener">Missouri DNR: Management of petroleum storage tank wastes</a></li>
  </ul>
  <p class="note">This guide is general information. Follow product labels, your equipment manufacturer's instructions, and your state's rules for disposing of tank water.</p>
</article>
"""

water_schema = [
    {
        "@context": "https://schema.org", "@type": "Article",
        "headline": WATER_TITLE, "description": WATER_DESC,
        "datePublished": UPDATED, "dateModified": UPDATED,
        "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
        "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
        "mainEntityOfPage": DOMAIN + WATER_PATH,
    },
    {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in water_faq],
    },
]
page(WATER_PATH, WATER_TITLE, WATER_DESC, water_body, schema=water_schema, og_type="article")

# ---------------- Article: 12V transfer pumps ----------------
FRMAN = "https://goind.com.au/cdn/shop/files/GO_Manual_Fill-Rite_DC_Pumps.pdf"
FRSHEET = "https://images.oreillyauto.com/parts/img/documents/fil/fillritedcpumpsalessheet.pdf"
FR1210 = "https://www.fillrite.com/catalog/product/view/id/18304"
FR4210 = "https://www.fillrite.com/12v-dc-20-gpm-fuel-transfer-pump-with-nozzle-fr4210h"
EZ8 = "https://www.toolsid.com/gpi/ez8-8-gpm-12-v-dc-fuel-transfer-pump-mpn-137100-01.html"
M150 = "https://toolsid.com/gpi/gpi-m-150s-series-fuel-transfer-pump-2114015016.html"
G20 = "https://toolsid.com/gpi/20-gpm-12-v-dc-fuel-transfer-pump-mpn-162000-03.html"

PUMP_PATH = "/12v-fuel-transfer-pump/"
TT_PATH = "/diesel-transfer-tank/"
PUMP_TITLE = "How to Choose a 12V Fuel Transfer Pump (Fill-Rite and GPI Compared)"
PUMP_DESC = ("How to pick a 12V fuel transfer pump: flow rate, duty cycle, wiring, and which size fits a "
             "pickup transfer tank, drums, or a farm tank. Fill-Rite and GPI models compared.")

pump_faq = [
    ("What size wire does a 12V transfer pump need?",
     f"At least 12 gauge, with a fuse near the battery. Fill-Rite specifies a 30-amp fuse for its 12V pumps, and heavier wire for runs over 20 feet {src(FRMAN, 'Fill-Rite manual')}."),
    ("Can I run a 12V pump continuously?",
     f"Most can't. The common 15 and 20 GPM pumps are rated 30 minutes on, 30 minutes off (<a href=\"{FR4210}\" rel=\"noopener\">Fill-Rite FR4210H</a>; <a href=\"{M150}\" rel=\"noopener\">GPI M-150S</a>)."),
    ("Can I use the same pump for gasoline and diesel?",
     f"The models here are rated for both, but don't switch back and forth on the same tank. Mixing gasoline into diesel lowers the flash point and creates a fire hazard {src(EPRI, 'EPRI')}."),
    ("Does a bigger pump mean faster fueling?",
     "Up to a point. Your hose, filter, meter, and nozzle all limit flow, and a bigger pump draws more current from your battery."),
]
pump_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in pump_faq)

pump_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/aboveground-fuel-tanks/">Aboveground tanks</a></p>
  <h1>How to choose a 12V fuel transfer pump</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>
  {AFF_NOTE}

  <div class="answer">
    <p><strong>For a pickup transfer tank or a small farm tank, a 15 GPM pump is the usual fit. Step up to 20 GPM for bigger tanks and frequent fueling, and drop to about 8 GPM for drums and occasional use.</strong> Then check three things before you buy: the duty cycle, the fuels it's rated for, and whether your truck or battery can feed its amp draw.</p>
  </div>

  <p>Most 12-volt pumps can't run all day. The common Fill-Rite and GPI models are rated for 30 minutes on, then 30 minutes off (<a href="{FR4210}" rel="noopener">Fill-Rite FR4210H</a>; <a href="{M150}" rel="noopener">GPI M-150S</a>). That's plenty for fueling equipment, but it rules them out for long, continuous transfers.</p>

  <h2>What the specs mean</h2>
  <p><strong>Five numbers on the box decide whether a pump fits your job.</strong></p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Spec</th><th scope="col">What it tells you</th><th scope="col">What to look for</th></tr></thead>
    <tbody>
      <tr><td>Flow rate (GPM)</td><td>Maximum gallons per minute with nothing slowing it down</td><td>Real flow is lower once you add a filter, meter, long hose, or auto nozzle</td></tr>
      <tr><td>Duty cycle</td><td>How long it can run before it needs to cool</td><td>"30 on / 30 off" is typical; some small pumps are 15 on / 30 off {src(EZ8, 'GPI EZ8')}. If it overheats, a thermal switch shuts it off {src(FRMAN, 'Fill-Rite manual')}</td></tr>
      <tr><td>Amp draw and fuse</td><td>How much current it pulls from the battery</td><td>15 to 20 GPM pumps draw about 19 to 20 amps (<a href="{FR1210}" rel="noopener">Fill-Rite FR1210HN</a>; <a href="{FR4210}" rel="noopener">FR4210H</a>). Bigger pumps need heavier wiring</td></tr>
      <tr><td>Approved fuels</td><td>What it's built to pump</td><td>Most pumps in this class are rated for diesel up to B20, gasoline up to E15, and kerosene. Check before pumping anything else</td></tr>
      <tr><td>Motor listing</td><td>Whether the motor is certified for use around fuel vapor</td><td>Look for a UL or cULus motor listing for hazardous locations (<a href="{M150}" rel="noopener">GPI M-150S</a>; <a href="{FRSHEET}" rel="noopener">Fill-Rite sales sheet</a>)</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>About thermal shutoff:</strong> On Fill-Rite's 1200 and 4200 series, once the motor overheats and shuts off, you have to let it cool and then turn the switch off to reset it. Some other series reset on their own {src(FRMAN, 'Fill-Rite manual')}. If your pump quits mid-fill and won't restart, that's often why.</p>

  <h2>Common 12V pumps compared</h2>
  <p><strong>Fill-Rite and GPI make most of the 12V transfer pumps you'll find at farm stores, and their lineups line up closely by flow rate.</strong> Specs below come from each manufacturer's listing. Model numbers vary by kit (hose, nozzle, meter), so match the series.</p>
  <div class="table-wrap">
  <table class="compare">
    <thead><tr><th scope="col">Pump</th><th scope="col">Flow</th><th scope="col">Duty cycle</th><th scope="col">Electrical</th><th scope="col">Warranty</th><th scope="col">Time for 100 gal</th></tr></thead>
    <tbody>
      <tr><td><a href="{EZ8}" rel="noopener">GPI EZ8</a><br><span class="shop">{amz("GPI EZ8 12V fuel transfer pump", "Check price on Amazon")}</span></td><td>8 GPM</td><td>15 on / 30 off</td><td>20 A fuse</td><td>2 years</td><td>12.5 min</td></tr>
      <tr><td><a href="{FR1210}" rel="noopener">Fill-Rite FR1200 series</a> (e.g., FR1210)<br><span class="shop">{amz("Fill-Rite FR1210 12V fuel pump", "Check price on Amazon")}</span></td><td>15 GPM</td><td>30 on / 30 off</td><td>20 A max draw</td><td>Limited lifetime</td><td>6.7 min</td></tr>
      <tr><td><a href="{M150}" rel="noopener">GPI M-150S</a><br><span class="shop">{amz("GPI M-150S 12V fuel transfer pump", "Check price on Amazon")}</span></td><td>15 GPM</td><td>30 on / 30 off</td><td>25 A fuse</td><td>2 years</td><td>6.7 min</td></tr>
      <tr><td><a href="{FR4210}" rel="noopener">Fill-Rite FR4200 series</a> (e.g., FR4210)<br><span class="shop">{amz("Fill-Rite FR4210 12V fuel pump", "Check price on Amazon")}</span></td><td>20 GPM</td><td>30 on / 30 off</td><td>19 A max draw</td><td>Limited lifetime</td><td>5 min</td></tr>
      <tr><td><a href="{G20}" rel="noopener">GPI G20</a><br><span class="shop">{amz("GPI G20 12V fuel transfer pump", "Check price on Amazon")}</span></td><td>20 GPM</td><td>30 on / 30 off</td><td>40 A fuse</td><td>Not listed</td><td>5 min</td></tr>
      <tr><td><a href="{FRSHEET}" rel="noopener">Fill-Rite FR3200 series</a> (e.g., FR3210)<br><span class="shop">{amz("Fill-Rite FR3210 12V fuel pump", "Check price on Amazon")}</span></td><td>25 GPM</td><td>30 min rated</td><td>About 50 A</td><td>Not listed</td><td>4 min</td></tr>
    </tbody>
  </table>
  </div>
  <p>All six are listed for diesel up to B20, gasoline up to E15, and kerosene. The fill times are the best case. Real-world times run longer once you add a filter, meter, and long hose.</p>
  <ul>
    <li><strong>Fill-Rite's FR4200 series moves a third more fuel than the FR1200 at about the same amp draw</strong> {src(FRSHEET, 'Fill-Rite sales sheet')}, so it's often worth the step up for a farm tank.</li>
    <li><strong>25 GPM pumps pull about two and a half times the current</strong> of a 15 to 20 GPM pump {src(FRSHEET, 'Fill-Rite sales sheet')}. Plan for heavy wiring and a strong charging system.</li>
    <li><strong>Fill-Rite's longer warranty</strong> is a real difference from GPI's 2 years on these models.</li>
  </ul>

  <h2>Which pump for which job</h2>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Job</th><th scope="col">Size to start with</th><th scope="col">Why</th></tr></thead>
    <tbody>
      <tr><td>Drums and occasional small fills</td><td>About 8 GPM</td><td>Cheaper and lighter, and a 15-minute run is enough for a drum or two</td></tr>
      <tr><td>Pickup <a href="{TT_PATH}">transfer tank</a> (roughly 50 to 119 gallons)</td><td>15 GPM</td><td>Fills equipment fast enough, and draws about 20 amps the truck can handle</td></tr>
      <tr><td>Farm skid tank or yard tank fueling big equipment</td><td>20 GPM</td><td>Shorter fill times for large tractor and truck tanks, at about the same amp draw as 15 GPM in Fill-Rite's lineup</td></tr>
      <tr><td>High-volume fueling or long transfers</td><td>25 GPM, or an AC pump</td><td>A 12V pump's 30-minute duty cycle becomes the limit; a 120V pump may fit better if power is available</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Gasoline needs extra care.</strong> The pumps above are rated for gasoline up to E15, but pumping gasoline means more vapor and more fire risk. Use a pump with a hazardous-location motor listing, an unleaded nozzle, a grounded hose, and bond the pump to the tank or frame (<a href="{FRMAN}" rel="noopener">Fill-Rite manual</a>; <a href="{M150}" rel="noopener">GPI M-150S</a>).</p>

  <h2>Installing and wiring it</h2>
  <p><strong>Wire it straight to the battery with a fuse near the battery, use at least 12-gauge wire, and bond the pump to the tank.</strong> These come from Fill-Rite's manual for its 1200, 2400, 4200, and 4400 series {src(FRMAN, 'Fill-Rite manual')}; check your own pump's manual for its numbers.</p>
  <ol>
    <li><strong>Power from the battery.</strong> Red to positive, black to negative. Put the fuse holder as close to the battery as you can. Fill-Rite calls for a 30-amp fuse on 12V installs, 20 amps on 24V.</li>
    <li><strong>Wire size.</strong> Nothing smaller than 12 gauge. For runs longer than 20 feet, size the wire to your electrical code. Longer runs need heavier wire to avoid voltage drop.</li>
    <li><strong>Bond the pump.</strong> Use the green bonding screw and wire to connect the pump to the tank or vehicle frame. Never connect power wires to the green screw.</li>
    <li><strong>Keep the suction tube off the bottom.</strong> Fill-Rite says at least 3 inches up from the tank bottom. That keeps the pump from pulling water and sludge that settle there. See <a href="{WATER_PATH}">water in your diesel tank</a>.</li>
    <li><strong>Put a filter on the outlet.</strong> It keeps dirt and water out of the equipment you're fueling {src(FRMAN, 'Fill-Rite manual')}. Fill-Rite's standard transfer filters are 10 micron, with water-detecting versions available {src(FILLRITE, 'Fill-Rite filters')}.</li>
    <li><strong>Skip extra check or foot valves</strong> unless they have a built-in pressure relief. They can cut flow {src(FRMAN, 'Fill-Rite manual')}.</li>
  </ol>

  <h2>Common problems and fixes</h2>
  <p>From Fill-Rite's troubleshooting guide {src(FRMAN, 'Fill-Rite manual')}:</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Problem</th><th scope="col">Check, in this order</th></tr></thead>
    <tbody>
      <tr><td>Slow flow</td><td>Dirty inlet screen; leaks or kinks in the suction line; a sticking bypass valve; a plugged filter, hose, or nozzle; worn rotor and vanes; low fuel in the tank</td></tr>
      <tr><td>Won't prime</td><td>Leaks or blockage in the suction line; bypass valve stuck open; nicked or worn vanes. For vapor lock, shorten the distance from pump to fuel and remove the automatic nozzle to test</td></tr>
      <tr><td>Motor won't run</td><td>Power at the pump; a failed switch; loose or wrong wiring. If the motor or thermal protector has failed, return it; don't open the motor</td></tr>
      <tr><td>Quit mid-fill</td><td>Likely the thermal shutoff after running past the duty cycle. Let it cool; on Fill-Rite 1200 and 4200 series, turn the switch off to reset</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>A plugged filter is one of the most common causes of slow flow at farm tanks,</strong> and it often means water or microbes in the tank.</p>

  <section class="faq">
  <h2>FAQ</h2>
  {pump_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{FRMAN}" rel="noopener">Fill-Rite: DC pump owner's manual (FR1200, FR2400, FR4200, FR4400 series)</a></li>
    <li><a href="{FRSHEET}" rel="noopener">Fill-Rite: DC pump sales sheet</a></li>
    <li><a href="{FR1210}" rel="noopener">Fill-Rite: FR1210HN 12V 15 GPM pump</a></li>
    <li><a href="{FR4210}" rel="noopener">Fill-Rite: FR4210H 12V 20 GPM pump</a></li>
    <li><a href="{FILLRITE}" rel="noopener">Fill-Rite: Fuel transfer filters</a></li>
    <li><a href="{EZ8}" rel="noopener">GPI EZ8 8 GPM 12V pump (Tools ID listing)</a></li>
    <li><a href="{M150}" rel="noopener">GPI M-150S 15 GPM 12V pump (Tools ID listing)</a></li>
    <li><a href="{G20}" rel="noopener">GPI G20 20 GPM 12V pump (Tools ID listing)</a></li>
    <li><a href="{EPRI}" rel="noopener">EPRI / Southwest Research Institute: Winterizing Diesel Fuel</a></li>
  </ul>
  <p class="note">This guide is general information. Follow your pump's manual and local electrical and fire codes when installing.</p>
</article>
"""

pump_schema = [
    {
        "@context": "https://schema.org", "@type": "Article",
        "headline": PUMP_TITLE, "description": PUMP_DESC,
        "datePublished": UPDATED, "dateModified": UPDATED,
        "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
        "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
        "mainEntityOfPage": DOMAIN + PUMP_PATH,
    },
    {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in pump_faq],
    },
]
page(PUMP_PATH, PUMP_TITLE, PUMP_DESC, pump_body, schema=pump_schema, og_type="article")

# ---------------- Article: transfer tanks ----------------
JJK = "https://jjkellercompliancenetwork.com/news/knowing-the-ins-and-outs-when-transporting-diesel"
PH21 = "https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/docs/standards-rulemaking/hazmat/interpretations/75041/210001.pdf"
MOT = "https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-A/section-173.6"
SP11911 = "https://www.phmsa.dot.gov/hazmat/documents/offer/SP11911.pdf/offerserver/SP11911"
AGB = "https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/2023-08/Agricultural-Products-brochure-0203-0823.pdf"
RDS95 = "https://www.tractorsupply.com/tsc/product/rds-95-gal-l-transfer-fuel-tank-combo-diamond-plate-71799"
RDS60 = "https://www.tractorsupply.com/tsc/product/rds-60-gal-transfer-fuel-tank-combo-diamond-plate-72548-2431065"

TT_PATH = "/diesel-transfer-tank/"
TT_TITLE = "Diesel Transfer Tanks: Sizing, Legal Limits, and Setup"
TT_DESC = ("Diesel transfer tanks up to 119 gallons are lightly regulated; gasoline tanks and bigger setups are not. "
           "Sizing, payload, legal limits, and setup for pickup transfer tanks.")

tt_faq = [
    ("Do I need placards for a 100-gallon diesel transfer tank?",
     f"Under federal hazmat rules, diesel in a tank of 119 gallons or less doesn't need placards {src(JJK, 'J.J. Keller')}. Whether you need a CDL depends on your truck's weight rating and use, not just the tank. Check your state's rules."),
    ("Can I put two 100-gallon tanks in my truck?",
     f"If they're connected so fuel can flow between them, PHMSA treats them as one bulk package, which brings placards. Keep the valves between them closed in transit {src(PH21, 'PHMSA letter 21-0001')}."),
    ("Can I haul gasoline in my transfer tank?",
     f"Only if the tank is approved for gasoline. Bed-mounted gasoline tanks are built under DOT special permits with conditions such as no connecting tanks together and cutting power to the pump in transit {src(SP11911, 'DOT-SP 11911')}."),
    ("Does a half-full 150-gallon tank count as 75 gallons?",
     f"No. The rules go by the tank's capacity, not what's in it {src(JJK, 'J.J. Keller')}."),
]
tt_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in tt_faq)

tt_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/aboveground-fuel-tanks/">Aboveground tanks</a></p>
  <h1>Diesel transfer tanks: sizing, legal limits, and setup</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>
  {AFF_NOTE}

  <div class="answer">
    <p><strong>A transfer tank is a fuel tank mounted in a pickup bed or on a trailer that you pump from to fuel equipment in the field. For diesel, keeping the tank at 119 gallons or less keeps it out of most federal hazmat rules.</strong> Over 119 gallons counts as "bulk" packaging, and diesel in bulk packaging needs placards {src(JJK, 'J.J. Keller')}.</p>
  </div>
  <p>Gasoline is a different story: it's regulated much more tightly, even in small tanks. This guide covers the rules, choosing a size your truck can carry, and setting it up right.</p>

  <h2>The rules for hauling fuel in a pickup</h2>
  <p><strong>Under federal hazmat rules, what matters is the fuel and the tank's capacity, not how much is in it.</strong> A 120-gallon tank with 20 gallons in it is still a bulk package {src(JJK, 'J.J. Keller')}.</p>
  {TRANSFER_RULE_SVG}
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Situation</th><th scope="col">What the federal rules say</th></tr></thead>
    <tbody>
      <tr><td>Diesel in a tank of 119 gallons or less</td><td>Diesel with a flash point of 100&deg;F or higher can be treated as a combustible liquid, and the hazmat rules don't apply to combustible liquids in non-bulk packaging. No placards, labels, or shipping papers (<a href="{JJK}" rel="noopener">J.J. Keller</a>; <a href="{PH21}" rel="noopener">PHMSA letter 21-0001</a>)</td></tr>
      <tr><td>Diesel in a tank over 119 gallons</td><td>Bulk packaging. Placards are always required for diesel in bulk packaging {src(JJK, 'J.J. Keller')}</td></tr>
      <tr><td>Two or more diesel tanks connected together</td><td>If fuel can flow between them, PHMSA treats them as one bulk package. Keep the valves between them closed during transport {src(PH21, 'PHMSA letter 21-0001')}</td></tr>
      <tr><td>Gasoline in small containers</td><td>As "materials of trade" used in your business, up to 8 gallons per container and 440 pounds total on the vehicle {src(MOT, '49 CFR 173.6')}</td></tr>
      <tr><td>Gasoline in a bed-mounted tank</td><td>Generally needs a tank built and used under a DOT special permit. For example, Transfer Flow's permit covers tanks up to 119 gallons, requires the pump to be disconnected from power in transit, and bans connecting tanks together {src(SP11911, 'DOT-SP 11911')}</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Farms get an extra exception.</strong> Farmers hauling fuel to or from the farm within 150 miles, intrastate, can carry up to 502 gallons of liquid agricultural products per vehicle, including diesel and gasoline, with relief from some packaging, training, and emergency response rules {src(AGB, 'PHMSA agricultural brochure')}. Your state's rules still apply.</p>
  <p><strong>Check the label before you buy a tank for gasoline.</strong> Some tanks are sold as approved for diesel, gasoline, and aviation fuel {src(RDS60, 'RDS 60-gallon combo')}. A tank sold for diesel only shouldn't carry gasoline.</p>

  <h2>Choosing a tank</h2>
  <p><strong>Start with your truck's payload, not the biggest tank that fits.</strong> Diesel weighs about 6.9 pounds per gallon {src(EPRI, 'EPRI')}, so fuel adds up fast:</p>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Tank size</th><th scope="col">Weight of the fuel alone, full</th></tr></thead>
    <tbody>
      <tr><td>50 gallons</td><td>About 350 lb</td></tr>
      <tr><td>75 gallons</td><td>About 520 lb</td></tr>
      <tr><td>100 gallons</td><td>About 690 lb</td></tr>
      <tr><td>119 gallons</td><td>About 830 lb</td></tr>
    </tbody>
  </table>
  </div>
  <p>Add the empty tank, pump, toolbox contents, and anything else in the bed, and compare the total to the payload on your door sticker. A half-ton pickup can run out of payload before it runs out of bed space.</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Style</th><th scope="col">Good for</th><th scope="col">Trade-off</th></tr></thead>
    <tbody>
      <tr><td>Rectangular, against the cab</td><td>Most capacity for the footprint</td><td>Uses bed space you might want for cargo</td></tr>
      <tr><td>L-shaped</td><td>Leaves more open bed floor beside the tank</td><td>Less capacity for the same bed length</td></tr>
      <tr><td>Combo tank with built-in toolbox</td><td>Fuel and tool storage in one unit, often with a lockable fill cap and level gauge {src(RDS95, 'RDS 95-gallon L combo')}</td><td>Heavier and costs more than a plain tank</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Material:</strong> Aluminum tanks don't rust and weigh less {src(RDS95, 'RDS 95-gallon L combo')}. Steel tanks usually cost less but add weight and can rust if the coating is damaged.</p>
  <p><strong>Features worth having:</strong> internal baffles to keep fuel from sloshing, a lockable fill cap, a rollover vent, a drain plug at the bottom, and a level gauge {src(RDS60, 'RDS 60-gallon combo')}. The drain plug matters more than people think: it's the easiest way to get water out (see <a href="{WATER_PATH}">water in your diesel tank</a>).</p>
  <p><strong>Shopping:</strong> {amz("RDS transfer tank toolbox combo", "RDS combo tanks on Amazon")}, {amz("aluminum L shaped diesel transfer tank", "L-shaped transfer tanks on Amazon")}, and {amz("Fill-Rite 12V transfer tank pump kit", "Fill-Rite pump kits on Amazon")}. Check that the tank is labeled for the fuel you'll carry.</p>

  <h2>Setting it up</h2>
  <p><strong>Bolt the tank down, put a filter after the pump, bond the pump to the tank, and cut power to the pump when you drive.</strong></p>
  <ol>
    <li><strong>Mount it solid.</strong> Use the manufacturer's mounting hardware and bolt through the bed, or use tie-downs rated for the full weight. A loose tank full of fuel is a hazard in a hard stop.</li>
    <li><strong>Pick a pump that fits.</strong> For most pickup transfer tanks, a 15 GPM 12V pump is the usual fit. See <a href="{PUMP_PATH}">how to choose a 12V fuel transfer pump</a> for sizing and wiring.</li>
    <li><strong>Wire it to the battery with a fuse.</strong> Fill-Rite calls for at least 12-gauge wire and a 30-amp fuse near the battery on its 12V pumps {src(FRMAN, 'Fill-Rite manual')}.</li>
    <li><strong>Bond and ground.</strong> Connect the pump to the tank or truck frame with its bonding wire, and use a hose with a static wire (<a href="{FRMAN}" rel="noopener">Fill-Rite manual</a>; <a href="{FR4210}" rel="noopener">Fill-Rite FR4210H</a>).</li>
    <li><strong>Add a filter after the pump.</strong> It keeps dirt and water out of the equipment you fuel. A 10-micron water-detecting filter is a good default {src(FILLRITE, 'Fill-Rite filters')}.</li>
    <li><strong>Keep the suction tube off the bottom.</strong> At least 3 inches up, so it doesn't pull water and sediment {src(FRMAN, 'Fill-Rite manual')}.</li>
    <li><strong>Shut it down for the road.</strong> Turn off the pump, secure the nozzle, and for a gasoline tank under a special permit, disconnect power and keep the hose and nozzle below the permit's "safe zone" {src(SP11911, 'DOT-SP 11911')}. It's a good habit for diesel too.</li>
  </ol>

  <h2>Keeping the fuel clean</h2>
  <p><strong>Transfer tanks spend a lot of time half empty and out in the weather, which is exactly how water gets into fuel.</strong> Long stretches at a low level cause condensation, and caps, gaskets, and vents that don't seal let in rain and snow {src(CRC672, 'CRC Report 672')}.</p>
  <ul>
    <li>Check the bottom with water-finding paste every month or so, and drain any water from the bottom plug.</li>
    <li>Keep the fill cap locked and the gasket in good shape.</li>
    <li>Refill before the tank sits low for weeks, especially going into winter.</li>
    <li>In cold weather, a pickup tank is as exposed as any aboveground tank. Treat or blend the fuel early (see <a href="{GEL_PATH}">diesel gelling</a>).</li>
  </ul>

  <section class="faq">
  <h2>FAQ</h2>
  {tt_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{JJK}" rel="noopener">J.J. Keller: Knowing the ins and outs when transporting diesel</a></li>
    <li><a href="{PH21}" rel="noopener">PHMSA interpretation letter 21-0001 (2021)</a></li>
    <li><a href="{MOT}" rel="noopener">49 CFR 173.6, materials of trade (eCFR)</a></li>
    <li><a href="{SP11911}" rel="noopener">PHMSA: DOT-SP 11911, Transfer Flow special permit (2025)</a></li>
    <li><a href="{AGB}" rel="noopener">PHMSA: Transporting agricultural products brochure</a></li>
    <li><a href="{EPRI}" rel="noopener">EPRI / Southwest Research Institute: Winterizing Diesel Fuel (diesel density)</a></li>
    <li><a href="{RDS95}" rel="noopener">RDS 95-gallon L transfer tank combo (Tractor Supply)</a></li>
    <li><a href="{RDS60}" rel="noopener">RDS 60-gallon transfer tank combo (Tractor Supply)</a></li>
    <li><a href="{FRMAN}" rel="noopener">Fill-Rite: DC pump owner's manual</a></li>
    <li><a href="{FILLRITE}" rel="noopener">Fill-Rite: Fuel transfer filters</a></li>
    <li><a href="{CRC672}" rel="noopener">Coordinating Research Council: CRC Report 672 (2016)</a></li>
  </ul>
  <p class="note">This guide is general information, not legal advice. Hazmat and vehicle rules vary by state and by how the truck is used; check with your state DOT for your situation.</p>
</article>
"""

tt_schema = [
    {
        "@context": "https://schema.org", "@type": "Article",
        "headline": TT_TITLE, "description": TT_DESC,
        "datePublished": UPDATED, "dateModified": UPDATED,
        "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
        "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
        "mainEntityOfPage": DOMAIN + TT_PATH,
    },
    {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in tt_faq],
    },
]
page(TT_PATH, TT_TITLE, TT_DESC, tt_body, schema=tt_schema, og_type="article")

# ---------------- Article: winter diesel additives ----------------
PSDFS = "https://powerservice.com/psp_product/diesel-fuel-supplement-cetane-boost/"
PSDIST = "https://petroleumservicecompany.com/power-service-diesel-fuel-supplement-cetane"
HOWES = "https://petroleumservicecompany.com/howes-diesel-treat/"
PS911LBL = "https://agrotradeparts.com/c89xnrotls-powerservice911dieselfuelsupplementwithslickdiesel"
BELLPOD = "https://www.bellperformance.com/fuel-pulse-show/039"
NHTSA = "https://static.nhtsa.gov/odi/tsbs/2020/MC-10170955-0001.pdf"
CENEXWIN = "https://www.cenex.com/our-products/fuels/premium-diesel-fuels/winterized-premium-diesel"

ADD_PATH = "/winter-diesel-additive/"
ADD_TITLE = "Winter Diesel Additives: What Anti-Gel Does, When to Add It, and How Much"
ADD_DESC = ("Anti-gel only works if it's in the fuel before it clouds. When to add winter diesel additive to a bulk tank, "
            "how much, and when treated or blended fuel is the better buy.")

add_faq = [
    ("Can I add anti-gel after the fuel is already cold?",
     f"It has to go in before the fuel reaches its cloud point. Once wax has formed, a preventive anti-gel won't fix it; use an emergency product like Diesel 9-1-1 (<a href=\"{HOWES}\" rel=\"noopener\">Howes</a>; <a href=\"{POWER}\" rel=\"noopener\">Power Service</a>)."),
    ("Can I use too much?",
     f"More isn't always better. Flow improvers give smaller gains as the dose goes up {src(EPRI, 'EPRI')}, and some engine makers say to follow the additive maker's mixing directions exactly and not over-concentrate {src(NHTSA, 'NHTSA service bulletin')}."),
    ("Does winter diesel from my supplier already have anti-gel?",
     f"Often. Refiners and terminals blend and treat fuel to meet the cold-weather needs of the region where it's sold {src(CRC, 'CRC Report 671')}, and suppliers sell winterized blends with flow improvers already added {src(CENEX, 'Cenex')}. Ask your supplier what yours has, and to what temperature it's treated."),
    ("Should I add gasoline or kerosene to keep diesel from gelling?",
     f"Never gasoline: it lowers the flash point and creates a fire hazard. Kerosene-type fuel or #1 diesel is the safe way to blend {src(EPRI, 'EPRI')}."),
]
add_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in add_faq)

add_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/fuel-quality/">Fuel quality</a></p>
  <h1>Winter diesel additives: what anti-gel does, when to add it, and how much</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>
  {AFF_NOTE}

  <div class="answer">
    <p><strong>An anti-gel additive lets #2 diesel keep flowing through filters below its cloud point, but only if it's mixed into the fuel before the fuel gets cold.</strong> Once wax crystals have formed, a regular anti-gel can't undo them (<a href="{HOWES}" rel="noopener">Howes</a>; <a href="{GOLD}" rel="noopener">Gold Eagle</a>).</p>
  </div>
  <p>Most of these additives are rated to protect fuel down to around 0&deg;F {src(CENEX, 'Cenex')}. Colder than that, you need #1 diesel blended in. This guide covers what the additives actually do, how to treat a bulk tank, and when buying treated fuel is the smarter move.</p>

  <h2>What winter additives actually do</h2>
  <p><strong>"Anti-gel" on the bottle usually means a cold flow improver: it changes the size and shape of wax crystals so they don't lock together on the filter.</strong> It doesn't stop wax from forming {src(CRC, 'CRC Report 671')}.</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Ingredient type</th><th scope="col">What it does</th><th scope="col">What it can't do</th></tr></thead>
    <tbody>
      <tr><td>Cold flow improver (the main "anti-gel")</td><td>Keeps wax crystals small and needle-shaped so a porous wax layer forms on the filter instead of a solid wall</td><td>Barely changes the cloud point; most lower it only 1&ndash;3&deg;C {src(CRC, 'CRC Report 671')}</td></tr>
      <tr><td>Wax anti-settling additive</td><td>Keeps small wax crystals suspended so they don't settle into a waxy layer at the bottom of a cold tank {src(CRC, 'CRC Report 671')}</td><td>Doesn't replace a flow improver</td></tr>
      <tr><td>Pour point depressant</td><td>Lowers the temperature where fuel stops pouring, which helps pumping in bulk</td><td>Often does little for filter plugging above the pour point {src(CRC, 'CRC Report 671')}</td></tr>
      <tr><td>De-icer</td><td>Keeps small amounts of water from freezing in filters {src(PSDFS, 'Power Service')}</td><td>Doesn't get rid of free water on the tank bottom; drain that (see <a href="{WATER_PATH}">water in your diesel tank</a>)</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Two things the bottle won't tell you:</strong></p>
  <ul>
    <li><strong>Results depend on your fuel.</strong> Some fuels respond well to flow improvers and some barely respond, depending on how the refinery blended them {src(CRC, 'CRC Report 671')}. The same bottle can work great one winter and poorly the next.</li>
    <li><strong>Biodiesel blends are harder to treat.</strong> Biodiesel generally makes fuel more difficult to treat with cold flow improvers {src(CRC, 'CRC Report 671')}, which is why labels raise the dose for biodiesel blends {src(PSDFS, 'Power Service')}.</li>
  </ul>

  <h2>Treating a bulk tank</h2>
  <p><strong>Pour the additive in right before a delivery so the incoming fuel mixes it, and do it while the fuel is still well above its cloud point.</strong></p>
  <ol>
    <li><strong>Treat early.</strong> If you don't know your fuel's cloud point, start treating when lows are forecast below about 30&deg;F (<a href="{BELLPOD}" rel="noopener">Bell Performance</a>; <a href="{PSDFS}" rel="noopener">Power Service</a>). Some fuels cloud as high as +20&deg;F {src(GOLD, 'Gold Eagle')}.</li>
    <li><strong>Add it before the fuel goes in.</strong> Power Service's directions say to add the product before filling the tank {src(PSDIST, 'Power Service')}. The rush of the delivery does the mixing. An additive poured on top of a full, still tank won't spread through it well.</li>
    <li><strong>Dose for the fuel you'll have, not the fuel you have now.</strong> Figure the dose on the gallons in the tank after the delivery. If old untreated fuel is already in the tank, the dose has to cover it too.</li>
    <li><strong>Follow the label for cold snaps.</strong> Labels typically increase the dose below 0&deg;F or for biodiesel blends. Power Service, for example, doubles its rate in those conditions {src(PSDFS, 'Power Service')}.</li>
    <li><strong>Treat again with each delivery.</strong> New fuel dilutes the treatment already in the tank {src(EPRI, 'EPRI')}.</li>
  </ol>
  <p><strong>Consider buying treated fuel instead.</strong> For a big tank, it's hard to get the additive mixed evenly yourself. EPRI's guidance for large standby tanks found that adding enough additive to treat a big storage tank and making sure it's mixed often isn't worth the cost or uncertainty compared with buying fuel already made for winter {src(EPRI, 'EPRI')}. Many fuel suppliers deliver winterized or blended diesel; ask what cloud point and operability it's treated to.</p>

  <h2>What the labels say</h2>
  <p><strong>Treat rates vary a lot from brand to brand and even between bottle sizes of the same brand, so dose from the bottle in your hand.</strong> Here's what two of the most common farm-store brands publish:</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Product</th><th scope="col">What it is</th><th scope="col">Treat rate on the maker's or distributor's page</th></tr></thead>
    <tbody>
      <tr><td>Power Service Diesel Fuel Supplement + Cetane Boost (white bottle)<br><span class="shop">{amz("Power Service Diesel Fuel Supplement Cetane Boost", "Check price on Amazon")}</span></td><td>Anti-gel with cetane improver, lubricity additive, and de-icer; meant for use below +30&deg;F</td><td>16 oz bottle treats 40 gallons above 0&deg;F, 20 gallons below 0&deg;F. Drums and totes: 1 gallon per 1,500 gallons {src(PSDFS, 'Power Service')}</td></tr>
      <tr><td>Howes Diesel Treat<br><span class="shop">{amz("Howes Diesel Treat", "Check price on Amazon")}</span></td><td>Anti-gel and conditioner, alcohol-free; lowers the fuel's cold filter plugging point</td><td>1 oz per 5 gallons above 0&deg;F, 1 oz per 2.5 gallons below 0&deg;F, doubled for cars and pickups {src(HOWES, 'distributor page')}</td></tr>
      <tr><td>Power Service Diesel 9-1-1 (gray bottle)<br><span class="shop">{amz("Power Service Diesel 9-1-1", "Check price on Amazon")}</span></td><td>Emergency product for fuel that has already gelled or filters that have iced; not a preventive</td><td>80 oz per 100 gallons to reliquefy gelled fuel, then treat with an anti-gel (<a href="{PS911LBL}" rel="noopener">label directions</a>; <a href="{POWER}" rel="noopener">Power Service</a>)</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Don't mix up the white and gray bottles.</strong> The white bottle prevents gelling; the gray 9-1-1 bottle rescues fuel that's already gelled {src(POWER, 'Power Service')}. Keep one of each on hand through the winter.</p>
  <p>These are the makers' own claims, not independent tests.</p>

  <h2>Anti-gel, #1 blending, or heat?</h2>
  <p><strong>Anti-gel covers most northern winters down to about 0&deg;F. Below that, blend in #1 diesel. Heat protects the one spot that fails first: the filter.</strong></p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Option</th><th scope="col">Best for</th><th scope="col">Limits</th></tr></thead>
    <tbody>
      <tr><td>Anti-gel additive</td><td>Typical winters; tanks you can treat at each delivery</td><td>Typically effective to about 0&deg;F {src(CENEX, 'Cenex')}; must go in before the fuel clouds</td></tr>
      <tr><td>#1 diesel blend</td><td>Deep cold. Cenex suggests 70/30 #2/#1 below 35&deg;F, 30/70 deeper into winter, and straight #1 below &minus;30&deg;F {src(CENEX, 'Cenex')}</td><td>Costs more per gallon; actually lowers the cloud point, unlike additives</td></tr>
      <tr><td>Filter heater, heat tracing, insulation</td><td>Exposed dispenser filters and short runs of line, which gel before the tank does {src(CRC, 'CRC Report 671')}</td><td>Needs power at the tank</td></tr>
    </tbody>
  </table>
  </div>
  <p>For the full picture on cloud point, CFPP, and what to do if fuel already gelled, see <a href="{GEL_PATH}">diesel gelling: when it happens and how to prevent it</a>.</p>

  <section class="faq">
  <h2>FAQ</h2>
  {add_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{CRC}" rel="noopener">Coordinating Research Council: Diesel Fuel Low Temperature Operability Guide (CRC Report 671, 2016)</a></li>
    <li><a href="{EPRI}" rel="noopener">EPRI / Southwest Research Institute: Winterizing Diesel Fuel (1994)</a></li>
    <li><a href="{CENEX}" rel="noopener">Cenex: Diesel gelling and how to stop it this winter</a></li>
    <li><a href="{CENEXWIN}" rel="noopener">Cenex: Winterized premium diesel</a></li>
    <li><a href="{PSDFS}" rel="noopener">Power Service: Diesel Fuel Supplement + Cetane Boost</a></li>
    <li><a href="{POWER}" rel="noopener">Power Service: Diesel 9-1-1</a></li>
    <li><a href="{PSDIST}" rel="noopener">Petroleum Service Company: Power Service product page</a></li>
    <li><a href="{HOWES}" rel="noopener">Petroleum Service Company: Howes Diesel Treat</a></li>
    <li><a href="{PS911LBL}" rel="noopener">Diesel 9-1-1 label directions (Agro Trade Parts listing)</a></li>
    <li><a href="{BELLPOD}" rel="noopener">Bell Performance: Fuel Pulse Show episode 39</a></li>
    <li><a href="{GOLD}" rel="noopener">Gold Eagle: Five things to be aware of with diesel fuel tanks</a></li>
    <li><a href="{NHTSA}" rel="noopener">NHTSA: Manufacturer service bulletin on anti-gel and de-icer use</a></li>
  </ul>
  <p class="note">This guide is general information. Always follow the additive maker's label and your engine manufacturer's recommendations.</p>
</article>
"""

add_schema = [
    {"@context": "https://schema.org", "@type": "Article", "headline": ADD_TITLE, "description": ADD_DESC,
     "datePublished": UPDATED, "dateModified": UPDATED,
     "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
     "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
     "mainEntityOfPage": DOMAIN + ADD_PATH},
    {"@context": "https://schema.org", "@type": "FAQPage",
     "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in add_faq]},
]
page(ADD_PATH, ADD_TITLE, ADD_DESC, add_body, schema=add_schema, og_type="article")

# ---------------- Article: diesel biocides ----------------
BIOKLEEN = "https://powerservice.com/psp_product/bio-kleen-diesel-fuel-biocide/"
BIOBOR = "https://www3.epa.gov/pesticides/chem_search/ppls/065217-00001-20140319.pdf"
BELLTEST = "https://www.bellperformance.com/bell-performs-blog/fuel-tests-that-actually-predict-failure-understanding-astm-d6469-and-microbial-testing"

BIO_TITLE = "Diesel Bugs and Biocides: How to Spot Microbial Growth and Treat It"
BIO_DESC = ("Diesel \"algae\" is bacteria and fungi living in water at the bottom of the tank. How to spot it, test for it, "
            "and treat it with a biocide, step by step, without plugging every filter you own.")

bio_faq = [
    ("Is diesel algae really algae?",
     f"No. It's bacteria and fungi living in the water layer and feeding on the fuel (<a href=\"{CENEXW}\" rel=\"noopener\">Cenex</a>; <a href=\"{GILBERT}\" rel=\"noopener\">Gilbert</a>)."),
    ("Can I just add biocide and skip draining the water?",
     f"The biocide may kill what's there, but the water stays, and growth comes back once the biocide is used up. Removing water is standard practice (<a href=\"{BIOBOR}\" rel=\"noopener\">Biobor JF label</a>; <a href=\"{VEEDER}\" rel=\"noopener\">Veeder-Root</a>)."),
    ("Why are my filters plugging worse after I treated?",
     f"That's dead growth coming loose from the tank walls. Change filters as needed, drain the bottom after the product settles, and it should clear up (<a href=\"{PSAIL}\" rel=\"noopener\">Practical Sailor</a>; <a href=\"{CRC672}\" rel=\"noopener\">CRC Report 672</a>)."),
    ("Is a fuel additive the same as a biocide?",
     f"Not unless it has an EPA registration number. Only registered products can claim to kill microbes {src(PSAIL, 'Practical Sailor')}."),
]
bio_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in bio_faq)

bio_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/fuel-quality/">Fuel quality</a></p>
  <h1>Diesel bugs and biocides: how to spot microbial growth and treat it</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>
  {AFF_NOTE}

  <div class="answer">
    <p><strong>"Diesel bugs" are bacteria and fungi that live in the water at the bottom of a fuel tank and feed on the fuel. Get the water out first, then use a biocide to kill what's left, then expect to change filters as the dead growth comes loose.</strong> Microbes concentrate where fuel meets water {src(BELLTEST, 'Bell Performance')}, so without water they can't take hold.</p>
  </div>
  <p>It's more common than most owners think. In one 2018 analysis of 3,855 tank-bottom samples, about 20% tested positive for microbes {src(GILBERT, 'Gilbert, National Tanks Conference')}.</p>

  <h2>Signs you have a microbe problem</h2>
  <p><strong>The first sign is usually the filter, not the tank.</strong> Slimy or mucous-like buildup on fuel filters and needing to change them more often are the earliest warnings {src(BIOKLEEN, 'Power Service')}.</p>
  <ul>
    <li><strong>Filters plugging early,</strong> with dark slime or sludge on the old filter {src(CRC672, 'CRC Report 672')}</li>
    <li><strong>Water on the tank bottom,</strong> confirmed with water-finding paste (see <a href="{WATER_PATH}">water in your diesel tank</a>)</li>
    <li><strong>Dark, hazy fuel</strong> or visible stringy material in a clear-jar sample {src(BELL, 'Bell Performance procedures')}</li>
    <li><strong>Rust and corrosion</strong> in the tank and fittings; microbes produce acids that eat metal {src(GILBERT, 'Gilbert')}</li>
  </ul>

  <h2>How to test for it</h2>
  <p><strong>Sample from the bottom of the tank, not the top.</strong> A sample from the top can look clean while the water layer is full of growth. Pull from about 3 to 6 inches off the bottom, plus any water layer {src(BELLTEST, 'Bell Performance')}.</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Test</th><th scope="col">Speed</th><th scope="col">Good for</th><th scope="col">Limits</th></tr></thead>
    <tbody>
      <tr><td>Culture test (dip slide or petri dish)</td><td>48 to 72 hours or more</td><td>Cheap; shows whether growth is present</td><td>Only detects organisms that grow on that medium</td></tr>
      <tr><td>Quick yes/no test (immunoassay)</td><td>Minutes</td><td>Fast check in the field</td><td>Tells you if a threshold is passed, not how bad it is</td></tr>
      <tr><td>ATP test</td><td>About 5 minutes</td><td>Gives a number you can track over time</td><td>Misses dormant spores</td></tr>
    </tbody>
  </table>
  </div>
  <p class="source-line">Source: <a href="{BELLTEST}" rel="noopener">Bell Performance, citing ASTM D6469</a>. Test kits: {amz("diesel fuel microbial test kit", "fuel microbe test kits on Amazon")}.</p>
  <p><strong>How often?</strong> Quarterly testing is a reasonable baseline for stored fuel, and more often after you've had a problem {src(BELLTEST, 'Bell Performance')}. For most farm tanks, a test whenever you find water or slime is the practical minimum. For sampling and the full set of lab tests, see <a href="/test-diesel-fuel-quality/">how to test diesel fuel</a>.</p>

  <h2>How biocides work</h2>
  <p><strong>A biocide kills the microbes. It doesn't remove the water they live in, the sludge they've made, or the bodies they leave behind.</strong></p>
  <ul>
    <li><strong>They're pesticides.</strong> Any product sold as a biocide has to be registered with EPA, and using it differently from the label is a violation of federal law (<a href="{PSAIL}" rel="noopener">Practical Sailor</a>; <a href="{BIOBOR}" rel="noopener">Biobor JF label</a>). Look for the EPA registration number on the bottle. A "fuel treatment" with no registration number isn't a biocide.</li>
    <li><strong>Water-soluble vs. fuel-soluble.</strong> Water-soluble products reach the water layer where microbes live and give a faster kill. Fuel-soluble products blend more easily through the fuel and are often better for maintenance dosing {src(PSAIL, 'Practical Sailor')}. Labels differ on where to add them: Biobor JF says to blend it into the fuel only, not the water bottom {src(BIOBOR, 'Biobor JF label')}.</li>
    <li><strong>Two doses.</strong> Most labels give a higher "shock" dose for a contaminated tank and a lower maintenance dose for a clean one (<a href="{BIOKLEEN}" rel="noopener">Power Service Bio Kleen</a>; <a href="{BIOBOR}" rel="noopener">Biobor JF label</a>).</li>
    <li><strong>Dead growth still causes trouble.</strong> Killing the microbes releases slime and dead cells from the tank walls, and that surge can plug filters {src(PSAIL, 'Practical Sailor')}. A badly fouled tank usually needs the bottom cleaned out mechanically, not just treated.</li>
  </ul>

  <h2>Treating a contaminated tank, step by step</h2>
  <p><strong>Drain, dose, let it settle, drain again, then watch your filters and retest.</strong> This follows the sequence industry presenters recommend for a positive test {src(GILBERT, 'Gilbert')}.</p>
  <ol>
    <li><strong>Remove the water bottom.</strong> Pump or drain from the low end until water-finding paste stays brown. Removing excess water is standard practice before treating {src(BIOBOR, 'Biobor JF label')}. Keep the water in a closed, labeled container; don't dump it {src(MODNR, 'Missouri DNR')}.</li>
    <li><strong>Add the shock dose for the whole tank.</strong> Follow the label for a contaminated tank. Some makers say to figure the dose on a full tank even if it's partly filled {src(BELL, 'Bell Performance procedures')}. Biobor's label says to start when the tank is at least half full, never empty {src(BIOBOR, 'Biobor JF label')}.</li>
    <li><strong>Mix it in.</strong> Add it just before a delivery, or circulate the tank, so it reaches all the fuel {src(BELL, 'Bell Performance procedures')}.</li>
    <li><strong>Let it settle.</strong> Bell's procedure calls for at least 8 hours so dead microbes fall to the bottom {src(BELL, 'Bell Performance procedures')}. Follow your label's wait time.</li>
    <li><strong>Drain the bottom again.</strong> Pull off the dead material and any water that settled out {src(GILBERT, 'Gilbert')}.</li>
    <li><strong>Change filters, and keep spares.</strong> Expect more frequent filter changes for a while after treatment {src(CRC672, 'CRC Report 672')}. {amz("Fill-Rite 10 micron fuel filter", "Fill-Rite filters on Amazon")}.</li>
    <li><strong>Retest.</strong> Test again over the following weeks to confirm it worked {src(GILBERT, 'Gilbert')}. If growth comes back fast or sludge is heavy, have the tank cleaned (see <a href="/diesel-tank-cleaning/">tank cleaning and fuel polishing</a>).</li>
  </ol>

  <h2>What the labels say</h2>
  <p><strong>Dose from the label on your bottle; these are what two common biocides publish.</strong></p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Product</th><th scope="col">Shock dose (contaminated tank)</th><th scope="col">Maintenance dose (clean tank)</th><th scope="col">Notes</th></tr></thead>
    <tbody>
      <tr><td>Power Service Bio Kleen<br><span class="shop">{amz("Power Service Bio Kleen diesel biocide", "Check price on Amazon")}</span></td><td>1 oz per 20 gallons; 1 gallon per 2,500 gallons</td><td>1 oz per 55 gallons; 1 gallon per 7,000 gallons</td><td>Sold as a quick-kill biocide {src(BIOKLEEN, 'Power Service')}</td></tr>
      <tr><td>Biobor JF<br><span class="shop">{amz("Biobor JF diesel biocide", "Check price on Amazon")}</span></td><td>270 ppm (2.6 oz per 100 gallons)</td><td>135 ppm (1.3 oz per 100 gallons)</td><td>EPA Reg. No. 65217-1; blend into the fuel, not the water bottom; never exceed 1,000 ppm {src(BIOBOR, 'Biobor JF label')}</td></tr>
    </tbody>
  </table>
  </div>

  <h2>Keeping microbes from coming back</h2>
  <p><strong>Keep water out, and they can't grow.</strong> Everything in <a href="{WATER_PATH}">water in your diesel tank</a> applies:</p>
  <ul>
    <li>Check for and drain water monthly and after deliveries.</li>
    <li>Keep caps, gaskets, and vents sealed, and don't let the tank sit low for long.</li>
    <li>Use a water-blocking dispenser filter and look at old filters for slime.</li>
    <li>Consider a maintenance dose of biocide if you've had a problem before. Bell's procedure for ultra-low sulfur diesel tanks calls for a maintenance dose every 90 to 120 days {src(BELL, 'Bell Performance procedures')}.</li>
  </ul>

  <section class="faq">
  <h2>FAQ</h2>
  {bio_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{BIOBOR}" rel="noopener">Biobor JF, EPA-accepted label (EPA Reg. No. 65217-1)</a></li>
    <li><a href="{BIOKLEEN}" rel="noopener">Power Service: Bio Kleen diesel fuel biocide</a></li>
    <li><a href="{BELLTEST}" rel="noopener">Bell Performance: Fuel tests that predict failure (ASTM D6469 and microbial testing), 2026</a></li>
    <li><a href="{BELL}" rel="noopener">Bell Performance: Fuel storage tank treatment procedures</a></li>
    <li><a href="{GILBERT}" rel="noopener">Riley Gilbert, Underground Storage Tank Corrosion: Problems and Solutions, National Tanks Conference (2018)</a></li>
    <li><a href="{CRC672}" rel="noopener">Coordinating Research Council: CRC Report 672 (2016)</a></li>
    <li><a href="{PSAIL}" rel="noopener">Practical Sailor: Diesel biocides take on contaminated fuel</a></li>
    <li><a href="{VEEDER}" rel="noopener">Veeder-Root: Why water needs to be removed continuously</a></li>
    <li><a href="{CENEXW}" rel="noopener">Cenex: Warning signs your diesel is water-contaminated</a></li>
    <li><a href="{MODNR}" rel="noopener">Missouri DNR: Management of petroleum storage tank wastes</a></li>
  </ul>
  <p class="note">This guide is general information. Biocides are pesticides: read and follow the label, and wear the protection it calls for.</p>
</article>
"""

bio_schema = [
    {"@context": "https://schema.org", "@type": "Article", "headline": BIO_TITLE, "description": BIO_DESC,
     "datePublished": UPDATED, "dateModified": UPDATED,
     "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
     "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
     "mainEntityOfPage": DOMAIN + BIO_PATH},
    {"@context": "https://schema.org", "@type": "FAQPage",
     "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in bio_faq]},
]
page(BIO_PATH, BIO_TITLE, BIO_DESC, bio_body, schema=bio_schema, og_type="article")


# ---------------- How long diesel lasts ----------------
STORE_PATH = "/how-long-does-diesel-last/"
ALBERTA = "https://www1.agric.gov.ab.ca/$Department/deptdocs.nsf/all/agdex12374"
CHEVRON = "https://www.trucknews.com/products/fuels-question-answer-2/"
NRELBIO = "https://www.nrel.gov/docs/fy23osti/86939.pdf"
NFPA110 = "https://www.bellperformance.com/bell-performs-blog/what-nfpa-110-requires-for-stored-generator-fuel"
MA527 = "https://www.mass.gov/doc/117512-testing-of-diesel-fuel/download"

STORE_TITLE = "How Long Does Diesel Last in Storage? Shelf Life, Testing, and Tips"
STORE_DESC = ("Diesel kept clean, cool, and dry generally lasts 6 to 12 months, and longer with treatment and testing. "
              "What shortens it, how to tell if stored fuel is still good, and how to make it last.")

store_faq = [
    ("Is 2-year-old diesel still usable?",
     "It might be, if it was stored well. Test it first: check a bottom sample for water, haze, and growth, and have a lab test it if it matters. Don't run it in critical equipment untested."),
    ("Does off-road (red) diesel last longer than on-road diesel?",
     "The dye doesn't change how it ages. Storage conditions, water, and biodiesel content matter much more."),
    ("Can I mix old diesel with new?",
     "Small amounts of good old fuel can be blended into fresh fuel and burned. Fuel with water, slime, or sludge should be cleaned up or removed first, or it will contaminate the fresh fuel."),
    ("Do fuel stabilizers really work?",
     f"Antioxidant stabilizers slow aging but can't reverse it, so add them while the fuel is fresh {src(NRELBIO, 'NREL')}."),
]
store_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in store_faq)

store_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/fuel-quality/">Fuel quality</a></p>
  <h1>How long does diesel last in storage?</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>
  {AFF_NOTE}

  <div class="answer">
    <p><strong>Diesel kept clean, cool, and dry can generally be expected to last 6 to 12 months</strong> {src(ALBERTA, 'Alberta Agriculture')}. <strong>Chevron's guidance for emergency fuel is to use it within a year and replace it with fresh fuel, unless special precautions are taken</strong> {src(CHEVRON, 'Chevron, via Truck News')}.</p>
  </div>
  <p>That's a rule of thumb, not an expiration date. Well-kept fuel with a stabilizer and regular testing can go much longer, and fuel sitting on a water bottom in a half-empty tank can go bad faster. The diesel spec itself, ASTM D975, has no storage-stability test for #1 or #2 diesel {src(NRELBIO, 'NREL')}, so testing is how you know for sure.</p>

  <h2>What happens to diesel as it sits</h2>
  <p><strong>Stored diesel breaks down in four ways, and most of them start with water or air.</strong></p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Problem</th><th scope="col">What it does</th><th scope="col">What speeds it up</th></tr></thead>
    <tbody>
      <tr><td>Oxidation</td><td>Fuel reacts with air and forms gums, sludge, and acids that plug filters</td><td>Heat, air in a half-empty tank, and metals like copper, brass, and zinc {src(NRELBIO, 'NREL')}</td></tr>
      <tr><td>Water</td><td>Collects on the tank bottom from condensation and leaks</td><td>A low fuel level and caps or vents that don't seal {src(CRC672, 'CRC Report 672')}</td></tr>
      <tr><td>Microbes</td><td>Bacteria and fungi grow in the water layer, make slime, and plug filters {src(GILBERT, 'Gilbert')}</td><td>Water on the bottom and warm weather</td></tr>
      <tr><td>Wax settling</td><td>In cold weather, wax can settle into a layer on the bottom</td><td>Fuel stored below its cloud point {src(CRC, 'CRC Report 671')}</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Biodiesel blends need more attention.</strong> Most diesel sold today can contain up to 5% biodiesel. A B20 blend meeting the minimum spec is expected to keep its quality for up to a year in clean, dry storage, and fuels with better stability or added antioxidants lasted much longer in testing {src(NRELBIO, 'NREL')}. Antioxidants only slow aging; they can't reverse it, so they work best added when the fuel is fresh {src(NRELBIO, 'NREL')}.</p>

  <h2>How to tell if stored diesel is still good</h2>
  <p><strong>Pull a sample from the bottom of the tank into a clear jar and look at it, then check the bottom for water.</strong> Good diesel is "clear and bright" with no haze, particles, or water layer {src(CRC672, 'CRC Report 672')}. Sample jars: {amz("fuel sample bottle clear", "clear fuel sample bottles on Amazon")}.</p>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">What you see</th><th scope="col">What it likely means</th></tr></thead>
    <tbody>
      <tr><td>Clear and bright, no water</td><td>Fuel is fine to use</td></tr>
      <tr><td>Hazy or cloudy at room temperature</td><td>Water suspended in the fuel</td></tr>
      <tr><td>Water layer at the bottom of the jar</td><td>Free water in the tank; drain it (see <a href="{WATER_PATH}">water in your diesel tank</a>)</td></tr>
      <tr><td>Dark color, slime, or stringy material</td><td>Microbial growth (see <a href="{BIO_PATH}">diesel bugs and biocides</a>)</td></tr>
      <tr><td>Sediment or dark particles</td><td>Sludge from aging fuel or rust; expect filter plugging</td></tr>
    </tbody>
  </table>
  </div>
  <p>Sample from near the bottom, not the top. Water, microbes, and sediment all collect at the bottom, so a top sample can look fine while the bottom isn't {src(BELLTEST, 'Bell Performance')}. Check for a water layer in the tank itself with water-finding paste on a gauge stick: {amz("water finding paste fuel", "water-finding paste on Amazon")}.</p>
  <p><strong>For fuel that has to work, test it.</strong> Standby generators are the clearest case: NFPA 110 requires a fuel quality test at least once a year using ASTM methods, and says tanks should be sized so fuel is used within its storage life {src(NFPA110, 'Bell Performance on NFPA 110')}. A fuel lab can test water and sediment, stability, and microbes; see <a href="/test-diesel-fuel-quality/">how to test diesel fuel</a> for which tests to ask for. If fuel fails, the usual fix is to recondition or replace it, clean the tank, and change filters {src(MA527, 'Massachusetts fire code excerpt')}.</p>

  <h2>How to make stored diesel last</h2>
  <p><strong>Keep it full, cool, dry, and treated, and use the oldest fuel first.</strong></p>
  <ol>
    <li><strong>Keep the tank nearly full.</strong> Less air space means less condensation and less oxidation {src(ALBERTA, 'Alberta Agriculture')}.</li>
    <li><strong>Keep it cool and out of the sun where you can.</strong> Heat speeds up aging {src(ALBERTA, 'Alberta Agriculture')}.</li>
    <li><strong>Drain water off the bottom on a schedule,</strong> at least monthly and after deliveries (see <a href="{WATER_PATH}">water in your diesel tank</a>).</li>
    <li><strong>Add a stabilizer when the fuel is fresh,</strong> and a biocide if microbes have been a problem. Filtering the fuel periodically and adding stabilizers and biocides help store diesel longer {src(ALBERTA, 'Alberta Agriculture')}. See <a href="/diesel-fuel-stabilizer/">diesel fuel stabilizer</a> for treat rates. {amz("diesel fuel stabilizer", "Diesel stabilizers on Amazon")}.</li>
    <li><strong>Avoid copper, brass, and zinc in the fuel system.</strong> These metals speed up fuel breakdown, especially with biodiesel blends; carbon steel, aluminum, and stainless are better {src(NRELBIO, 'NREL')}.</li>
    <li><strong>Size the tank to what you use.</strong> A tank you empty a few times a year stays fresher than one that holds a two-year supply. For standby generators, that's an NFPA 110 requirement, not just good advice {src(NFPA110, 'Bell Performance on NFPA 110')}.</li>
    <li><strong>Rotate it.</strong> Burn the old fuel before adding a big load of new fuel to it, so old fuel doesn't keep getting mixed into fresh.</li>
  </ol>

  <h2>What about gasoline?</h2>
  <p><strong>Gasoline goes bad much faster.</strong> Alberta Agriculture recommends using gasoline within about a month of purchase, and expects it to stay good for at least 6 months under good storage conditions {src(ALBERTA, 'Alberta Agriculture')}. A gasoline stabilizer helps.</p>

  <p>More on keeping fuel clean: <a href="/fuel-quality/">all fuel quality guides</a>.</p>

  <section class="faq">
  <h2>FAQ</h2>
  {store_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{ALBERTA}" rel="noopener">Government of Alberta: Farm Fuel Storage and Handling, frequently asked questions (2008)</a></li>
    <li><a href="{CHEVRON}" rel="noopener">Chevron, via Truck News: Fuels question and answer (2014)</a></li>
    <li><a href="{NRELBIO}" rel="noopener">NREL: Biodiesel Handling and Use Guide, Sixth Edition</a></li>
    <li><a href="{CRC672}" rel="noopener">Coordinating Research Council: CRC Report 672 (2016)</a></li>
    <li><a href="{CRC}" rel="noopener">Coordinating Research Council: CRC Report 671 (2016)</a></li>
    <li><a href="{NFPA110}" rel="noopener">Bell Performance: What NFPA 110 requires for stored generator fuel (2026)</a></li>
    <li><a href="{BELLTEST}" rel="noopener">Bell Performance: Fuel tests that predict failure (2026)</a></li>
    <li><a href="{MA527}" rel="noopener">Massachusetts 527 CMR fire code excerpt: Testing of diesel fuel</a></li>
    <li><a href="{GILBERT}" rel="noopener">Riley Gilbert, National Tanks Conference (2018)</a></li>
  </ul>
  <p class="note">This guide is general information. For standby generators and other critical systems, follow NFPA 110, your fire code, and the equipment maker's fuel requirements.</p>
</article>
"""

store_schema = [
    {"@context": "https://schema.org", "@type": "Article", "headline": STORE_TITLE, "description": STORE_DESC,
     "datePublished": UPDATED, "dateModified": UPDATED,
     "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
     "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
     "mainEntityOfPage": DOMAIN + STORE_PATH},
    {"@context": "https://schema.org", "@type": "FAQPage",
     "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in store_faq]},
]
page(STORE_PATH, STORE_TITLE, STORE_DESC, store_body, schema=store_schema, og_type="article")


# ---------------- Article: testing diesel ----------------
TEST_PATH = "/test-diesel-fuel-quality/"
ASTM4176 = "https://www.astm.org/d4176.html"
ASTM4057 = "https://www.astm.org/d4057.html"
ASTM2709 = "https://www.astm.org/d2709.html"
ASTM6217 = "https://www.astm.org/d6217.html"
ASTM2274 = "https://www.astm.org/d2274.html"
ASTM6371 = "https://www.astm.org/d6371.html"
ASTM6469 = "https://www.astm.org/d6469.html"
ASTM7687 = "https://www.astm.org/d7687.html"
ASTM8070 = "https://www.astm.org/d8070.html"
ASTM975 = "https://www.astm.org/d975.html"

TEST_TITLE = "How to Test Diesel Fuel: Sampling, Field Checks, Lab Tests"
TEST_DESC = ("How to pull a good diesel sample, what you can check yourself with a jar and water paste, "
             "and which lab tests find water, sediment, microbes, and aging.")

test_faq = [
    ("Is a sample from the top of the tank good enough?",
     f"No. Water, microbes, and sediment collect at the bottom, so a top sample can look clean while the bottom isn't {src(BELLTEST, 'Bell Performance')}."),
    ("Do biodiesel blends need different tests?",
     f"Some lab tests do. ASTM's accelerated stability test and its particulate filtration test haven't been validated for biodiesel blends, and ASTM points to other methods for them ({src(ASTM2274, 'ASTM D2274')[1:-1]}; {src(ASTM6217, 'ASTM D6217')[1:-1]}). Most diesel can contain up to 5% biodiesel, so tell the lab what you have."),
    ("Do I need a lab, or can I test it myself?",
     "Start yourself: a clear-jar bottom sample and water paste catch most problems. Send a sample to a lab when the fuel has to work, like a standby generator, when the jar shows haze or sediment you can't explain, or before you spend money on fuel you might not need to replace."),
]
test_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in test_faq)

test_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/fuel-quality/">Fuel quality</a></p>
  <h1>How to test diesel fuel: sampling, field checks, and lab tests</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>
  {AFF_NOTE}

  <div class="answer">
    <p><strong>Start with a sample from the bottom of the tank in a clear jar, and water-finding paste on a gauge stick. Good diesel is "clear and bright," with no haze, particles, or water layer.</strong> When fuel has to work, or the jar shows something you can't explain, send a sample to a fuel lab for water and sediment, particulates, stability, cold flow, and microbes.</p>
  </div>

  <h2>What you're testing for</h2>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Problem</th><th scope="col">Quick check</th><th scope="col">More</th></tr></thead>
    <tbody>
      <tr><td>Free water</td><td>Water paste on the tank bottom; water layer in the jar</td><td><a href="{WATER_PATH}">Water in your diesel tank</a></td></tr>
      <tr><td>Microbes</td><td>Slime, dark mats, or a hazy layer where fuel meets water; field test kit</td><td><a href="{BIO_PATH}">Diesel bugs and biocides</a></td></tr>
      <tr><td>Sediment and rust</td><td>Particles in the jar; plugged filters</td><td>Lab particulate test</td></tr>
      <tr><td>Aging (oxidation)</td><td>Darkening, gums, sludge</td><td><a href="{STORE_PATH}">How long diesel lasts</a></td></tr>
      <tr><td>Cold-weather wax</td><td>Cloudiness that clears when the sample warms</td><td><a href="{GEL_PATH}">Diesel gelling</a></td></tr>
    </tbody>
  </table>
  </div>

  <h2>Step 1: Take a good sample</h2>
  <p><strong>Sample from the bottom.</strong> Water, microbes, and sediment all settle there. Pull from about 3 to 6 inches off the bottom, plus any water layer {src(BELLTEST, 'Bell Performance')}. The industry practice for doing this, including sampling free water, is ASTM D4057 {src(ASTM4057, 'ASTM D4057')}.</p>
  <ul>
    <li><strong>Use a bottom sampler</strong> lowered through a tank opening, or drain a sample from a low-point valve if your tank has one.</li>
    <li><strong>At a dispenser, also take a nozzle sample.</strong> Industry guidance for diesel dispensing sites calls for a weekly nozzle sample in a clear jar {src(CRC672, 'CRC Report 672')}.</li>
    <li><strong>Use a clean, clear glass or plastic jar</strong>, and label it with the date, tank, and where in the tank it came from. Sample jars: {amz("fuel sample bottle clear", "clear fuel sample bottles on Amazon")}.</li>
    <li><strong>Dispose of samples properly</strong> unless you're keeping them {src(CRC672, 'CRC Report 672')}.</li>
  </ul>
  <p><strong>Field note:</strong> On the tanks I service, I pull a bottom sample once a year. Water and sediment are what I find most.</p>

  <h2>Step 2: Checks you can do yourself</h2>
  <p><strong>The clear-jar check.</strong> Let the jar settle, then hold it up to the light. Good diesel is "clear and bright" with no haze or particles {src(CRC672, 'CRC Report 672')}. ASTM D4176 standardizes this check: one procedure is a quick pass/fail for contamination, the other rates the haze, and both work as field tests at storage temperature {src(ASTM4176, 'ASTM D4176')}. If the haze clears when the sample warms up, it's probably wax, not water.</p>
  <p><strong>Water paste on the tank bottom.</strong> Industry guidance is to stick the tank bottom with water-finding paste weekly, and to compare the reading with the automatic tank gauge if you have one {src(CRC672, 'CRC Report 672')}. Check before and after deliveries, too {src(CRC672, 'CRC Report 672')}. Water paste: {amz("water finding paste fuel", "water-finding paste on Amazon")}.</p>
  <p><strong>Microbe test kits.</strong> Two ASTM methods can be run in the field:</p>
  <ul>
    <li><strong>Immunoassay (ASTM D8070):</strong> screens fuel or tank water for antigens from bacteria and fungi, in the field or a lab {src(ASTM8070, 'ASTM D8070')}.</li>
    <li><strong>ATP (ASTM D7687):</strong> measures the energy molecule in living cells and gives a number you can track over time; it works as a lab or portable test {src(ASTM7687, 'ASTM D7687')}.</li>
  </ul>
  <p>Culture tests are cheaper but take 48 to 72 hours or more {src(BELLTEST, 'Bell Performance')}. ASTM's guide to microbial contamination, D6469, covers the symptoms and how to detect and control it {src(ASTM6469, 'ASTM D6469')}. Test water you drain from the tank, too {src(CRC672, 'CRC Report 672')}. Kits: {amz("diesel fuel microbial test kit", "fuel microbe test kits on Amazon")}.</p>
  <p><strong>Your filters are a test, too.</strong> Filters that clog often, or a dispenser that slows down after a delivery, point to contamination; flow should stay above 5 gallons per minute. When you change a filter, look at the old one for rust and slime {src(CRC672, 'CRC Report 672')}.</p>
  <p><strong>Field note:</strong> In the field, I mostly go by the jar and the paste. A lab is for when those turn up something they can't explain.</p>

  <h2>Step 3: Lab tests worth asking for</h2>
  <p><strong>A fuel lab runs standard ASTM methods. These are the ones that answer the usual storage questions.</strong></p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Test</th><th scope="col">ASTM method</th><th scope="col">What it tells you</th></tr></thead>
    <tbody>
      <tr><td>Water and sediment</td><td><a href="{ASTM2709}" rel="noopener">D2709</a></td><td>The percentage of free water and sediment suspended in the fuel, by centrifuge. The diesel spec allows 0.05% {src(GILBERT, 'Gilbert')}</td></tr>
      <tr><td>Particulate contamination</td><td><a href="{ASTM6217}" rel="noopener">D6217</a></td><td>The weight of particles caught by filtering the fuel. Not validated for biodiesel blends; ASTM points to D7321 for those</td></tr>
      <tr><td>Oxidation stability</td><td><a href="{ASTM2274}" rel="noopener">D2274</a></td><td>How well the fuel resists aging under accelerated conditions at 95&deg;C. For biodiesel blends, ASTM points to D7462</td></tr>
      <tr><td>Cold filter plugging point</td><td><a href="{ASTM6371}" rel="noopener">D6371</a></td><td>The temperature at which the fuel plugs a test filter, with or without flow-improver additives</td></tr>
      <tr><td>Microbial ATP</td><td><a href="{ASTM7687}" rel="noopener">D7687</a></td><td>How much living microbial growth is in the fuel or tank water</td></tr>
      <tr><td>Haze and free water</td><td><a href="{ASTM4176}" rel="noopener">D4176</a></td><td>A standardized version of the clear-jar check</td></tr>
    </tbody>
  </table>
  </div>
  <p>The specification diesel is sold against is ASTM D975, which covers seven grades of diesel {src(ASTM975, 'ASTM D975')}. It has no storage-stability test for #1 or #2 diesel {src(NRELBIO, 'NREL')}, which is why stored fuel gets tested separately. Tell the lab whether your fuel has biodiesel in it, since some methods differ for blends.</p>

  <h2>How often to test</h2>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Situation</th><th scope="col">How often</th></tr></thead>
    <tbody>
      <tr><td>Water paste on the tank bottom</td><td>Weekly at dispensing sites, and before and after deliveries {src(CRC672, 'CRC Report 672')}</td></tr>
      <tr><td>Nozzle sample in a clear jar</td><td>Weekly at dispensing sites {src(CRC672, 'CRC Report 672')}</td></tr>
      <tr><td>Microbial test</td><td>Quarterly as a baseline for stored fuel, more often after a problem {src(BELLTEST, 'Bell Performance')}</td></tr>
      <tr><td>Standby generator fuel</td><td>At least once a year by ASTM methods, under NFPA 110 {src(NFPA110, 'Bell Performance on NFPA 110')}</td></tr>
      <tr><td>Farm and yard tanks</td><td>A clear-jar bottom sample and water paste monthly and after deliveries is a reasonable minimum</td></tr>
    </tbody>
  </table>
  </div>

  <h2>What to do with the results</h2>
  <ul>
    <li><strong>Water:</strong> get it off the bottom as soon as you find it. "No detectable water is desirable" {src(CRC672, 'CRC Report 672')}. See <a href="{WATER_PATH}">water in your diesel tank</a>.</li>
    <li><strong>Microbes:</strong> remove the water first, then treat with an EPA-registered biocide. See <a href="{BIO_PATH}">diesel bugs and biocides</a>.</li>
    <li><strong>Sediment or failed stability:</strong> the usual fix is to recondition or replace the fuel, clean the tank, and change filters {src(MA527, 'Massachusetts fire code excerpt')}. See <a href="/diesel-tank-cleaning/">tank cleaning and fuel polishing</a>.</li>
    <li><strong>Cold-flow problems:</strong> see <a href="{GEL_PATH}">diesel gelling</a> and <a href="{ADD_PATH}">winter additives</a>.</li>
  </ul>

  <section class="faq">
  <h2>FAQ</h2>
  {test_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{CRC672}" rel="noopener">CRC Report 672: Preventive maintenance guide for diesel storage and dispensing systems (2016)</a></li>
    <li><a href="{ASTM4057}" rel="noopener">ASTM D4057: Manual sampling of petroleum and petroleum products</a></li>
    <li><a href="{ASTM4176}" rel="noopener">ASTM D4176: Free water and particulate contamination, visual inspection</a></li>
    <li><a href="{ASTM2709}" rel="noopener">ASTM D2709: Water and sediment in middle distillate fuels by centrifuge</a></li>
    <li><a href="{ASTM6217}" rel="noopener">ASTM D6217: Particulate contamination by laboratory filtration</a></li>
    <li><a href="{ASTM2274}" rel="noopener">ASTM D2274: Oxidation stability of distillate fuel oil</a></li>
    <li><a href="{ASTM6371}" rel="noopener">ASTM D6371: Cold filter plugging point</a></li>
    <li><a href="{ASTM6469}" rel="noopener">ASTM D6469: Guide for microbial contamination in fuels</a></li>
    <li><a href="{ASTM7687}" rel="noopener">ASTM D7687: Cellular ATP in fuel and fuel-associated water</a></li>
    <li><a href="{ASTM8070}" rel="noopener">ASTM D8070: Microbial screening by lateral flow immunoassay</a></li>
    <li><a href="{ASTM975}" rel="noopener">ASTM D975: Standard specification for diesel fuel</a></li>
    <li><a href="{BELLTEST}" rel="noopener">Bell Performance: Fuel tests that predict failure (ASTM D6469 and microbial testing)</a></li>
    <li><a href="{GILBERT}" rel="noopener">Gilbert, National Tanks Conference (2018)</a></li>
    <li><a href="{NRELBIO}" rel="noopener">NREL: Biodiesel handling and use guide</a></li>
    <li><a href="{NFPA110}" rel="noopener">Bell Performance: What NFPA 110 requires for stored generator fuel</a></li>
    <li><a href="{MA527}" rel="noopener">Massachusetts: Testing of diesel fuel (527 CMR excerpt)</a></li>
  </ul>
  <p class="note">This guide is general information. Follow your equipment manufacturer's fuel requirements and your fuel lab's sampling instructions.</p>
</article>
"""

test_schema = [{"@context": "https://schema.org", "@type": "Article", "headline": TEST_TITLE, "description": TEST_DESC,
                "datePublished": UPDATED, "dateModified": UPDATED, "mainEntityOfPage": DOMAIN + TEST_PATH}]
page(TEST_PATH, TEST_TITLE, TEST_DESC, test_body, schema=test_schema, og_type="article")


# ---------------- Article: tank cleaning and fuel polishing ----------------
CLEAN_PATH = "/diesel-tank-cleaning/"
OSHAHS = "https://www.osha.gov/storage-tanks/hazard-solutions"
OSHAWA = "https://www.osha.gov/storage-tanks/work-activities"
OSHAFARM = "https://www.osha.gov/sites/default/files/publications/OSHA3939.pdf"
C1910146 = "https://www.law.cornell.edu/cfr/text/29/1910.146"
POLPAT = "https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7883627"

CLEAN_TITLE = "Diesel Tank Cleaning and Fuel Polishing: When and How"
CLEAN_DESC = ("Fuel polishing filters the fuel in place; tank cleaning removes the sludge and water. When you need each, "
              "how they work, and why not to climb inside.")

clean_faq = [
    ("Can I clean my own fuel tank?",
     f"You can drain water off the bottom and change filters yourself. Don't go inside the tank. Most storage tanks are permit-required confined spaces, even when they're out of service {src(OSHAHS, 'OSHA')}. Interior cleaning is a job for a contractor with a confined space program."),
    ("Will an additive clean my tank?",
     f"Some multifunctional additives contain detergents that lift sludge and corrosion deposits {src(GILBERT, 'Gilbert')}. That loosened material ends up in your filters, so expect to change them. An additive won't remove a heavy sludge layer or the water under it."),
    ("How often should a tank be cleaned?",
     "There's no set schedule for a farm or fleet tank. Clean it when the signs below show up, and keep water out so it doesn't need cleaning often."),
]
clean_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in clean_faq)

clean_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/fuel-quality/">Fuel quality</a></p>
  <h1>Diesel tank cleaning and fuel polishing: when and how</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>

  <div class="answer">
    <p><strong>Fuel polishing pumps the fuel through filters and water separators and back into the tank, so you keep the fuel. Tank cleaning removes the sludge, water, and growth from the tank itself.</strong> Polish when the fuel is worth saving and the contamination is light. Clean when there's heavy sludge, the water keeps coming back, or filters keep plugging after treatment. Either way, nobody should climb into the tank.</p>
  </div>

  <h2>Signs a tank needs attention</h2>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">What you see</th><th scope="col">What it points to</th></tr></thead>
    <tbody>
      <tr><td>Filters that clog often, or a dispenser that slows after a delivery</td><td>Contamination stirred up from the bottom {src(CRC672, 'CRC Report 672')}</td></tr>
      <tr><td>Rust or slime on a used filter</td><td>Corrosion or microbial growth {src(CRC672, 'CRC Report 672')}</td></tr>
      <tr><td>Water that keeps coming back after you drain it</td><td>A leak, a bad cap or vent, or a water layer you can't reach</td></tr>
      <tr><td>Slime, mats, or heavy sediment in a bottom sample</td><td>Growth or sludge on the tank bottom (see <a href="{TEST_PATH}">how to test diesel fuel</a>)</td></tr>
      <tr><td>Filters still plugging weeks after a biocide treatment</td><td>Dead growth still coming off the walls; a badly infected tank usually needs the bottom material removed mechanically {src(PSAIL, 'Practical Sailor')}</td></tr>
    </tbody>
  </table>
  </div>

  <h2>Polishing or cleaning?</h2>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col"></th><th scope="col">Fuel polishing</th><th scope="col">Tank cleaning</th></tr></thead>
    <tbody>
      <tr><td>What it does</td><td>Filters and dewaters the fuel while it stays in the tank</td><td>Removes the fuel, then the water, sludge, and growth from the tank</td></tr>
      <tr><td>Good for</td><td>Light contamination, water and particles in the fuel, standby fuel you want to keep usable</td><td>Heavy sludge, recurring water, a microbial problem that treatment didn't fix</td></tr>
      <tr><td>Limits</td><td>Doesn't remove sludge stuck to the walls and bottom</td><td>More downtime and cost; the fuel has to go somewhere while it's done</td></tr>
    </tbody>
  </table>
  </div>
  <p>For a small farm tank with bad fuel, it's often simpler to have the fuel and bottoms pumped out and start over. Your fuel supplier can often pump the tank out {src(CENEXW, 'Cenex')}.</p>
  <p><strong>Field note:</strong> When I find a bad tank, the usual call is to have it pumped and cleaned. When one gets opened up, I see all of it: sludge, rust scale, and microbial mats.</p>

  <h2>How fuel polishing works</h2>
  <p><strong>A polishing unit pulls fuel from the tank, runs it through a filter and water separator, and returns it to the tank, over and over.</strong> Fuel polishing is used to clean and filter fuel in tanks that are contaminated or at risk of it; a typical unit has a primary filter and water separator, a pump, and a secondary filter and water separator {src(POLPAT, 'U.S. Patent 7,883,627')}.</p>
  <ul>
    <li><strong>Draw from the bottom.</strong> That's where water and sediment are. The goal is to move fuel across the bottom, not just through the middle of the tank.</li>
    <li><strong>Drain the separator.</strong> The water it catches has to be emptied and disposed of properly.</li>
    <li><strong>Test before and after</strong> so you know it worked (see <a href="{TEST_PATH}">how to test diesel fuel</a>).</li>
  </ul>

  <h2>How tank cleaning works</h2>
  <p><strong>Tank cleaning is a contractor job with a set sequence.</strong> OSHA's guidance on tank cleaning covers a pre-cleaning site review, degassing and vapor control, removing the product, disposal, and a safety check before the tank goes back into service {src(OSHAWA, 'OSHA')}.</p>
  <ol>
    <li><strong>Remove the usable fuel</strong>, usually by pumping it through filters into temporary storage. Removing product calls for controlling ignition sources and bonding and grounding the equipment {src(OSHAWA, 'OSHA')}.</li>
    <li><strong>Remove the water and sludge</strong> from the bottom.</li>
    <li><strong>Clean the interior</strong>, from outside the tank where possible, or by trained entrants under a confined space permit.</li>
    <li><strong>Check the tank before it goes back in service.</strong> OSHA calls for a recommissioning safety check using a written checklist signed by qualified people {src(OSHAWA, 'OSHA')}.</li>
    <li><strong>Return or replace the fuel</strong>, and change the filters.</li>
  </ol>
  <p><strong>Ask where the waste goes.</strong> Tank-bottom water is petroleum-contaminated and can count as hazardous waste. Don't let it go on the ground or down a drain {src(MODNR, 'Missouri DNR')}. A contractor should tell you how sludge and water will be handled.</p>
  <p><strong>Field note:</strong> Owners draining tank bottoms onto the ground is something I still run into. Don't do it. Catch it in a closed, labeled container and get it disposed of properly.</p>

  <h2>Never climb into a fuel tank</h2>
  <p><strong>"Because they may contain hazards when taken out of service, most storage tanks will be considered Permit-Required Confined Spaces"</strong> {src(OSHAHS, 'OSHA')}. The hazards include vapors, hazardous gases, and an atmosphere with too little or too much oxygen, which can cause serious injury or death {src(OSHAHS, 'OSHA')}.</p>
  <ul>
    <li><strong>What counts as a confined space:</strong> a space big enough to enter and work in, with limited ways in and out, and not meant for continuous occupancy. Tanks are the first example the rule gives {src(C1910146, '29 CFR 1910.146')}.</li>
    <li><strong>A hazardous atmosphere</strong> includes flammable vapor over 10% of its lower flammable limit, or oxygen below 19.5% or above 23.5% {src(C1910146, '29 CFR 1910.146')}.</li>
    <li><strong>On farms:</strong> OSHA's confined space standard doesn't apply to agricultural operations, but OSHA points to it as the guide for preventing deaths, and the General Duty Clause still requires a workplace free from recognized hazards {src(OSHAFARM, 'OSHA Fatal Facts No. 16')}. OSHA's farm example is a worker who died from a hazardous atmosphere inside a storage tank that wasn't marked as a confined space {src(OSHAFARM, 'OSHA')}.</li>
  </ul>
  <p>If a tank needs interior work, hire a contractor with a confined space program and rescue plan.</p>

  <h2>After the job</h2>
  <ul>
    <li><strong>Let it settle.</strong> Mixing or circulating a tank kicks sludge up off the bottom; one fuel treatment maker says to let fuel settle at least 8 hours before use {src(BELL, 'Bell Performance')}.</li>
    <li><strong>Expect to change filters</strong> for a while, especially after a biocide treatment {src(CRC672, 'CRC Report 672')}.</li>
    <li><strong>Keep water out</strong> so you don't have to do this again soon: tight caps and vents, and water checks before and after deliveries {src(CRC672, 'CRC Report 672')}. See <a href="{WATER_PATH}">water in your diesel tank</a>.</li>
    <li><strong>Treat for microbes</strong> if they were the problem. See <a href="{BIO_PATH}">diesel bugs and biocides</a>.</li>
  </ul>

  <section class="faq">
  <h2>FAQ</h2>
  {clean_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{OSHAHS}" rel="noopener">OSHA: Storage tanks, hazards and solutions</a></li>
    <li><a href="{OSHAWA}" rel="noopener">OSHA: Major work activities for tank cleaning operations</a></li>
    <li><a href="{C1910146}" rel="noopener">29 CFR 1910.146, permit-required confined spaces (Cornell LII)</a></li>
    <li><a href="{OSHAFARM}" rel="noopener">OSHA Fatal Facts No. 16: Confined space entry on a farm (2018)</a></li>
    <li><a href="{CRC672}" rel="noopener">CRC Report 672: Preventive maintenance guide for diesel storage and dispensing systems (2016)</a></li>
    <li><a href="{PSAIL}" rel="noopener">Practical Sailor: Diesel biocides take on contaminated fuel</a></li>
    <li><a href="{CENEXW}" rel="noopener">Cenex: Water-contaminated diesel</a></li>
    <li><a href="{MODNR}" rel="noopener">Missouri DNR: Management of petroleum storage tank wastes</a></li>
    <li><a href="{GILBERT}" rel="noopener">Gilbert, National Tanks Conference (2018)</a></li>
    <li><a href="{BELL}" rel="noopener">Bell Performance: Fuel storage tank treatment recommendations (2014)</a></li>
    <li><a href="{POLPAT}" rel="noopener">U.S. Patent 7,883,627: Automated fuel polishing system</a></li>
  </ul>
  <p class="note">This guide is general information. Tank entry and waste disposal are regulated; follow OSHA, your state, and your contractor's procedures.</p>
</article>
"""

clean_schema = [{"@context": "https://schema.org", "@type": "Article", "headline": CLEAN_TITLE, "description": CLEAN_DESC,
                 "datePublished": UPDATED, "dateModified": UPDATED, "mainEntityOfPage": DOMAIN + CLEAN_PATH}]
page(CLEAN_PATH, CLEAN_TITLE, CLEAN_DESC, clean_body, schema=clean_schema, og_type="article")


# ---------------- Article: diesel fuel stabilizer ----------------
STAB_PATH = "/diesel-fuel-stabilizer/"
STABIL = "https://www.goldeagle.com/product/diesel-formula-sta-bil-fuel-stabilizer/"
DEEZOL = "https://www.bellperformance.com/dee-zol-life"
BELLB20 = "https://www.bellperformance.com/bell-performs-blog/biodiesel-stability-why-b20-goes-bad-faster-in-storage"

STAB_TITLE = "Diesel Fuel Stabilizer: When You Need It and How Much to Add"
STAB_DESC = ("What a diesel stabilizer does and doesn't do, when stored fuel needs one, label treat rates "
             "for bulk tanks, and biodiesel blends.")

stab_faq = [
    ("Is a stabilizer the same as anti-gel?",
     f"No. A stabilizer slows the fuel's aging in storage. Anti-gel keeps wax from plugging filters in cold weather. Some products do both, but check the label. See <a href=\"{ADD_PATH}\">winter diesel additives</a>."),
    ("Does a stabilizer kill microbes?",
     f"Not unless it's also an EPA-registered biocide, with a registration number on the label. Microbes are a separate problem with a separate fix; see <a href=\"{BIO_PATH}\">diesel bugs and biocides</a>."),
    ("Can a stabilizer bring old fuel back?",
     f"No. Antioxidants slow aging but can't reverse it {src(NRELBIO, 'NREL')}. Test old fuel before you decide to keep it; see <a href=\"{TEST_PATH}\">how to test diesel fuel</a>."),
    ("Is more stabilizer better?",
     f"No. Use the label rate. STA-BIL's diesel label, for one, says \"DO NOT OVERTREAT\" {src(STABIL, 'Gold Eagle')}."),
]
stab_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in stab_faq)

stab_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/fuel-quality/">Fuel quality</a></p>
  <h1>Diesel fuel stabilizer: when you need it and how much to add</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>
  {AFF_NOTE}

  <div class="answer">
    <p><strong>A diesel stabilizer slows the oxidation that turns stored fuel dark and gummy. It only works if you add it while the fuel is fresh, because it can't reverse aging that has already happened</strong> {src(NRELBIO, 'NREL')}. Use one when fuel will sit longer than you'd normally burn through it, and follow the label rate for storage.</p>
  </div>

  <h2>What a stabilizer does, and what it doesn't</h2>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Does</th><th scope="col">Doesn't</th></tr></thead>
    <tbody>
      <tr><td>Slows oxidation, the reaction that forms gums, sludge, and sediment as fuel ages {src(DEEZOL, 'Bell Performance')}</td><td>Reverse aging in fuel that's already gone bad {src(NRELBIO, 'NREL')}</td></tr>
      <tr><td>Helps stored fuel stay usable longer, alongside filtering and keeping water out {src(ALBERTA, 'Alberta Agriculture')}</td><td>Remove water. Some products push water out of the fuel so it drops to the bottom {src(STABIL, 'Gold Eagle')}, but you still have to drain it</td></tr>
      <tr><td></td><td>Kill microbes, unless it's also an EPA-registered biocide</td></tr>
      <tr><td></td><td>Prevent gelling, unless it's also an anti-gel</td></tr>
    </tbody>
  </table>
  </div>
  <p>Diesel today has less natural protection to start with. The hydrotreating that takes sulfur out of ultra-low sulfur diesel also removes naturally occurring antioxidants, according to one fuel treatment maker {src(BELLB20, 'Bell Performance')}.</p>

  <h2>When stored diesel needs one</h2>
  <ul>
    <li><strong>Fuel that sits for months:</strong> seasonal equipment, a farm tank filled in spring for fall, or a tank sized bigger than you use. See <a href="{STORE_PATH}">how long diesel lasts</a> for typical shelf life.</li>
    <li><strong>Standby generators.</strong> That fuel sits the longest and has to work when it's needed. NFPA 110 also requires a yearly fuel quality test {src(NFPA110, 'Bell Performance on NFPA 110')}.</li>
    <li><strong>Biodiesel blends.</strong> Blends need more attention in storage, and added antioxidants extended their life in testing {src(NRELBIO, 'NREL')}.</li>
  </ul>
  <p><strong>Fuel you burn within a few months usually doesn't need it</strong> if the tank is kept full, dry, and clean. A stabilizer is cheap insurance, not a substitute for keeping water out.</p>

  <h2>Label treat rates, worked out for bulk tanks</h2>
  <p><strong>Treat rates vary a lot between products, so always use the label on the product you buy.</strong> Two diesel stabilizers with published rates, as examples:</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Product</th><th scope="col">Label rate</th><th scope="col">500-gallon tank</th><th scope="col">1,000-gallon tank</th></tr></thead>
    <tbody>
      <tr><td>STA-BIL Diesel Formula, storage rate {src(STABIL, 'Gold Eagle')}</td><td>1 oz per 5 gallons</td><td>100 oz (about 3 qt)</td><td>200 oz (about 1.6 gal)</td></tr>
      <tr><td>STA-BIL Diesel Formula, every-fill rate {src(STABIL, 'Gold Eagle')}</td><td>1 oz per 10 gallons</td><td>50 oz</td><td>100 oz</td></tr>
      <tr><td>Bell Performance Dee-Zol Life {src(BELL, 'Bell Performance')}</td><td>1 gallon per 2,000 gallons (about 1 oz per 15&ndash;16 gallons)</td><td>32 oz (1 qt)</td><td>64 oz (&frac12; gal)</td></tr>
      <tr><td>Bell Performance Bio Dee-Zol Life, for B20 {src(BELLB20, 'Bell Performance')}</td><td>1 oz per 10 gallons</td><td>50 oz</td><td>100 oz</td></tr>
    </tbody>
  </table>
  </div>
  <p class="source-line">Rates are from the makers' labels and pages; check the current label before you buy. Products: {amz("STA-BIL Diesel Formula fuel stabilizer", "STA-BIL Diesel on Amazon")}; {amz("Bell Performance Dee-Zol Life", "Dee-Zol Life on Amazon")}.</p>
  <p><strong>Compare by cost per gallon treated, not bottle price.</strong> A bottle with a low treat rate can cost more and still treat more fuel.</p>

  <h2>How to add it to a bulk tank</h2>
  <ol>
    <li><strong>Add it to fresh fuel, ideally right before or during a delivery,</strong> so the incoming fuel mixes it in. Antioxidants work best added when the fuel is fresh {src(NRELBIO, 'NREL')}.</li>
    <li><strong>Drain any water off the bottom first.</strong> See <a href="{WATER_PATH}">water in your diesel tank</a>.</li>
    <li><strong>Dose for the whole tank,</strong> using the tank's capacity, not just the gallons delivered, if the old fuel was never treated.</li>
    <li><strong>Write down the date and amount</strong> so you know when it was last treated.</li>
  </ol>

  <h2>Biodiesel blends need the right product</h2>
  <p><strong>Most diesel can contain up to 5% biodiesel, and higher blends like B20 age differently.</strong> One fuel treatment maker says the traditional antioxidants used in petroleum fuels, hindered phenols like BHT and TBHQ, weren't designed to fully protect biodiesel, and sells a separate biodiesel stabilizer {src(BELLB20, 'Bell Performance')}. That's a maker's claim, so treat it as a reason to check the label for biodiesel use, not as settled fact. NREL's testing found fuels with added antioxidants lasted much longer in storage {src(NRELBIO, 'NREL')}.</p>
  <p>Avoid copper, brass, and zinc in the fuel system; they speed up breakdown, especially with biodiesel blends {src(NRELBIO, 'NREL')}.</p>

  <section class="faq">
  <h2>FAQ</h2>
  {stab_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{NRELBIO}" rel="noopener">NREL: Biodiesel handling and use guide</a></li>
    <li><a href="{ALBERTA}" rel="noopener">Alberta Agriculture: Storing fuel on the farm</a></li>
    <li><a href="{STABIL}" rel="noopener">Gold Eagle: Diesel Formula STA-BIL product page and directions</a></li>
    <li><a href="{DEEZOL}" rel="noopener">Bell Performance: Dee-Zol Life product page</a></li>
    <li><a href="{BELL}" rel="noopener">Bell Performance: Fuel storage tank treatment recommendations (2014)</a></li>
    <li><a href="{BELLB20}" rel="noopener">Bell Performance: Biodiesel stability and B20 in storage (2026)</a></li>
    <li><a href="{NFPA110}" rel="noopener">Bell Performance: What NFPA 110 requires for stored generator fuel</a></li>
  </ul>
  <p class="note">This guide is general information. We haven't lab-tested these products; rates come from the makers. Follow the label on the product you use.</p>
</article>
"""

stab_schema = [{"@context": "https://schema.org", "@type": "Article", "headline": STAB_TITLE, "description": STAB_DESC,
                "datePublished": UPDATED, "dateModified": UPDATED, "mainEntityOfPage": DOMAIN + STAB_PATH}]
page(STAB_PATH, STAB_TITLE, STAB_DESC, stab_body, schema=stab_schema, og_type="article")

# ---------------- Fuel quality hub ----------------
FQ_PATH = "/fuel-quality/"
FQ_TITLE = "Fuel Quality Guides: Keeping Stored Diesel Clean, Dry, and Usable"
FQ_DESC = ("Guides to the problems that ruin stored diesel: water, microbes, cold-weather gelling, and old fuel. "
           "Start with the symptom you're seeing.")
FQ_GUIDES = [
    (WATER_PATH, "Water in your diesel tank", "How water gets in, how to check for it with paste or a clear jar, how to get it out, and how to keep it out."),
    (BIO_PATH, "Diesel bugs and biocides", "How to spot microbial growth, test for it, and treat a tank step by step without plugging every filter."),
    (STORE_PATH, "How long does diesel last in storage?", "Shelf life, what makes fuel go bad, how to tell if it's still good, and how to make it last."),
    (TEST_PATH, "How to test diesel fuel", "Taking a good bottom sample, the checks you can do yourself, and which lab tests to ask for."),
    (STAB_PATH, "Diesel fuel stabilizer", "What a stabilizer does and doesn't do, when stored fuel needs one, and label treat rates for bulk tanks."),
    (CLEAN_PATH, "Tank cleaning and fuel polishing", "When to polish the fuel and when to clean the tank, how each works, and why nobody should climb inside."),
    (GEL_PATH, "Diesel gelling: when it happens and how to prevent it", "Cloud point, CFPP, and pour point explained, why bulk tanks gel first, and a winter checklist."),
    (ADD_PATH, "Winter diesel additives", "How anti-gel works, how to treat a bulk tank before the cold, label treat rates, and when blending makes more sense."),
]
fq_cards = "\n".join(
    f'    <li><a class="guide" href="{p}"><span class="card-title">{t}</span><p>{d}</p></a></li>' for p, t, d in FQ_GUIDES)
fq_body = f"""
<div class="wrap">
  <h1>Fuel quality</h1>
  <p class="lede">Most stored-fuel problems come down to four things: water, microbes, cold, and time. These guides cover how to spot each one in your tank and what to do about it.</p>

  <h2>Start with what you're seeing</h2>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">What you're seeing</th><th scope="col">Where to start</th></tr></thead>
    <tbody>
      <tr><td>Water on the gauge stick or in a sample jar</td><td><a href="{WATER_PATH}">Water in your diesel tank</a></td></tr>
      <tr><td>Slime on filters, or filters plugging early</td><td><a href="{BIO_PATH}">Diesel bugs and biocides</a></td></tr>
      <tr><td>Fuel that's been sitting for months</td><td><a href="{STORE_PATH}">How long diesel lasts in storage</a></td></tr>
      <tr><td>Cloudy fuel or plugged filters in cold weather</td><td><a href="{GEL_PATH}">Diesel gelling</a></td></tr>
      <tr><td>Getting a tank ready for winter</td><td><a href="{ADD_PATH}">Winter diesel additives</a></td></tr>
    </tbody>
  </table>
  </div>

  <h2>All fuel quality guides</h2>
  <ul class="guide-list">
{fq_cards}
  </ul>
</div>
"""
fq_schema = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": FQ_TITLE, "description": FQ_DESC,
              "url": DOMAIN + FQ_PATH,
              "hasPart": [{"@type": "Article", "name": t, "url": DOMAIN + p} for p, t, _ in FQ_GUIDES]}]
page(FQ_PATH, FQ_TITLE, FQ_DESC, fq_body, schema=fq_schema)



# ---------------- Anti-siphon valves ----------------
ASV_PATH = "/anti-siphon-valve/"
PEIASV = "https://pei.org/?p=11463"
FLDEP = "https://floridadep.gov/sites/default/files/BlockValvesandAntiSiphonValves_2023_0.pdf"
NCDEQ = "https://www.deq.nc.gov/waste-management/dwm/ust/pib/pib-guidance-docs/memo-anti-siphon-valves-marinas/open"
NMAC = "https://regulations.justia.com/states/new-mexico/title-20/chapter-5/part-109/section-20-5-109-902/"
FREEPORT = "https://www.freeporttx.gov/page/open/2729/0/ABOVEGROUND%20STORAGE%20TANKS%20Flammable%20Liquids.pdf"
NESFM = "https://sfm.nebraska.gov/sites/default/files/doc/nfpa395_0.pdf"
OPWASV = "https://www.opwglobal.com/products/us/ast-equipment/anti-siphon-valves/opw-199asv-anti-siphon-valve"
MORASV = "https://yodify.com/Products/PzAqG/Fig-910-Anti-Siphon-Valve"
FFSASV = "https://dv.franklinfueling.com/en/products/service-station-hardware/aboveground-storage-tank-equipment/anti-syphon-valves/"
ELAFLEX = "https://elaflex.com.au/dokumente/download/ElaflexInformation/ELAFLEX_Information_6.07E.pdf"

ASV_TITLE = "Anti-Siphon Valves for Fuel Tanks: How They Work and When You Need One"
ASV_DESC = ("An anti-siphon valve keeps fuel from draining out of an aboveground tank if a line breaks. How it works, "
            "when codes require one, how to pick the head setting, and why it can make a pump struggle.")

asv_faq = [
    ("Do I need an anti-siphon valve if my pump is on top of the tank?",
     f"If the hose or piping runs below the top of the tank, fire code checklists still call for one {src(CAZ, 'Central Arizona Fire')}. Farm rules can differ: Nebraska allows a self-closing nozzle instead {src(NESFM, 'Nebraska State Fire Marshal')}."),
    ("Is an anti-siphon valve the same as a check valve?",
     f"A spring-loaded anti-siphon valve is a type of check valve, but it's set to hold back a specific head of fuel and usually includes thermal relief (<a href=\"{PEIASV}\" rel=\"noopener\">PEI</a>; <a href=\"{MORASV}\" rel=\"noopener\">Morrison Bros.</a>)."),
    ("Does it need to be tested?",
     f"Florida's rules have no annual test requirement for anti-siphon valves, but manufacturers may have their own {src(FLDEP, 'Florida DEP')}."),
]
asv_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in asv_faq)

asv_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/aboveground-fuel-tanks/">Aboveground tanks</a></p>
  <h1>Anti-siphon valves for fuel tanks: how they work and when you need one</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>
  {AFF_NOTE}

  <div class="answer">
    <p><strong>An anti-siphon valve is a normally closed valve in the outlet piping of an aboveground tank. It keeps fuel from flowing or siphoning out of the tank if a line breaks, and opens only when the pump runs</strong> {src(PEIASV, 'PEI')}. <strong>You generally need one whenever the fuel level in the tank sits higher than any part of the piping or the dispenser.</strong></p>
  </div>
  <p>The fire code language many local fire departments use reads: "Approved antisiphon devices shall be installed in each external pipe connected to the tank when the pipe extends below the level of the top of the tank" {src(CAZ, 'Central Arizona Fire and Medical Authority checklist, International Fire Code')}.</p>

  <h2>How a tank siphons, and how the valve stops it</h2>
  <p><strong>If the fuel level in the tank is higher than the pipe or dispenser, gravity pushes fuel toward the low point. When a line breaks, it keeps coming until the tank drains down to the level of the break.</strong> PEI puts it simply: fuel in an elevated tank will try to flow out, so you need a positive shutoff except when you mean to pump {src(PEIASV, 'PEI')}.</p>
  <p>This happens even when the piping leaves through the top of the tank. Once the line is full of fuel, it works like a siphon hose. A tank on a stand, a tank on higher ground than the dispenser, and piping that runs down a hill or to a dock are all common setups that do this.</p>
  {ASV_SVG}
  <p><strong>The valve holds a spring-loaded poppet closed against that gravity pressure.</strong> When the pump starts, it overcomes the spring and fuel flows. When the pump stops, the spring closes the valve again {src(OPWASV, 'OPW')}. Most also have a built-in relief for pressure from fuel expanding in a sun-warmed line (<a href="{FFSASV}" rel="noopener">Franklin Fueling Systems</a>; <a href="{MORASV}" rel="noopener">Morrison Bros.</a>).</p>

  <h2>When codes require one</h2>
  <p><strong>Fire codes, NFPA 30A, and several state tank rules all require an anti-siphon valve where an aboveground tank creates gravity head on the piping.</strong> Your local fire marshal decides which code edition applies.</p>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Rule</th><th scope="col">What it says</th></tr></thead>
    <tbody>
      <tr><td>International Fire Code (as used on local permit checklists)</td><td>Antisiphon devices are required in each external pipe connected to the tank when the pipe extends below the top of the tank (<a href="{CAZ}" rel="noopener">Central Arizona Fire</a>; <a href="{FREEPORT}" rel="noopener">Freeport, TX Fire Marshal</a>)</td></tr>
      <tr><td>NFPA 30A (2021), Section 11.2</td><td>Referenced by Florida as the standard for installing and maintaining anti-siphon valves {src(FLDEP, 'Florida DEP')}</td></tr>
      <tr><td>PEI RP200 (2019), Section 7</td><td>Industry practice for installing aboveground tank systems, also referenced by Florida {src(FLDEP, 'Florida DEP')}</td></tr>
      <tr><td>PEI RP1000, Section 4.4 (marinas)</td><td>Where product piping is below the tank's liquid level, use a normally closed solenoid valve that opens and closes with the pump {src(NCDEQ, 'NC DEQ')}</td></tr>
      <tr><td>New Mexico 20.5.109.902</td><td>Tanks that create gravity head on dispensers or piping need an anti-siphon or solenoid valve, adjusted so fuel can't flow or siphon out if the piping fails {src(NMAC, 'NMAC')}</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Valve order matters.</strong> Florida's rule spells out the sequence: tank, then block (shutoff) valve, then anti-siphon valve {src(FLDEP, 'Florida DEP')}. PEI describes the same placement: downstream of the block valve, outside the tank shell {src(PEIASV, 'PEI')}.</p>
  <p><strong>Farm tanks.</strong> Nebraska's farm tank guidance, based on NFPA 395, says a pump discharge must have an effective anti-siphoning device or a self-closing nozzle on the hose, and siphons are prohibited {src(NESFM, 'Nebraska State Fire Marshal')}. Check with your state: farm rules vary a lot.</p>

  <h2>Types of anti-siphon valves</h2>
  <p><strong>There are three main types: spring-loaded mechanical valves, normally closed solenoid valves, and siphon breakers</strong> {src(PEIASV, 'PEI')}.</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Type</th><th scope="col">How it works</th><th scope="col">Where it fits</th></tr></thead>
    <tbody>
      <tr><td>Spring-loaded (mechanical)</td><td>A spring holds the valve shut; pump suction or pressure opens it</td><td>The most common type on farm, fleet, and generator tanks</td></tr>
      <tr><td>Normally closed solenoid</td><td>Wired to the pump so it opens and closes with the pump motor</td><td>Required for marinas under PEI RP1000; PEI says mechanical valves aren't recommended there (<a href="{PEIASV}" rel="noopener">PEI</a>; <a href="{NCDEQ}" rel="noopener">NC DEQ</a>)</td></tr>
      <tr><td>Siphon breaker</td><td>A normally open solenoid at the high point of the pipe. It closes while the pump runs and opens to let air in and break the siphon when the pump stops</td><td>Piping that leaves through the top of the tank {src(PEIASV, 'PEI')}</td></tr>
    </tbody>
  </table>
  </div>

  <h2>Picking the head setting</h2>
  <p><strong>Spring-loaded valves are rated in feet of head. Pick the range that covers the height from the tank's highest fuel level down to the lowest point in the piping.</strong> One maker's guide calculates it as the height of the maximum liquid level minus the height of the lowest point of the delivery pipework {src(ELAFLEX, 'Elaflex')}.</p>
  <p>Common ranges are 0 to 5, 5 to 10, 10 to 15, and 15 to 20 feet of water column {src(MORASV, 'Morrison Bros.')}. OPW's 199ASV comes in four factory-set ranges, and OPW says not to field-adjust it {src(OPWASV, 'OPW')}. Some others are adjustable and lock once set {src(FFSASV, 'Franklin Fueling Systems')}.</p>
  <p><strong>Example:</strong> A tank on a stand with a full fuel level 9 feet above the ground, feeding a dispenser whose lowest piping is at ground level, has about 9 feet of head. That calls for the 5 to 10 foot range.</p>
  <p><strong>Field note:</strong> Morrison and OPW are the two brands I install. Both are widely stocked by fuel equipment distributors. Shop: <span class="shop">{amz("Morrison Bros anti siphon valve", "Morrison anti-siphon valves on Amazon")}</span> · <span class="shop">{amz("OPW 199ASV anti siphon valve", "OPW anti-siphon valves on Amazon")}</span></p>

  <h2>Installing it</h2>
  <ul>
    <li><strong>Put it after the shutoff valve:</strong> tank, block valve, then anti-siphon valve {src(FLDEP, 'Florida DEP')}.</li>
    <li><strong>Top-mount valves go on the tank top,</strong> with the suction tube on the inlet and the line to the pump on the outlet {src(OPWASV, 'OPW')}.</li>
    <li><strong>Check orientation.</strong> Some are vertical-only {src(FFSASV, 'Franklin Fueling Systems')}; others work horizontal or vertical {src(MORASV, 'Morrison Bros.')}.</li>
    <li><strong>With a line leak detector,</strong> put the detector right downstream of the anti-siphon valve {src(NCDEQ, 'NC DEQ')}.</li>
  </ul>

  <h2>Troubleshooting</h2>
  <p><strong>The pump has to overcome the valve's spring every time it runs</strong> {src(OPWASV, 'OPW')}. On a suction pump, that's extra lift on top of everything else, so a valve set much higher than needed can cause trouble. For pump basics, see <a href="{PUMP_PATH}">how to choose a 12V fuel transfer pump</a>.</p>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Symptom</th><th scope="col">Things to check</th></tr></thead>
    <tbody>
      <tr><td>Pump won't prime or loses prime</td><td>Head setting too high for the pump; air leaks in suction fittings</td></tr>
      <tr><td>Low flow</td><td>Wrong valve setting or size; clogged strainer or filter</td></tr>
      <tr><td>Fuel still drains out with the pump off</td><td>Debris on the seat or a worn seal; replace or service the valve</td></tr>
      <tr><td>Line pressure building with the pump off</td><td>Thermal expansion relief not working</td></tr>
    </tbody>
  </table>
  </div>

  <section class="faq">
  <h2>FAQ</h2>
  {asv_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{PEIASV}" rel="noopener">PEI: Antisiphon valve (2014)</a></li>
    <li><a href="{FLDEP}" rel="noopener">Florida DEP: Block valves and anti-siphon valves (rev. July 2023)</a></li>
    <li><a href="{NCDEQ}" rel="noopener">NC DEQ: Anti-siphon valves at marinas (2022)</a></li>
    <li><a href="{NMAC}" rel="noopener">New Mexico Administrative Code 20.5.109.902</a></li>
    <li><a href="{CAZ}" rel="noopener">Central Arizona Fire and Medical Authority: Above-ground fuel tank checklist</a></li>
    <li><a href="{FREEPORT}" rel="noopener">Freeport, TX Fire Marshal: Aboveground storage tanks</a></li>
    <li><a href="{NESFM}" rel="noopener">Nebraska State Fire Marshal: Installation and use of farm tanks (2003)</a></li>
    <li><a href="{OPWASV}" rel="noopener">OPW: 199ASV anti-siphon valve</a></li>
    <li><a href="{MORASV}" rel="noopener">Morrison Bros.: Fig. 910 anti-siphon valve</a></li>
    <li><a href="{FFSASV}" rel="noopener">Franklin Fueling Systems: Anti-syphon valves</a></li>
    <li><a href="{ELAFLEX}" rel="noopener">Elaflex: Anti-siphon valve information</a></li>
  </ul>
  <p class="note">This guide is general information. Your fire marshal or tank regulator decides what's required at your site.</p>
</article>
"""

asv_schema = [
    {"@context": "https://schema.org", "@type": "Article", "headline": ASV_TITLE, "description": ASV_DESC,
     "datePublished": UPDATED, "dateModified": UPDATED,
     "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
     "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
     "mainEntityOfPage": DOMAIN + ASV_PATH},
    {"@context": "https://schema.org", "@type": "FAQPage",
     "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in asv_faq]},
]
page(ASV_PATH, ASV_TITLE, ASV_DESC, asv_body, schema=asv_schema, og_type="article")




# ---------------- Fuel nozzles ----------------
NOZ_PATH = "/fuel-nozzle/"
PEINOZ = "https://pei.org/?p=11360"
OPWNOZ = "https://opwglobal.com/products/us/retail-fueling-products/standard-dispensing-equipment/automatic-nozzles-gas-station/11a-and-11b-automatic-nozzles"
FRAUTO = "https://www.fillrite.com/1-cold-weather-automatic-diesel-spout-nozzle-blue"
FRMANN = "https://www.fillrite.com/1-aluminum-manual-nozzle"
DULTNOZ = "https://www.dultmeier.com/fuel-nozzle-automatic-34-diesel-green-cover-1516-spout-max-145-gpm"

NOZ_TITLE = "Fuel Nozzles: Automatic vs. Manual, Sizes, and Which Fits Your Pump"
NOZ_DESC = ("Automatic or manual, 3/4 or 1 inch, gas or diesel spout: how to pick a fuel nozzle that fits your pump and tank, "
            "how the automatic shutoff works, and what to do when it clicks off too early.")

noz_faq = [
    ("Can I use a gas nozzle for diesel?",
     f"It will work if it's rated for diesel, but use a diesel nozzle with the green cover and 15/16-inch spout. The different sizes and colors help prevent putting the wrong fuel in a vehicle {src(DULTNOZ, 'Dultmeier')}."),
    ("Why won't my automatic nozzle work on my gravity-fed farm tank?",
     f"Automatic nozzles need pumped flow to work the shutoff. Fill-Rite says its automatic nozzles aren't meant for gravity systems {src(FRAUTO, 'Fill-Rite')}. On a gravity tank, use a manual nozzle and stay with it."),
]
noz_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in noz_faq)

noz_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/aboveground-fuel-tanks/">Aboveground tanks</a></p>
  <h1>Fuel nozzles: automatic vs. manual, sizes, and which fits your pump</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>
  {AFF_NOTE}

  <div class="answer">
    <p><strong>Pick a nozzle by three things: automatic or manual, an inlet size that matches your hose (3/4 or 1 inch), and the right spout for your fuel.</strong> Automatic nozzles shut off when the tank is full; manual ones flow until you let go. Diesel nozzles usually have a 15/16-inch spout and a green cover, and unleaded gasoline nozzles a 13/16-inch spout, which helps keep the wrong fuel out of a vehicle {src(DULTNOZ, 'Dultmeier')}.</p>
  </div>
  <p>Match the nozzle to your pump's flow, too. A typical 3/4-inch automatic nozzle is rated to about 14.5 gallons per minute {src(DULTNOZ, 'Dultmeier')}; Fill-Rite's 1-inch nozzles are rated to 40 {src(FRMANN, 'Fill-Rite')}.</p>

  <h2>Automatic vs. manual</h2>
  <p><strong>An automatic nozzle shuts itself off when fuel covers a small hole near the tip of the spout. A manual nozzle has no shutoff: it flows as long as the handle is squeezed.</strong></p>
  <p><strong>How the automatic shutoff works.</strong> While fuel flows, air is drawn in through the hole at the spout tip. When the fuel level rises and covers that hole, the air stops, a vacuum builds inside the nozzle, and it pulls a diaphragm that trips the valve closed {src(PEINOZ, 'PEI')}. That's why a nozzle clicks off when the tank is full, and also why splash-back can trip it early.</p>
  {NOZZLE_SVG}
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col"></th><th scope="col">Automatic</th><th scope="col">Manual</th></tr></thead>
    <tbody>
      <tr><td>Shuts off when full</td><td>Yes</td><td>No; you have to watch it</td></tr>
      <tr><td>Best for</td><td>Farm and fleet tanks, pickups and equipment with a fill neck</td><td>Gravity-fed tanks, drums, and cans</td></tr>
      <tr><td>Watch out for</td><td>Needs pumped flow; Fill-Rite says its automatic nozzles aren't for gravity systems {src(FRAUTO, 'Fill-Rite')}</td><td>Easy to overfill if you walk away</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Field note:</strong> On farm and fleet tanks with a pump, I always install automatic nozzles.</p>
  <p><strong>Hold-open latches.</strong> Many automatic nozzles have a clip that holds the handle open at a set flow; Fill-Rite's have three latch positions {src(FRAUTO, 'Fill-Rite')}. Some sites can't use them: OPW says not to use its 11A with a hold-open device at pre-pay self-service sites {src(OPWNOZ, 'OPW')}. Never latch a manual nozzle open.</p>

  <h2>Sizes and spouts</h2>
  <p><strong>Match the inlet to your hose, the flow rating to your pump, and the spout to your fuel.</strong></p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Choice</th><th scope="col">Options</th><th scope="col">How to pick</th></tr></thead>
    <tbody>
      <tr><td>Inlet</td><td>3/4-inch or 1-inch NPT</td><td>Match your hose. A 3/4-inch automatic is typically rated to about 14.5 GPM {src(DULTNOZ, 'Dultmeier')}; 1-inch Fill-Rite nozzles go to 40 GPM {src(FRMANN, 'Fill-Rite')}</td></tr>
      <tr><td>Spout</td><td>13/16 inch (gasoline), 15/16 inch (diesel), larger high-flow spouts</td><td>Use the spout that matches the fuel {src(DULTNOZ, 'Dultmeier')}. Fill-Rite's 1-inch automatic diesel nozzle has a 1-3/16-inch spout {src(FRAUTO, 'Fill-Rite')}; whether that fits depends on the truck or tank, so check the fill neck first</td></tr>
      <tr><td>Fuel rating</td><td>Gasoline, diesel, ethanol and biodiesel blends</td><td>Check the listing. OPW's 11A and 11B are UL-listed for gasoline, diesel, and up to E85 {src(OPWNOZ, 'OPW')}</td></tr>
      <tr><td>Pressure</td><td>Check the max rating</td><td>OPW's 11A and 11B are rated to 50 psi {src(OPWNOZ, 'OPW')}</td></tr>
    </tbody>
  </table>
  </div>
  <p>For matching a nozzle to a 12V transfer pump, see <a href="{PUMP_PATH}">how to choose a 12V fuel transfer pump</a>.</p>

  <h2>Common nozzles</h2>
  <p><strong>Field note:</strong> OPW is the nozzle I install most.</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Nozzle</th><th scope="col">Type and size</th><th scope="col">Notes</th></tr></thead>
    <tbody>
      <tr><td>OPW 11B<br><span class="shop">{amz("OPW 11B automatic fuel nozzle", "Check price on Amazon")}</span></td><td>Automatic, 3/4 inch, gas or diesel versions</td><td>Won't open until the system is pressurized; rated to 50 psi {src(OPWNOZ, 'OPW')}</td></tr>
      <tr><td>OPW 11A<br><span class="shop">{amz("OPW 11A automatic fuel nozzle", "Check price on Amazon")}</span></td><td>Automatic, 3/4 inch, gas or diesel versions</td><td>No pressure-to-open feature; not for pre-pay self-serve with a hold-open {src(OPWNOZ, 'OPW')}</td></tr>
      <tr><td>Fill-Rite 1" automatic diesel<br><span class="shop">{amz("Fill-Rite 1 inch automatic diesel nozzle", "Check price on Amazon")}</span></td><td>Automatic, 1 inch, 1-3/16 inch spout, 40 GPM</td><td>Three latch positions; not for gravity flow {src(FRAUTO, 'Fill-Rite')}</td></tr>
      <tr><td>Fill-Rite 1" manual<br><span class="shop">{amz("Fill-Rite FRHMN100S manual nozzle", "Check price on Amazon")}</span></td><td>Manual, 1 inch, 15/16 inch spout, 40 GPM</td><td>For gravity tanks and drums {src(FRMANN, 'Fill-Rite')}</td></tr>
    </tbody>
  </table>
  </div>

  <h2>Troubleshooting</h2>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Problem</th><th scope="col">What to do</th></tr></thead>
    <tbody>
      <tr><td>Clicks off too early</td><td>Fuel is splashing up and covering the sensing hole at the spout tip {src(PEINOZ, 'PEI')}. Insert the spout further, lower the flow with the latch, or angle the nozzle</td></tr>
      <tr><td>Won't shut off</td><td>Stop using it and change the nozzle before it causes a spill</td></tr>
      <tr><td>OPW 11B won't open</td><td>The system isn't pressurized yet; the 11B is designed not to open until it is {src(OPWNOZ, 'OPW')}</td></tr>
      <tr><td>Automatic nozzle won't shut off on a gravity tank</td><td>Not enough flow; automatic nozzles aren't meant for gravity systems {src(FRAUTO, 'Fill-Rite')}</td></tr>
      <tr><td>Slow flow at a dispenser</td><td>Often the leak detector, not the nozzle. See <a href="/line-leak-detector/">line leak detectors</a></td></tr>
    </tbody>
  </table>
  </div>

  <section class="faq">
  <h2>FAQ</h2>
  {noz_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{PEINOZ}" rel="noopener">PEI: Automatic nozzle (2014)</a></li>
    <li><a href="{OPWNOZ}" rel="noopener">OPW: 11A and 11B automatic nozzles</a></li>
    <li><a href="{FRAUTO}" rel="noopener">Fill-Rite: 1" automatic diesel spout nozzle</a></li>
    <li><a href="{FRMANN}" rel="noopener">Fill-Rite: 1" aluminum manual nozzle</a></li>
    <li><a href="{DULTNOZ}" rel="noopener">Dultmeier: 3/4" automatic diesel nozzle</a></li>
  </ul>
</article>
"""

noz_schema = [
    {"@context": "https://schema.org", "@type": "Article", "headline": NOZ_TITLE, "description": NOZ_DESC,
     "datePublished": UPDATED, "dateModified": UPDATED,
     "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
     "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
     "mainEntityOfPage": DOMAIN + NOZ_PATH},
    {"@context": "https://schema.org", "@type": "FAQPage",
     "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in noz_faq]},
]
page(NOZ_PATH, NOZ_TITLE, NOZ_DESC, noz_body, schema=noz_schema, og_type="article")


# ---------------- Aboveground tanks hub ----------------
AST_PATH = "/aboveground-fuel-tanks/"
WGUL = "https://western-global.com/us/support/insights/knowing-the-approvals-ul142-vs-ul2085/"
NCUL = "https://www.ncosfm.gov/fire-prevention/220623-listing-and-labeling-above-ground-fuel-dispensing-tanks/open"
AST_TITLE = "Aboveground Fuel Tanks: Types, Rules, and Equipment"
AST_DESC = ("A guide to aboveground fuel tanks for farms, fleets, and small businesses: tank types, "
            "the rules that apply, the equipment on top, and links to every detailed guide.")
AST_GUIDES = [
    (SPCC_PATH, "Do I need an SPCC plan?", "The 1,320-gallon rule, the farm thresholds, which plan type you need, and a one-minute checker."),
    (SC_PATH, "Secondary containment", "How big a dike has to be, what the 110% rule really means, and when a double-wall tank counts."),
    (ASV_PATH, "Anti-siphon valves", "Why elevated tanks siphon, what the fire code requires, picking the head setting, and pump troubleshooting."),
    (TT_PATH, "Diesel transfer tanks", "Why 119 gallons matters, the rules for gasoline, payload math for your pickup, and setup."),
    (NOZ_PATH, "Fuel nozzles", "Automatic vs. manual, 3/4 or 1 inch, gas or diesel spouts, and troubleshooting."),
    (PUMP_PATH, "How to choose a 12V fuel transfer pump", "Flow rate, duty cycle, and wiring explained, and Fill-Rite and GPI models compared."),
]
ast_cards = "\n".join(
    f'    <li><a class="guide" href="{p}"><span class="card-title">{t}</span><p>{d}</p></a></li>' for p, t, d in AST_GUIDES)
ast_body = f"""
<div class="wrap">
  <h1>Aboveground fuel tanks</h1>
  <p class="lede">An aboveground storage tank (AST) is any fuel tank that sits on or above the ground instead of buried: a farm tank on a stand, a skid tank at a job site, a generator's base tank, or a fleet's fueling tank. Here's how they're built, the rules that apply, and the equipment that goes on them.</p>

  <h2>Types of aboveground tanks</h2>
  <p><strong>Most steel aboveground fuel tanks are built to UL 142. Protected tanks are built to UL 2085, which adds insulation between the walls for fire protection</strong> {src(WGUL, 'Western Global')}.</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Type</th><th scope="col">What it is</th><th scope="col">Typical use</th></tr></thead>
    <tbody>
      <tr><td>Single-wall (UL 142)</td><td>One steel wall</td><td>Needs a separate dike or containment area to meet spill rules {src(ECFR, '40 CFR 112.8(c)(2)')}; see <a href="{SC_PATH}">secondary containment</a></td></tr>
      <tr><td>Double-wall (UL 142)</td><td>A tank inside a tank; the outer wall catches a leak from the inner one</td><td>Can help meet the containment requirement, but still counts toward your SPCC capacity (see <a href="{SPCC_PATH}">the SPCC guide</a>)</td></tr>
      <tr><td>Protected (UL 2085)</td><td>Double-wall with insulation between the walls, built to limit heat to the inner tank during a 2-hour fire; can also be tested for ballistics and vehicle impact {src(WGUL, 'Western Global')}</td><td>Permanent installations with higher fire risk, such as gasoline dispensing; some states require it for aboveground gasoline dispensing tanks {src(NCUL, 'NC State Fire Marshal')}</td></tr>
      <tr><td>Transfer and auxiliary tanks</td><td>Small tanks in a pickup bed</td><td>See <a href="{TT_PATH}">diesel transfer tanks</a></td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Field note:</strong> On the farm and fleet sites I service, most tanks are UL 142, and double-wall tanks are more common than single-wall tanks in a dike. Protected tanks are heavier and harder to move than standard tanks {src(WGUL, 'Western Global')}.</p>

  <h2>The rules at a glance</h2>
  <p><strong>Three sets of rules can apply to an aboveground tank: the federal SPCC rule, your fire code, and your state's tank rules.</strong></p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Rule</th><th scope="col">Who it covers</th><th scope="col">Guide</th></tr></thead>
    <tbody>
      <tr><td>SPCC (40 CFR 112)</td><td>Sites with more than 1,320 gallons of aboveground oil storage that could spill to water; farms have higher thresholds</td><td><a href="{SPCC_PATH}">Do I need an SPCC plan?</a></td></tr>
      <tr><td>Fire code (IFC or NFPA 30/30A, as adopted locally)</td><td>Tank construction, spacing, and equipment such as anti-siphon valves</td><td><a href="{ASV_PATH}">Anti-siphon valves</a></td></tr>
      <tr><td>State tank rules</td><td>Varies by state; some register or inspect aboveground tanks</td><td>Check with your state fire marshal or environmental agency</td></tr>
    </tbody>
  </table>
  </div>

  <h2>Equipment on an aboveground tank</h2>
  <p><strong>The fittings on top of the tank keep it filled safely, vented, and from leaking out through the piping.</strong> Guides for the rest are in the works.</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Equipment</th><th scope="col">What it does</th><th scope="col">Guide</th></tr></thead>
    <tbody>
      <tr><td>Anti-siphon valve</td><td>Keeps fuel from draining out if a line breaks</td><td><a href="{ASV_PATH}">Anti-siphon valves</a></td></tr>
      <tr><td>Transfer pump</td><td>Moves fuel from the tank to equipment</td><td><a href="{PUMP_PATH}">12V transfer pumps</a></td></tr>
      <tr><td>Nozzle</td><td>Shuts off automatically when the tank you're filling is full</td><td><a href="{NOZ_PATH}">Fuel nozzles</a></td></tr>
      <tr><td>Vents (normal and emergency)</td><td>Let air in and out as fuel moves; relieve pressure in a fire</td><td>Coming soon</td></tr>
      <tr><td>Fill and spill containment</td><td>Catch drips at the fill when the delivery hose comes off</td><td>Coming soon</td></tr>
      <tr><td>Overfill prevention</td><td>Stops or warns before the tank is overfilled</td><td>Coming soon</td></tr>
      <tr><td>Gauges</td><td>Show how much fuel is in the tank</td><td>Coming soon</td></tr>
    </tbody>
  </table>
  </div>

  <h2>All aboveground tank guides</h2>
  <ul class="guide-list">
{ast_cards}
  </ul>
  <p>For the fuel inside the tank, see the <a href="{FQ_PATH}">fuel quality guides</a>.</p>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{WGUL}" rel="noopener">Western Global: UL 142 vs. UL 2085</a></li>
    <li><a href="{NCUL}" rel="noopener">NC Office of State Fire Marshal: Listing and labeling of aboveground fuel dispensing tanks (2011)</a></li>
    <li><a href="{ECFR}" rel="noopener">eCFR: 40 CFR Part 112</a></li>
  </ul>
</div>
"""
ast_schema = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": AST_TITLE, "description": AST_DESC,
               "url": DOMAIN + AST_PATH,
               "hasPart": [{"@type": "Article", "name": t, "url": DOMAIN + p} for p, t, _ in AST_GUIDES]}]
page(AST_PATH, AST_TITLE, AST_DESC, ast_body, schema=ast_schema)



# ---------------- Spill buckets ----------------
SB_PATH = "/spill-bucket-testing/"
C28035 = "https://www.law.cornell.edu/cfr/text/40/280.35"
EPASO = "https://www.epa.gov/system/files/documents/2024-08/spill-overfill-2024-07-11.pdf"
EPASB = "https://www.epa.gov/sites/default/files/2017-06/documents/spill-bucket-2017_0.pdf"
EPAOM = "https://www.epa.gov/ust/operating-and-maintaining-ust-systems-2015-requirements"
KUBIN = "https://neiwpcc.org/wp-content/uploads/2022/09/Kubinsky_UST-Testing_9-13-22.pdf"
GAEPD = "https://epd.georgia.gov/sites/epd.georgia.gov/files/GA_EPD_UST_3_Yr_Spill_Bucket_Test.pdf"
MI2120 = "https://www.law.cornell.edu/regulations/michigan/Mich-Admin-Code-R-29-2120"

SB_TITLE = "Spill Bucket Testing: What the UST Rule Requires and How the Test Works"
SB_DESC = ("Spill buckets on underground tanks must be checked every 30 days and tested every 3 years, unless they're "
           "double-walled and monitored. What the federal rule requires, how the test works, and what fails.")

sb_faq = [
    ("Can I just drain the fuel in my spill bucket back into the tank?",
     f"Many buckets have a drain valve for that, but water and debris go in with it. EPA's advice is to empty the bucket right away and dispose of the contents properly {src(EPASB, 'EPA')}."),
    ("Does a double-walled spill bucket ever need testing?",
     f"Not while you check between the walls at least as often as your walkthroughs. If you stop monitoring, you have 30 days to test it {src(C28035, '40 CFR 280.35')}."),
    ("Who can test a spill bucket?",
     "The federal rule sets the method, not who does it. Some states require a certified tester and others don't, so check with your state UST program."),
    ("Do aboveground tanks need spill buckets?",
     f"The federal UST rule covers underground tanks. For aboveground tanks, see the <a href=\"{AST_PATH}\">aboveground fuel tanks guide</a> and your fire code."),
]
sb_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in sb_faq)

sb_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/underground-storage-tanks/">Underground tanks</a></p>
  <h1>Spill bucket testing: what the UST rule requires and how the test works</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>

  <div class="answer">
    <p><strong>A spill bucket is the container around an underground tank's fill pipe that catches fuel that drips when the delivery hose comes off. Under the federal UST rule, you check it every 30 days and test it for tightness at least every 3 years, unless it's double-walled and you check between the walls instead</strong> (<a href="{EPASO}" rel="noopener">EPA</a>; <a href="{C28035}" rel="noopener">40 CFR 280.35</a>).</p>
  </div>
  <p>Spill buckets are meant to hold small spills for a short time, not to store fuel. EPA says to empty them right away and dispose of what's inside properly {src(EPASB, 'EPA')}.</p>
  {SPILL_SVG}

  <h2>What the federal rule requires</h2>
  <p><strong>Any UST filled with more than 25 gallons at a time needs spill and overfill prevention</strong> {src(EPASO, 'EPA')}. For spill buckets, that means three ongoing jobs:</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Requirement</th><th scope="col">How often</th><th scope="col">Details</th></tr></thead>
    <tbody>
      <tr><td>Walkthrough inspection</td><td>Every 30 days, or before each delivery if deliveries are less frequent</td><td>Check for damage, remove liquid or debris, clear any obstruction in the fill pipe, make sure the fill cap is secure, and on double-walled buckets check between the walls for a leak {src(EPAOM, 'EPA')}. See the <a href="/ust-walkthrough-inspection/">walkthrough checklist</a></td></tr>
      <tr><td>Tightness test (single-wall)</td><td>At least every 3 years</td><td>Vacuum, pressure, or liquid test to show it's liquid tight {src(C28035, '40 CFR 280.35')}</td></tr>
      <tr><td>Interstitial monitoring (double-wall)</td><td>At least as often as walkthroughs</td><td>Replaces the 3-year test. Stop monitoring and you have to test within 30 days {src(C28035, '40 CFR 280.35')}</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Keep the records.</strong> Test records are kept for 3 years. If you skip testing because the bucket is double-walled, keep proof that it's double-walled for as long as you monitor it {src(C28035, '40 CFR 280.35')}. Keep the most recent year of walkthrough records {src(EPAOM, 'EPA')}.</p>
  <p><strong>Deadlines.</strong> Tanks in use on or before October 13, 2015 needed their first test by October 13, 2018. Newer tanks have to comply from installation {src(C28035, '40 CFR 280.35')}.</p>
  <p>EPA also recommends checking the bucket before and right after each delivery, and after rain or snowmelt {src(EPASO, 'EPA')}.</p>

  <h2>How a spill bucket test works</h2>
  <p><strong>The test has to follow the manufacturer's procedure, a recognized code of practice such as PEI RP1200, or your state's method</strong> (<a href="{C28035}" rel="noopener">40 CFR 280.35</a>; <a href="{GAEPD}" rel="noopener">Georgia EPD</a>). Either way, a bucket with a visible crack or hole fails without testing {src(GAEPD, 'Georgia EPD form')}.</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Method</th><th scope="col">How it's done</th><th scope="col">Passes if</th></tr></thead>
    <tbody>
      <tr><td>Hydrostatic (water)</td><td>Fill the bucket with water to within 1.5 inches of the top and hold it at least an hour</td><td>The level drops less than 1/8 inch (<a href="{KUBIN}" rel="noopener">Kubinsky, National Tanks Conference 2022</a>; <a href="{GAEPD}" rel="noopener">Georgia EPD</a>)</td></tr>
      <tr><td>Vacuum</td><td>Seal a test lid on top and pull 30 inches of water column vacuum</td><td>Vacuum holds at 26 inches or more {src(KUBIN, 'Kubinsky')}</td></tr>
      <tr><td>Vacuum on the interstitial space (double-wall)</td><td>Pull 15 inches of water column between the walls</td><td>Holds at 12 inches or more {src(KUBIN, 'Kubinsky')}</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Field note:</strong> I test with water. While the bucket is open, I always check the drop tube gasket and the fill gasket, and replace them if they're bad or stretched.</p>
  <p>The water from a hydrostatic test has been in contact with fuel residue, so handle and dispose of it properly.</p>

  <h2>What fails, and what to do about it</h2>
  <p><strong>Cracks, bad seals, leaking drain valves, and broken lids are the usual problems. EPA says to repair or replace any of them right away</strong> {src(EPASB, 'EPA')}.</p>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Problem</th><th scope="col">Why it matters</th></tr></thead>
    <tbody>
      <tr><td>Cracked, damaged, or corroded bucket</td><td>Not liquid tight; it won't hold a spill {src(EPASB, 'EPA')}</td></tr>
      <tr><td>Worn seals or gaskets, including around the fill riser</td><td>The bucket leaks even if the body is fine {src(EPASB, 'EPA')}</td></tr>
      <tr><td>Damaged drain valve</td><td>Lets fuel or water into the tank, or out of the bucket {src(EPASB, 'EPA')}</td></tr>
      <tr><td>Damaged, missing, or loose lid</td><td>Lets water and debris collect in the bucket and get into the tank {src(EPASB, 'EPA')}</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Keep it clean and dry.</strong> Water left sitting in the bucket can get dumped into the tank through the drain valve. That's one of the ways water gets into stored fuel (see <a href="{WATER_PATH}">water in your diesel tank</a>).</p>

  <h2>State rules</h2>
  <p><strong>States run most UST programs, so your state's rules are the ones you're inspected on.</strong> Michigan, for example, adopted the same 3-year test for spill prevention equipment, with the same double-walled option {src(MI2120, 'Mich. Admin. Code R 29.2120')}. Some states publish their own test forms {src(GAEPD, 'Georgia EPD')}.</p>

  <section class="faq">
  <h2>FAQ</h2>
  {sb_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{C28035}" rel="noopener">Cornell LII: 40 CFR 280.35</a></li>
    <li><a href="{EPASO}" rel="noopener">EPA: UST Spill and Overfill Prevention (EPA 510-F-24-006, July 2024)</a></li>
    <li><a href="{EPASB}" rel="noopener">EPA: Spill Buckets (EPA 510-F-17-004, May 2017)</a></li>
    <li><a href="{EPAOM}" rel="noopener">EPA: Operating and maintaining UST systems, 2015 requirements</a></li>
    <li><a href="{KUBIN}" rel="noopener">Edward Kubinsky, CROMPCO: UST testing, National Tanks Conference (2022)</a></li>
    <li><a href="{GAEPD}" rel="noopener">Georgia EPD: 3-year spill bucket test form</a></li>
    <li><a href="{MI2120}" rel="noopener">Michigan Admin. Code R 29.2120</a></li>
  </ul>
  <p class="note">This guide is general information. Your state UST program decides what's required at your site.</p>
</article>
"""

sb_schema = [
    {"@context": "https://schema.org", "@type": "Article", "headline": SB_TITLE, "description": SB_DESC,
     "datePublished": UPDATED, "dateModified": UPDATED,
     "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
     "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
     "mainEntityOfPage": DOMAIN + SB_PATH},
    {"@context": "https://schema.org", "@type": "FAQPage",
     "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in sb_faq]},
]
page(SB_PATH, SB_TITLE, SB_DESC, sb_body, schema=sb_schema, og_type="article")



# ---------------- Line leak detectors ----------------
LLD_PATH = "/line-leak-detector/"
STOT = "https://www.epa.gov/sites/default/files/2016-05/documents/stot_5-2-16_final_508.pdf"
MSLLD = "https://deq.ms.gov/wp-content/uploads/2012/02/LineLeakDetectorTest-1.pdf"
SCELLD = "https://des.sc.gov/sites/des/files/Documents/BLWM/UST/Electronic_Line_Leak_Detection.pdf"
VRFXV = "https://www.veeder.com/us/fuel-leak-detection/mechanical-line-leak-detection"
EPAIM = "https://www.epa.gov/ust/release-detection-underground-storage-tanks-usts-interstitial-method"

LLD_TITLE = "Line Leak Detectors: How They Work, the Annual Test, and Slow Flow"
LLD_DESC = ("Every pressurized UST line needs an automatic line leak detector that catches a 3 gallon-per-hour leak, "
            "tested every year. How mechanical and electronic detectors work, how the test is done, and why your dispenser runs slow.")

lld_faq = [
    ("Does a line leak detector replace the annual line tightness test?",
     f"No. The detector covers big leaks. You still need a second method for small ones, such as an annual 0.1 gph tightness test or monthly monitoring {src(STOT, 'EPA')}."),
    ("Does an electronic detector's self-test count as the annual test?",
     f"Only if it runs a simulated leak. A self-diagnostic alone doesn't meet the requirement {src(STOT, 'EPA')}."),
    ("Is a diesel leak detector different from a gasoline one?",
     f"Yes. Veeder-Root sells separate mechanical models for gasoline (FX1V) and diesel (FX1DV), plus versions for higher ethanol and biodiesel blends {src(VRFXV, 'Veeder-Root')}."),
]
lld_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in lld_faq)

lld_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/underground-storage-tanks/">Underground tanks</a></p>
  <h1>Line leak detectors: how they work, the annual test, and slow flow</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>

  <div class="answer">
    <p><strong>A line leak detector watches the pressure in the pipe between an underground tank's submersible pump and the dispenser. If the line can't hold pressure, it slows the flow, shuts off the pump, or sounds an alarm. Federal rules require one on all pressurized UST piping, able to catch a 3 gallon-per-hour leak at 10 psi within an hour, and it has to be tested every year</strong> {src(STOT, 'EPA, Straight Talk on Tanks')}.</p>
  </div>
  <p>Suction systems, where the dispenser pulls fuel up from the tank, don't use one. This guide is about pressurized systems, the setup at most gas stations and many fleet sites.</p>

  <h2>What the federal rule requires</h2>
  <p><strong>Pressurized piping needs two kinds of leak detection: an automatic line leak detector for big leaks, plus a second method for small ones</strong> {src(STOT, 'EPA')}.</p>
  <div class="table-wrap">
  <table class="even">
    <thead><tr><th scope="col">Requirement</th><th scope="col">Standard</th></tr></thead>
    <tbody>
      <tr><td>Automatic line leak detector</td><td>Detects 3 gallons per hour at 10 psi within 1 hour, and shuts off flow, restricts flow, or triggers an alarm</td></tr>
      <tr><td>Annual test of the detector</td><td>Simulate a leak at or below 3 gph; follow the manufacturer, a code of practice, or your state's method. A self-diagnostic alone doesn't count unless it runs a simulated leak</td></tr>
      <tr><td>Second method (pick one)</td><td>Annual line tightness test (0.1 gph at 1.5 times operating pressure), or monthly interstitial, vapor, groundwater, or statistical inventory monitoring, or continuous in-tank detection that covers the lines</td></tr>
      <tr><td>Records</td><td>Keep test records for 3 years</td></tr>
    </tbody>
  </table>
  </div>
  <p class="source-line">Source: <a href="{STOT}" rel="noopener">EPA, Straight Talk on Tanks (2016)</a>.</p>
  <p>UST systems installed or replaced after April 11, 2016 must be secondarily contained and use interstitial monitoring {src(EPAIM, 'EPA')}. In practice that means double-wall piping, and monitoring between the walls becomes the second method on newer sites.</p>

  <h2>Mechanical vs. electronic leak detectors</h2>
  <p><strong>Both watch line pressure. A mechanical detector screws into the pump head and slows the flow if it senses a leak; an electronic one uses a pressure sensor tied to a tank monitor or controller that can shut the pump off and log results</strong> (<a href="{STOT}" rel="noopener">EPA</a>; <a href="{SCELLD}" rel="noopener">SC DES</a>).</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col"></th><th scope="col">Mechanical</th><th scope="col">Electronic</th></tr></thead>
    <tbody>
      <tr><td>How it checks</td><td>Each time the pump turns on, it holds the line at a low "metering" pressure for a few seconds. If the line holds, it opens to full flow {src(MSLLD, 'Mississippi DEQ')}</td><td>Pressurizes the line with the pump and times how fast the pressure decays {src(SCELLD, 'SC DES')}</td></tr>
      <tr><td>What happens with a leak</td><td>Stays in the leak position and restricts flow to the dispenser {src(VRFXV, 'Veeder-Root')}</td><td>Shuts off or restricts flow, or alarms {src(SCELLD, 'SC DES')}</td></tr>
      <tr><td>Small-leak testing</td><td>No</td><td>Many can also run 0.2 gph monthly or 0.1 gph annual tests, which can count as the second method {src(SCELLD, 'SC DES')}</td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Field note:</strong> The mechanical detectors I see most are FE Petro and Red Jacket. Red Jacket makes separate gasoline (FX1V) and diesel (FX1DV) models {src(VRFXV, 'Veeder-Root')}.</p>

  <h2>How the annual test works</h2>
  <p><strong>The tester connects a test rig at the dispenser end of the line, opens a calibrated leak of 3 gph at 10 psi, and turns on the pump to see whether the detector catches it</strong> {src(MSLLD, 'Mississippi DEQ')}.</p>
  <p>For a mechanical detector, Mississippi's procedure works like this:</p>
  <ol>
    <li>Set the test orifice to 189 mL per minute, which equals 3 gph.</li>
    <li>Turn on the pump with no leak open. Pressure should rise, pause for about 2 to 5 seconds at the metering pressure, then build to full pump pressure. Record the metering pressure and the opening time.</li>
    <li>Bleed the line to zero so the detector resets, open the simulated leak, and turn the pump on again for at least 60 seconds.</li>
    <li><strong>Pass:</strong> the line pressure never climbs above the metering pressure while the leak is open. <strong>Fail:</strong> it reaches full pump pressure, or the detector doesn't reset when the line is bled to zero.</li>
  </ol>
  {LLD_SVG}
  <p>An electronic detector passes if it alarms or shuts the pump down during the simulated leak. Mississippi says to repeat the test before calling a first failure final {src(MSLLD, 'Mississippi DEQ')}.</p>

  <h2>"My dispenser is slow"</h2>
  <p><strong>A dispenser that pumps at a trickle usually means a mechanical leak detector is sitting in its restricted-flow position.</strong> It couldn't confirm the line was tight when the pump came on (<a href="{STOT}" rel="noopener">EPA</a>; <a href="{VRFXV}" rel="noopener">Veeder-Root</a>).</p>
  <p><strong>Field note:</strong> The most common cause I see isn't a leak. It's someone squeezing the nozzle before the dispenser is ready. Fuel flows out while the detector is still checking the line, so it reads that as a leak and stays tripped. Hang up the nozzle, wait for the dispenser to reset, and let it come up to pressure before you start pumping.</p>
  <p>If it's still slow after a clean restart, treat it as a possible leak and have the line and detector checked. Some states have reporting deadlines for a suspected release; South Carolina, for example, asks for a call within 24 hours when an electronic detector reports anything other than a pass {src(SCELLD, 'SC DES')}.</p>

  <section class="faq">
  <h2>FAQ</h2>
  {lld_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{STOT}" rel="noopener">EPA: Release Detection for USTs and Piping, Straight Talk on Tanks (EPA 510-K-16-003, May 2016)</a></li>
    <li><a href="{EPAIM}" rel="noopener">EPA: Release detection, interstitial method</a></li>
    <li><a href="{MSLLD}" rel="noopener">Mississippi DEQ: Line leak detector test procedure</a></li>
    <li><a href="{SCELLD}" rel="noopener">South Carolina DES: Electronic line leak detection</a></li>
    <li><a href="{VRFXV}" rel="noopener">Veeder-Root: Red Jacket FXV mechanical line leak detectors</a></li>
  </ul>
  <p class="note">This guide is general information. Your state UST program decides what's required at your site.</p>
</article>
"""

lld_schema = [
    {"@context": "https://schema.org", "@type": "Article", "headline": LLD_TITLE, "description": LLD_DESC,
     "datePublished": UPDATED, "dateModified": UPDATED,
     "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
     "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
     "mainEntityOfPage": DOMAIN + LLD_PATH},
    {"@context": "https://schema.org", "@type": "FAQPage",
     "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in lld_faq]},
]
page(LLD_PATH, LLD_TITLE, LLD_DESC, lld_body, schema=lld_schema, og_type="article")



# ---------------- Overfill prevention ----------------
OFP_PATH = "/ust-overfill-prevention/"
MUSTS = "https://www.epa.gov/sites/default/files/2015-12/documents/musts_for_usts.pdf"
NEIOFP = "https://neiwpcc.org/wp-content/uploads/2021/12/FINAL_UST-Overfill-Prevention_12.15.21.pdf"

OFP_TITLE = "UST Overfill Prevention: Shutoff Valves, Alarms, and Ball Floats"
OFP_DESC = ("Underground tanks need overfill prevention: a drop-tube shutoff valve, an alarm, or (on older tanks) a ball float. "
            "The activation levels, the 3-year inspection, and how to order fuel so it never gets close.")

ofp_faq = [
    ("Can I still use my ball float?",
     f"Under the federal rule, an existing ball float installed on or before October 13, 2015 can stay if it works properly. Once you replace your overfill prevention, the replacement can't be a ball float {src(EPASO, 'EPA')}. Check your state's rule too."),
    ("Where does the overfill alarm have to be?",
     f"Where the delivery driver can easily see or hear it {src(EPASO, 'EPA')}."),
    ("Does a spill bucket count as overfill prevention?",
     f"No. A spill bucket catches drips at the fill when the hose comes off; overfill prevention stops the tank itself from overfilling. You need both. See <a href=\"{SB_PATH}\">spill bucket testing</a>."),
]
ofp_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in ofp_faq)

ofp_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/underground-storage-tanks/">Underground tanks</a></p>
  <h1>UST overfill prevention: shutoff valves, alarms, and ball floats</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>

  <div class="answer">
    <p><strong>Overfill prevention stops or warns before a delivery overfills an underground tank. The federal rule allows three devices: an automatic shutoff valve in the drop tube, an overfill alarm, or a ball float valve, and each has to be inspected at least every 3 years</strong> {src(MUSTS, 'EPA, Musts for USTs')}.</p>
  </div>
  <p>A tank that never receives more than 25 gallons at a time doesn't need it {src(MUSTS, 'EPA')}.</p>

  <h2>The three types</h2>
  <p><strong>Each device has a level it has to act by.</strong></p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Device</th><th scope="col">What it does</th><th scope="col">Must act by</th></tr></thead>
    <tbody>
      <tr><td>Automatic shutoff valve (flapper in the drop tube)</td><td>Closes and stops the delivery</td><td>95% full, and before the fittings on top of the tank are covered</td></tr>
      <tr><td>Overfill alarm</td><td>Warns the driver with a horn or light they can see or hear at the fill</td><td>90% full, or 1 minute before overfilling</td></tr>
      <tr><td>Ball float valve (vent line)</td><td>Blocks vapor from leaving, which slows the delivery</td><td>90% full, or 30 minutes before overfilling</td></tr>
    </tbody>
  </table>
  </div>
  <p class="source-line">Sources: <a href="{MUSTS}" rel="noopener">EPA, Musts for USTs</a>; <a href="{EPASO}" rel="noopener">EPA, Spill and Overfill Prevention (2024)</a>.</p>
  {OVERFILL_SVG}
  <p><strong>Ball floats are on their way out.</strong> They can't be used when overfill prevention is installed or replaced after October 13, 2015 {src(MUSTS, 'EPA')}. They also only work with tight-fill gravity deliveries, not pressurized (pumped) deliveries or tanks with suction pumps or coaxial drop tubes {src(NEIOFP, 'NEIWPCC inspector training, 2021')}.</p>
  <p><strong>Field note:</strong> On the sites I work on, overfill prevention is alarms and drop-tube shutoff valves. Ball floats aren't an option for new or replacement equipment.</p>

  <h2>The 3-year inspection</h2>
  <p><strong>The inspection has to confirm the device is set to act at the right level and will actually act when fuel gets there</strong> {src(MI2120, 'Mich. Admin. Code R 29.2120, adopting 40 CFR 280.35')}. It follows the manufacturer's instructions or a code of practice {src(MUSTS, 'EPA')}.</p>
  <p>For a drop-tube valve, that usually means pulling the drop tube. Testing in place misses many problems {src(NEIOFP, 'NEIWPCC')}. The inspector measures the tube and the tank's manway height to confirm where the valve will shut off, and accounts for tank tilt.</p>
  <p><strong>What fails.</strong> At one first round of inspections, half the devices were installed wrong or didn't work. Failures included corroded parts, missing gaskets, loose adapters, valves set at the wrong height (one at 97% instead of 93% because the tank was tilted), and tampering {src(NEIOFP, 'NEIWPCC')}. EPA also says to check that a shutoff hasn't been tampered with, disabled, or removed {src(EPASO, 'EPA')}.</p>

  <h2>How to order fuel so it never gets close</h2>
  <p><strong>The device is a backup. The real overfill prevention is ordering the right amount.</strong> The rule says to make sure the delivery will fit in the empty space in the tank and to watch the delivery the whole time {src(MUSTS, 'EPA')}.</p>
  <p>EPA's formula: order no more than (tank capacity × 0.90) − fuel already in the tank {src(MUSTS, 'EPA')}.</p>
  <p><strong>Example:</strong> A 10,000-gallon tank holding 3,500 gallons can take 10,000 × 0.90 − 3,500 = <strong>5,500 gallons</strong>.</p>

  <section class="faq">
  <h2>FAQ</h2>
  {ofp_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{MUSTS}" rel="noopener">EPA: Musts for USTs (EPA 510-K-15-001, Nov. 2015)</a></li>
    <li><a href="{EPASO}" rel="noopener">EPA: UST Spill and Overfill Prevention (EPA 510-F-24-006, July 2024)</a></li>
    <li><a href="{NEIOFP}" rel="noopener">NEIWPCC: UST inspector training, overfill prevention (Dec. 2021)</a></li>
    <li><a href="{MI2120}" rel="noopener">Michigan Admin. Code R 29.2120</a></li>
  </ul>
  <p class="note">This guide is general information. Your state UST program decides what's required at your site.</p>
</article>
"""

ofp_schema = [
    {"@context": "https://schema.org", "@type": "Article", "headline": OFP_TITLE, "description": OFP_DESC,
     "datePublished": UPDATED, "dateModified": UPDATED,
     "author": {"@type": "Person", "name": "FuelStorageGuide", "jobTitle": "Fuel-system technician"},
     "publisher": {"@type": "Organization", "name": "FuelStorageGuide", "url": DOMAIN},
     "mainEntityOfPage": DOMAIN + OFP_PATH},
    {"@context": "https://schema.org", "@type": "FAQPage",
     "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in ofp_faq]},
]
page(OFP_PATH, OFP_TITLE, OFP_DESC, ofp_body, schema=ofp_schema, og_type="article")


# ---------------- UST walkthrough inspections ----------------
WT_PATH = "/ust-walkthrough-inspection/"
C28036 = "https://www.law.cornell.edu/cfr/text/40/280.36"
C28031 = "https://www.law.cornell.edu/cfr/text/40/280.31"
C28034 = "https://www.law.cornell.edu/cfr/text/40/280.34"
C28012 = "https://www.law.cornell.edu/cfr/text/40/280.12"
EPAOMPDF = "https://www.epa.gov/sites/default/files/2016-02/documents/om_final_2-17-16_508_0.pdf"

WT_TITLE = "UST Walkthrough Inspection: 30-Day and Annual Checklist"
WT_DESC = ("What the federal UST rule says to check every 30 days and every year, a printable walkthrough "
           "checklist, and the records you have to keep.")

wt_faq = [
    ("Who is allowed to do the walkthrough?",
     "The federal rule doesn't say who has to do it, only what gets checked and what gets written down. Your state may set its own requirements, so check with your state UST program."),
    ("Does my farm tank need walkthroughs?",
     f"Not if it's 1,100 gallons or less and holds motor fuel for noncommercial use. Those tanks aren't USTs under the federal rule, and neither are heating oil tanks used on the premises {src(C28012, '40 CFR 280.12')}. Your state may still regulate them."),
    ("Do I send walkthrough records to the state?",
     f"No. Keep them at the site where an inspector can see them right away, or at another location and hand them over when asked {src(C28034, '40 CFR 280.34(c)')}."),
    ("My tank only gets fuel every couple of months. Do I still check spill buckets every 30 days?",
     f"No. If deliveries come less often than every 30 days, you can check spill prevention equipment before each delivery instead. Keep the delivery records to show why {src(C28036, '40 CFR 280.36')}."),
]
wt_faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in wt_faq)

wt_rows = [
    ("Every 30 days", "Spill buckets", "No cracks, holes, or other damage"),
    ("Every 30 days", "Spill buckets", "Liquid and debris removed"),
    ("Every 30 days", "Fill pipe", "Nothing blocking the fill pipe"),
    ("Every 30 days", "Fill cap", "Cap secure on the fill pipe"),
    ("Every 30 days", "Double-wall spill buckets", "No leak in the space between the walls"),
    ("Every 30 days", "Release detection", "Equipment running, no alarms or unusual conditions"),
    ("Every 30 days", "Release detection records", "Test records reviewed and up to date"),
    ("Every year", "Containment sumps", "No damage, no leaks into the sump, no releases to the environment"),
    ("Every year", "Containment sumps", "Liquid and debris removed"),
    ("Every year", "Double-wall sumps", "No leak in the space between the walls"),
    ("Every year", "Hand-held equipment", "Gauge sticks and groundwater bailers usable and in good shape"),
]
wt_checklist = "\n".join(
    f"      <tr><td>{f}</td><td>{a}</td><td>{c}</td><td></td><td></td></tr>" for f, a, c in wt_rows)

wt_body = f"""
<article class="wrap">
  <p class="crumbs"><a href="/underground-storage-tanks/">Underground tanks</a></p>
  <h1>UST walkthrough inspection: the 30-day and annual checklist</h1>
  <p class="meta">Written by a fuel-system technician. Updated {UPDATED_HUMAN}.</p>

  <div class="answer">
    <p><strong>Under the federal UST rule, you walk your system every 30 days to check spill buckets and release detection, and once a year to check containment sumps and hand-held release detection equipment. Keep a record of each walkthrough for one year.</strong> The requirement has applied since October 13, 2018 {src(C28036, '40 CFR 280.36')}.</p>
  </div>

  <p>The walkthrough is the routine check that catches problems between the formal tests: a cracked spill bucket, a loose fill cap, an alarm nobody noticed. It doesn't replace the 3-year tests or the yearly line leak detector test; it runs alongside them.</p>

  <h2>Who has to do walkthroughs</h2>
  <p><strong>Owners and operators of regulated underground storage tanks.</strong> Some tanks aren't USTs under the federal rule, including farm or residential tanks of 1,100 gallons or less holding motor fuel for noncommercial use, and tanks holding heating oil used on the premises {src(C28012, '40 CFR 280.12')}.</p>
  <p><strong>States run most UST programs</strong>, so your state's version of the rule is the one you're inspected on. You can meet the walkthrough requirement any of three ways {src(C28036, '40 CFR 280.36(a)')}:</p>
  <ul>
    <li>Check the equipment the federal rule lists (the checklist below)</li>
    <li>Follow a recognized code of practice; the rule names PEI RP 900, the Petroleum Equipment Institute's recommended practice for UST inspection and maintenance</li>
    <li>Use a walkthrough developed by your state program</li>
  </ul>

  <h2>Every 30 days</h2>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Equipment</th><th scope="col">What to check</th></tr></thead>
    <tbody>
      <tr><td>Spill prevention equipment (spill buckets)</td><td>Visually check for damage; remove liquid or debris; check for and remove obstructions in the fill pipe; make sure the fill cap is securely on the fill pipe; on double-walled equipment with interstitial monitoring, check for a leak between the walls</td></tr>
      <tr><td>Release detection equipment</td><td>Make sure it's operating with no alarms or other unusual operating conditions; make sure release detection test records are reviewed and current</td></tr>
    </tbody>
  </table>
  </div>
  <p class="source-line">Source: <a href="{C28036}" rel="noopener">40 CFR 280.36(a)(1)(i)</a>.</p>
  <p><strong>Field note:</strong> On walkthroughs I find all of it: water or fuel sitting in spill buckets and sumps, fill caps that aren't tight, and alarms nobody acted on. Another gap I see a lot is owners not printing the sensor status reports from the tank monitor, so there's no record of what the sensors showed.</p>
  <p><strong>Infrequent deliveries.</strong> If your tank gets fuel less often than every 30 days, you can check the spill prevention equipment before each delivery instead. You then keep the delivery records with your walkthrough records {src(C28036, '40 CFR 280.36')}. Release detection still gets checked every 30 days.</p>
  <p>For what a spill bucket should look like and why water in it matters, see <a href="{SB_PATH}">spill bucket testing</a>. For release detection on pressurized piping, see <a href="{LLD_PATH}">line leak detectors</a>.</p>

  <h2>Once a year</h2>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Equipment</th><th scope="col">What to check</th></tr></thead>
    <tbody>
      <tr><td>Containment sumps (under dispensers and at the tank top)</td><td>Visually check for damage, leaks into the sump, or releases to the environment; remove liquid (in contained sumps) or debris; on double-walled sumps with interstitial monitoring, check for a leak between the walls</td></tr>
      <tr><td>Hand-held release detection equipment</td><td>Check devices such as tank gauge sticks or groundwater bailers for operability and serviceability</td></tr>
    </tbody>
  </table>
  </div>
  <p class="source-line">Source: <a href="{C28036}" rel="noopener">40 CFR 280.36(a)(1)(ii)</a>.</p>

  <h2>Printable walkthrough checklist</h2>
  <p><strong>Print this page and fill in a row for each item, each walkthrough.</strong> It covers the federal minimum; add anything your state requires. EPA also publishes a longer manual with checklists and record forms {src(EPAOMPDF, 'EPA 510-K-16-001')}.</p>
  <div class="table-wrap">
  <table class="checklist">
    <thead><tr><th scope="col">How often</th><th scope="col">Equipment</th><th scope="col">Check</th><th scope="col">OK?</th><th scope="col">Action taken</th></tr></thead>
    <tbody>
{wt_checklist}
    </tbody>
  </table>
  </div>
  <p>Date: ____________ &nbsp; Checked by: ______________________ &nbsp; Last delivery (if checking before deliveries): ____________</p>

  <h2>Records you have to keep</h2>
  <p><strong>Keep walkthrough records for one year.</strong> Each record has to include {src(C28036, '40 CFR 280.36(b)')}:</p>
  <ul>
    <li>A list of each area checked</li>
    <li>Whether each area was acceptable or needed action</li>
    <li>A description of what was done to fix any problem</li>
    <li>Delivery records, if you check spill equipment before deliveries instead of every 30 days</li>
  </ul>
  <p><strong>Field note:</strong> The slip-up I see most is owners who do the walkthrough but never write it down. Without the record, there's nothing to show an inspector.</p>
  <p>Keep them at the site, immediately available to an inspector, or at another location and provide them when asked {src(C28034, '40 CFR 280.34(c)')}. Records of the 3-year spill bucket, sump, and overfill tests are kept longer: three years {src(C28035, '40 CFR 280.35(c)')}.</p>

  <h2>How the walkthrough fits the other UST deadlines</h2>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">How often</th><th scope="col">What</th><th scope="col">Rule</th></tr></thead>
    <tbody>
      <tr><td>Every 30 days</td><td>Walkthrough: spill buckets and release detection</td><td><a href="{C28036}" rel="noopener">280.36</a></td></tr>
      <tr><td>Every 60 days</td><td>Check impressed current cathodic protection is running</td><td><a href="{C28031}" rel="noopener">280.31(c)</a></td></tr>
      <tr><td>Every year</td><td>Walkthrough: containment sumps and hand-held equipment</td><td><a href="{C28036}" rel="noopener">280.36</a></td></tr>
      <tr><td>Every year</td><td>Line leak detector test on pressurized piping (see <a href="{LLD_PATH}">line leak detectors</a>)</td><td><a href="{STOT}" rel="noopener">EPA</a></td></tr>
      <tr><td>Every 3 years</td><td>Tightness test of single-wall spill buckets and of sumps used for piping interstitial monitoring (see <a href="{SB_PATH}">spill bucket testing</a>)</td><td><a href="{C28035}" rel="noopener">280.35</a></td></tr>
      <tr><td>Every 3 years</td><td>Overfill prevention inspection (see <a href="{OFP_PATH}">overfill prevention</a>)</td><td><a href="{C28035}" rel="noopener">280.35</a></td></tr>
      <tr><td>Every 3 years</td><td>Cathodic protection test by a qualified tester</td><td><a href="{C28031}" rel="noopener">280.31(b)</a></td></tr>
    </tbody>
  </table>
  </div>
  <p><strong>Double-walled spill buckets and sumps</strong> can skip the 3-year tightness test if you check between the walls at least as often as your walkthroughs. Stop checking, and you have 30 days to test {src(C28035, '40 CFR 280.35(a)(1)')}.</p>

  <section class="faq">
  <h2>FAQ</h2>
  {wt_faq_html}
  </section>

  <h2>Sources</h2>
  <ul class="sources">
    <li><a href="{C28036}" rel="noopener">40 CFR 280.36, periodic operation and maintenance walkthrough inspections (Cornell LII)</a></li>
    <li><a href="{C28035}" rel="noopener">40 CFR 280.35, periodic testing of spill and overfill prevention equipment and containment sumps (Cornell LII)</a></li>
    <li><a href="{C28034}" rel="noopener">40 CFR 280.34, reporting and recordkeeping (Cornell LII)</a></li>
    <li><a href="{C28031}" rel="noopener">40 CFR 280.31, operation and maintenance of corrosion protection (Cornell LII)</a></li>
    <li><a href="{C28012}" rel="noopener">40 CFR 280.12, definitions (Cornell LII)</a></li>
    <li><a href="{EPAOMPDF}" rel="noopener">EPA: Operating and Maintaining UST Systems, Practical Help and Checklists (EPA 510-K-16-001, 2016)</a></li>
    <li><a href="{STOT}" rel="noopener">EPA: UST system operation and testing requirements</a></li>
  </ul>
  <p class="note">This guide is general information. Your state UST program decides what's required at your site.</p>
</article>
"""

wt_schema = [{"@context": "https://schema.org", "@type": "Article", "headline": WT_TITLE, "description": WT_DESC,
              "datePublished": UPDATED, "dateModified": UPDATED, "mainEntityOfPage": DOMAIN + WT_PATH}]
page(WT_PATH, WT_TITLE, WT_DESC, wt_body, schema=wt_schema, og_type="article")

# ---------------- Underground tanks hub ----------------
UST_PATH = "/underground-storage-tanks/"
UST_TITLE = "Underground Storage Tanks: Inspections, Testing, and Equipment"
UST_DESC = ("A guide to underground fuel tank (UST) compliance for gas stations, fleets, airports, and small businesses: "
            "what gets checked monthly, yearly, and every 3 years, and a detailed guide for each piece of equipment.")
UST_GUIDES = [
    (WT_PATH, "Walkthrough inspections", "What to check every 30 days and every year, a printable checklist, and the records to keep."),
    (SB_PATH, "Spill bucket testing", "The 30-day walkthrough, the 3-year test, how the water and vacuum tests work, and what fails."),
    (LLD_PATH, "Line leak detectors", "How mechanical and electronic detectors work, what the yearly test checks, and why a dispenser drops to a trickle."),
    (OFP_PATH, "Overfill prevention", "Shutoff valves, alarms, and ball floats, the 3-year inspection, and how to order fuel so it never gets close."),
]
ust_cards = "\n".join(
    f'    <li><a class="guide" href="{p}"><span class="card-title">{t}</span><p>{d}</p></a></li>' for p, t, d in UST_GUIDES)
ust_body = f"""
<div class="wrap">
  <h1>Underground storage tanks</h1>
  <p class="lede">Underground storage tanks (USTs) sit at gas stations, fleet yards, airports, and plenty of small businesses. The federal UST rule (40 CFR Part 280) sets what has to be checked and how often, and your state program enforces it. These guides cover each piece of equipment.</p>

  <h2>What gets checked, and how often</h2>
  <p><strong>Most UST compliance runs on three clocks: every 30 days, every year, and every 3 years.</strong></p>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">How often</th><th scope="col">What</th><th scope="col">Guide</th></tr></thead>
    <tbody>
      <tr><td>Every 30 days</td><td>Walkthrough inspection, including spill buckets {src(EPAOM, 'EPA')}</td><td><a href="{WT_PATH}">Walkthrough checklist</a></td></tr>
      <tr><td>Every year</td><td>Walkthrough of containment sumps and hand-held release detection equipment {src(C28036, '40 CFR 280.36')}</td><td><a href="{WT_PATH}">Walkthrough checklist</a></td></tr>
      <tr><td>Every year</td><td>Line leak detector test on pressurized piping, plus a line tightness test unless you monitor monthly {src(STOT, 'EPA')}</td><td><a href="{LLD_PATH}">Line leak detectors</a></td></tr>
      <tr><td>Every 3 years</td><td>Spill bucket tightness test (single-wall) {src(C28035, '40 CFR 280.35')}</td><td><a href="{SB_PATH}">Spill buckets</a></td></tr>
      <tr><td>Every 3 years</td><td>Overfill prevention inspection {src(MUSTS, 'EPA')}</td><td><a href="{OFP_PATH}">Overfill prevention</a></td></tr>
    </tbody>
  </table>
  </div>
  <p>The federal rule also covers release detection for the tanks themselves, containment sumps, corrosion protection, and operator training. Guides on those are coming.</p>
  <p><strong>Your state runs the program.</strong> Most states adopted the federal rule and inspect against it, sometimes with their own forms and extra requirements. Michigan, for example, adopted the federal testing schedule {src(MI2120, 'Mich. Admin. Code R 29.2120')}. Check with your state UST program.</p>

  <h2>All underground tank guides</h2>
  <ul class="guide-list">
{ust_cards}
  </ul>
  <p>Have aboveground tanks too? See the <a href="{AST_PATH}">aboveground fuel tanks guide</a>. For the fuel inside, see the <a href="{FQ_PATH}">fuel quality guides</a>.</p>
</div>
"""
ust_schema = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": UST_TITLE, "description": UST_DESC,
               "url": DOMAIN + UST_PATH,
               "hasPart": [{"@type": "Article", "name": t, "url": DOMAIN + p} for p, t, _ in UST_GUIDES]}]
page(UST_PATH, UST_TITLE, UST_DESC, ust_body, schema=ust_schema)


# ---------------- Home ----------------
def hotspot(href, x, y, lx, ly, text, anchor="start"):
    """A labeled callout on the hero tank that links to a guide."""
    w = len(text) * 7.4 + 18
    rx = lx if anchor == "start" else lx - w
    return (f'<a href="{href}" class="hotspot"><line x1="{x}" y1="{y}" x2="{lx}" y2="{ly}"/>'
            f'<circle cx="{x}" cy="{y}" r="5"/>'
            f'<rect x="{rx}" y="{ly - 13}" width="{w}" height="26" rx="13"/>'
            f'<text x="{rx + w / 2}" y="{ly + 4.5}" text-anchor="middle">{text}</text></a>')

HERO_TANK_SVG = f"""<svg class="hero-tank" viewBox="0 0 560 380" role="img" aria-labelledby="tank-title">
  <title id="tank-title">Cutaway of an aboveground diesel tank. Each label links to a guide.</title>
  <defs>
    <clipPath id="tank-clip"><rect x="60" y="120" width="380" height="150" rx="75"/></clipPath>
    <pattern id="bugs" width="14" height="8" patternUnits="userSpaceOnUse"><circle cx="3" cy="4" r="1.6" fill="#9fd3a9"/><circle cx="10" cy="2.5" r="1.1" fill="#9fd3a9"/></pattern>
  </defs>
  <!-- saddles -->
  <path d="M120 262 L104 318 H186 L170 262Z M330 262 L314 318 H396 L380 262Z" fill="#33454e"/>
  <rect x="40" y="318" width="420" height="6" rx="3" fill="#33454e"/>
  <!-- tank contents -->
  <g clip-path="url(#tank-clip)">
    <rect x="60" y="120" width="380" height="150" fill="#22323a"/>
    <rect x="60" y="160" width="380" height="110" fill="#c79f2a" opacity=".9"/>
    <rect x="60" y="160" width="380" height="3" fill="#f0c02b"/>
    <rect x="60" y="246" width="380" height="24" fill="#3b7ea1"/>
    <rect x="60" y="240" width="380" height="8" fill="url(#bugs)"/>
    <path d="M60 150 Q 110 140 160 150 T 260 150 T 360 150 T 440 150" stroke="#5f737c" stroke-width="1.5" fill="none" stroke-dasharray="3 5"/>
  </g>
  <rect x="60" y="120" width="380" height="150" rx="75" fill="none" stroke="#d9e2df" stroke-width="3"/>
  <!-- vent -->
  <path d="M120 120 V78" stroke="#d9e2df" stroke-width="6"/>
  <path d="M104 80 Q120 60 136 80Z" fill="#d9e2df"/>
  <!-- fill -->
  <rect x="200" y="104" width="26" height="16" fill="#d9e2df"/><rect x="196" y="98" width="34" height="8" rx="2" fill="#f0c02b"/>
  <!-- pump, valve, hose, nozzle -->
  <rect x="320" y="84" width="44" height="36" rx="4" fill="#1d6a48" stroke="#d9e2df" stroke-width="2"/>
  <path d="M364 102 H404 V112" stroke="#d9e2df" stroke-width="5" fill="none"/>
  <rect x="396" y="112" width="16" height="16" rx="2" fill="#f0c02b"/>
  <path d="M404 128 C 404 230, 480 210, 486 286" stroke="#0e171c" stroke-width="7" fill="none"/>
  <path d="M404 128 C 404 230, 480 210, 486 286" stroke="#4d5f67" stroke-width="4" fill="none"/>
  <path d="M478 282 h18 l4 26 h-8 l-3 14 h-6z" fill="#d9e2df"/>
  <g class="hotspots">
    {hotspot(STORE_PATH, 250, 200, 18, 210, "Old fuel")}
    {hotspot(WATER_PATH, 150, 258, 18, 352, "Water on the bottom")}
    {hotspot(BIO_PATH, 300, 243, 250, 352, "Diesel bugs")}
    {hotspot(GEL_PATH, 180, 175, 18, 168, "Gelling")}
    {hotspot(PUMP_PATH, 342, 90, 300, 32, "12V pump")}
    {hotspot(ASV_PATH, 412, 120, 548, 72, "Anti-siphon valve", "end")}
    {hotspot(NOZ_PATH, 492, 300, 548, 352, "Nozzle", "end")}
    {hotspot(WATER_PATH, 120, 70, 18, 32, "Vent")}
  </g>
</svg>"""

def topic_card(num, path, name, blurb, guides, icon):
    items = "".join(f'<li><a href="{p}">{t}</a></li>' for p, t, _ in guides)
    return f"""
    <section class="topic" aria-labelledby="topic-{num}">
      <span class="rivet tl"></span><span class="rivet tr"></span><span class="rivet bl"></span><span class="rivet br"></span>
      <div class="topic-head">
        <span class="topic-icon" aria-hidden="true">{icon}</span>
        <div><p class="label">{num:02d} / {len(guides)} guides</p><h3 id="topic-{num}"><a href="{path}">{name}</a></h3></div>
      </div>
      <p class="topic-blurb">{blurb}</p>
      <ol class="topic-list">{items}</ol>
      <a class="topic-cta" href="{path}">Start here: {name.lower()}</a>
    </section>"""

ICON_DROP = '<svg viewBox="0 0 32 32"><path d="M16 3 C 16 3, 6 15, 6 21 a10 10 0 0 0 20 0 C 26 15, 16 3, 16 3Z" fill="#f0c02b"/><path d="M8 22 h16" stroke="#15212a" stroke-width="2"/></svg>'
ICON_AST = '<svg viewBox="0 0 32 32"><rect x="3" y="9" width="26" height="14" rx="7" fill="#f0c02b"/><path d="M9 23 l-2 6 M23 23 l2 6 M10 9 V5" stroke="#f0c02b" stroke-width="2.5"/></svg>'
ICON_UST = '<svg viewBox="0 0 32 32"><path d="M2 12 H30" stroke="#f0c02b" stroke-width="2.5" stroke-dasharray="3 2"/><rect x="5" y="16" width="22" height="12" rx="6" fill="#f0c02b"/><path d="M12 16 V4 M20 16 V8" stroke="#f0c02b" stroke-width="2.5"/></svg>'

QUICK = [
    (SPCC_PATH, "Do I need an SPCC plan?"),
    (STORE_PATH, "How long does diesel last?"),
    (GEL_PATH, "At what temperature does diesel gel?"),
    (WATER_PATH, "How do I get water out of my tank?"),
    (TT_PATH, "Is a 119-gallon transfer tank legal?"),
    (LLD_PATH, "Why is my dispenser so slow?"),
]
HERO_CHIPS = [(WATER_PATH, "Water on the bottom"), (BIO_PATH, "Diesel bugs"), (GEL_PATH, "Gelling"), (STORE_PATH, "Old fuel"),
              (PUMP_PATH, "12V pump"), (ASV_PATH, "Anti-siphon valve"), (NOZ_PATH, "Nozzle")]
hero_chips = "".join(f'<li><a href="{p}">{t}</a></li>' for p, t in HERO_CHIPS)
quick_links = "".join(f'<li><a href="{p}">{q}</a></li>' for p, q in QUICK)

home_body = f"""
<section class="hero">
  <div class="hero-inner">
    <div class="hero-text">
      <p class="label label-light">Fuel storage guides from the field</p>
      <h1>Straight answers about the fuel in your tank</h1>
      <p class="lede">Practical guides for farms, contractors, fleets, and anyone who owns a fuel tank: keeping fuel clean and flowing, choosing equipment, and understanding the rules for aboveground and underground tanks.</p>
      <div class="hero-actions">
        <a class="btn btn-yellow" href="#topics">Find your guide</a>
        <a class="btn btn-ghost" href="{SPCC_PATH}#checker-title">Check if you need an SPCC plan</a>
      </div>
    </div>
    <figure class="hero-figure">
      {HERO_TANK_SVG}
      <figcaption>Tap a part of the tank to jump to its guide.</figcaption>
      <ul class="hero-chips">{hero_chips}</ul>
    </figure>
  </div>
</section>

<section class="proof" aria-label="Why trust these guides">
  <ul class="proof-inner">
    <li><span class="proof-num">8 yrs</span><span>servicing tanks, pumps, dispensers, and leak detectors</span></li>
    <li><span class="proof-num">Sourced</span><span>every number links to the regulation, study, or manufacturer it came from</span></li>
    <li><span class="proof-num">Independent</span><span>no fuel supplier, additive maker, or equipment brand owns this site</span></li>
  </ul>
</section>

<div class="wide home-body">
  <div class="section-head" id="topics">
    <p class="label">Pick a topic</p>
    <h2>What kind of tank problem do you have?</h2>
  </div>
  <div class="topics">
    {topic_card(1, FQ_PATH, "Fuel quality", "Water, microbes, gelling, and old fuel. Start with what you're seeing in the tank.", FQ_GUIDES, ICON_DROP)}
    {topic_card(2, AST_PATH, "Aboveground tanks", "Farm and fleet tanks: the spill rules, transfer tanks, and the equipment on top.", AST_GUIDES, ICON_AST)}
    {topic_card(3, UST_PATH, "Underground tanks", "What gets tested every 30 days, every year, and every 3 years, piece by piece.", UST_GUIDES, ICON_UST)}
  </div>

  <div class="quick">
    <div class="section-head">
      <p class="label">Common questions</p>
      <h2>Quick answers people come here for</h2>
    </div>
    <ul class="quick-list">{quick_links}</ul>
  </div>

  {AUTHOR_BOX}
</div>
"""
page("/", "FuelStorageGuide: Practical Guides for Farm and Fleet Fuel Tanks",
     "Practical, sourced guides for farms, contractors, and fleets that store their own fuel, written by a working fuel-system technician.",
     home_body, current="/",
     schema=[{"@context": "https://schema.org", "@graph": [
         {"@type": "WebSite", "@id": DOMAIN + "/#website", "name": "FuelStorageGuide", "url": DOMAIN + "/",
          "publisher": {"@id": ORG_ID}},
         ORG,
         {"@type": "WebPage", "@id": DOMAIN + "/", "url": DOMAIN + "/",
          "name": "FuelStorageGuide: Practical Guides for Farm and Fleet Fuel Tanks",
          "isPartOf": {"@id": DOMAIN + "/#website"}, "about": {"@id": ORG_ID}}]}])

# ---------------- About ----------------
about_body = """
<div class="wrap">
  <h1>About FuelStorageGuide</h1>
  <p class="lede">FuelStorageGuide is written by Austin, a working fuel-system technician with eight years in the trade.</p>
  <p>The day job is inspecting and servicing fuel systems: underground and aboveground tanks, dispensers, piping, valves, and leak detection equipment, plus annual inspections and filter changes on aviation fuel systems.</p>
  <p>Most of what goes wrong with stored fuel is preventable, but the good information is scattered across fuel supplier marketing, government PDFs, and forum threads that contradict each other. This site puts it in one place, in plain language, for the people who actually own the tanks.</p>
  <h2>How guides are written</h2>
  <ul>
    <li><strong>Sourced.</strong> Every specific number or rule links to the source it came from: industry research, regulators, or the manufacturer. Sources are listed at the bottom of each guide.</li>
    <li><strong>Checked against field experience.</strong> Guides are reviewed by someone who services this equipment, and they say so when field practice differs from the textbook.</li>
    <li><strong>Independent.</strong> FuelStorageGuide isn't owned by a fuel supplier, additive maker, or equipment brand. Some pages may include affiliate links; see the <a href="/affiliate-disclosure/">affiliate disclosure</a>.</li>
    <li><strong>Updated.</strong> Each guide shows the date it was last updated.</li>
  </ul>
  <p>Spot something wrong or out of date? <a href="/contact/">Send a correction</a>.</p>
</div>
"""
page("/about/", "About FuelStorageGuide",
     "FuelStorageGuide is written by a working fuel-system technician. How guides are researched, sourced, and kept up to date.",
     about_body, current="/about/",
     schema=[{"@context": "https://schema.org", "@type": "AboutPage", "@id": DOMAIN + "/about/",
              "url": DOMAIN + "/about/", "name": "About FuelStorageGuide",
              "mainEntity": AUTHOR if AUTHOR_NAME else {"@id": ORG_ID},
              "isPartOf": {"@id": DOMAIN + "/#website"}}])

# ---------------- Contact ----------------
contact_body = """
<div class="wrap">
  <h1>Contact</h1>
  <p class="lede">Questions, corrections, and topic suggestions are welcome.</p>
  <p>Email <a href="mailto:contact@fuelstorageguide.com">contact@fuelstorageguide.com</a>.</p>
  <p>Corrections are especially appreciated. If a guide is wrong or out of date, include the page and what you've seen in the field, and it will be checked and updated.</p>
  <p class="note">FuelStorageGuide can't inspect or troubleshoot specific equipment over email. For a problem with your own tank or pump, contact a licensed local fuel-system contractor.</p>
</div>
"""
page("/contact/", "Contact FuelStorageGuide",
     "Send questions, corrections, or topic suggestions to FuelStorageGuide.",
     contact_body, current="/contact/")

# ---------------- Privacy ----------------
privacy_body = f"""
<div class="wrap">
  <h1>Privacy policy</h1>
  <p class="meta">Last updated {UPDATED_HUMAN}</p>
  <p>FuelStorageGuide is a reading site. There are no accounts, logins, or comments. The SPCC checker runs entirely in your browser, and nothing you enter in it is sent anywhere.</p>
  <h2>What is collected</h2>
  <ul>
    <li><strong>Visit statistics.</strong> The site uses Cloudflare Web Analytics to count page views and see which guides are useful. It doesn't use cookies or track you across other sites.</li>
    <li><strong>Server logs.</strong> The site is hosted on Cloudflare, which processes standard request information such as IP addresses to deliver pages and protect against attacks. See <a href="https://www.cloudflare.com/privacypolicy/" rel="noopener">Cloudflare's privacy policy</a>.</li>
    <li><strong>Email.</strong> If you email us, your message and address are used only to reply.</li>
  </ul>
  <h2>Fonts</h2>
  <p>Fonts are served from this site. No third-party font service sees your visit.</p>
  <h2>Affiliate links</h2>
  <p>Some pages link to products through affiliate programs, including Amazon Associates. If you click one, the retailer may set its own cookies to credit the referral. Their privacy policies apply on their sites. See the <a href="/affiliate-disclosure/">affiliate disclosure</a>.</p>
  <h2>Changes and questions</h2>
  <p>If this policy changes, the date above will change. Questions: <a href="mailto:contact@fuelstorageguide.com">contact@fuelstorageguide.com</a>.</p>
</div>
"""
page("/privacy/", "Privacy Policy | FuelStorageGuide",
     "What FuelStorageGuide collects (very little) and how it's used.",
     privacy_body)

# ---------------- Affiliate disclosure ----------------
aff_body = f"""
<div class="wrap">
  <h1>Affiliate disclosure</h1>
  <p class="meta">Last updated {UPDATED_HUMAN}</p>
  <p>Some links on FuelStorageGuide are affiliate links. If you buy something through one, the site may earn a commission at no extra cost to you.</p>
  <p><strong>As an Amazon Associate, FuelStorageGuide earns from qualifying purchases.</strong></p>
  <p>Affiliate relationships don't decide what gets recommended. Products are mentioned because they fit the job, and guides say when a cheaper or simpler option works just as well. No company pays to be included or reviewed.</p>
  <p>Product links go to Amazon search results rather than a single listing, so you can compare sellers and kits. Pages with affiliate links say so near the top. Questions: <a href="mailto:contact@fuelstorageguide.com">contact@fuelstorageguide.com</a>.</p>
</div>
"""
page("/affiliate-disclosure/", "Affiliate Disclosure | FuelStorageGuide",
     "How FuelStorageGuide handles affiliate links and product recommendations.",
     aff_body)

# ---------------- 404 ----------------
nf_body = """
<div class="wrap">
  <h1>That page isn't here</h1>
  <p class="lede">The link may be old or mistyped.</p>
  <p><a href="/">Go to all guides</a></p>
</div>
"""
page("/404.html", "Page not found | FuelStorageGuide", "Page not found.", nf_body)

for _args in PAGES:
    render(*_args)

# ---------------- sitemap, robots, favicon ----------------
# Legal and contact pages stay crawlable through the footer but are left out of the sitemap
urls = ["/", NOZ_PATH, UST_PATH, WT_PATH, OFP_PATH, AST_PATH, SB_PATH, LLD_PATH, FQ_PATH, STORE_PATH, TEST_PATH, CLEAN_PATH, STAB_PATH, ASV_PATH, SPCC_PATH, SC_PATH, ADD_PATH, WATER_PATH, BIO_PATH, TT_PATH, PUMP_PATH, GEL_PATH, "/about/"]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls:
    sitemap += f"  <url><loc>{DOMAIN}{u}</loc><lastmod>{DATES.get(u, (UPDATED,))[0]}</lastmod></url>\n"
sitemap += "</urlset>\n"
(SITE / "sitemap.xml").write_text(sitemap)
(SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")

# ---------------- Cloudflare headers and redirects ----------------
(SITE / "_headers").write_text("""/*
  Strict-Transport-Security: max-age=31536000
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Content-Security-Policy: frame-ancestors 'none'; base-uri 'self'; form-action 'self'

/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/styles.css
  Cache-Control: public, max-age=31536000, immutable

/og/*
  Cache-Control: public, max-age=86400

/logo.png
  Cache-Control: public, max-age=86400
""")
# Permanent redirects for slashless URLs (the host's default is a temporary 307)
(SITE / "_redirects").write_text("".join(
    f"{p.rstrip('/')} {p} 301\n" for p, *_ in PAGES if p.endswith("/") and p != "/"))
(SITE / "favicon.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<rect width="32" height="32" rx="4" fill="#1c272c"/>'
    '<rect x="4" y="9" width="24" height="14" rx="7" fill="#1d6a48"/>'
    '<rect x="4" y="19" width="24" height="4" fill="#f0c02b"/>'
    '</svg>'
)
print("built", sorted(str(p.relative_to(SITE)) for p in SITE.rglob("*") if p.is_file()))
