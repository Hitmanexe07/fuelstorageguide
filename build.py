"""Builds the FuelStorageGuide.com static site into ./site"""
import json
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent / "tools"))
from diagrams import WATER_TANK_SVG, TRANSFER_RULE_SVG
from pathlib import Path

SITE = Path(__file__).parent / "site"
DOMAIN = "https://fuelstorageguide.com"
UPDATED = "2026-10-28"
UPDATED_HUMAN = "October 28, 2026"

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


NAV = [("/", "Guides"), ("/about/", "About"), ("/contact/", "Contact")]


def page(path, title, description, body, current=None, schema=None, og_type="website"):
    canonical = DOMAIN + path
    slug = path.strip("/").replace(".html", "") or "home"
    og_file = SITE / "og" / f"{slug}.png"
    og_image = f"{DOMAIN}/og/{slug}.png" if og_file.exists() else f"{DOMAIN}/og/home.png"
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
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="FuelStorageGuide">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og_image}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
{schema_tag}
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="site-header">
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
    <span>FuelStorageGuide. Practical guidance on stored fuel, written by a working fuel-system technician. As an Amazon Associate, we earn from qualifying purchases.</span>
    <nav aria-label="Footer">
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
  <p><strong>These numbers could change.</strong> The farm thresholds come from the 2014 law, not the regulation text. EPA's 2015 study recommended dropping the 6,000-gallon tier and using 2,500 gallons for farms {src(STUDY, 'EPA farm study')}, but we found no final rule making that change. Going the other way, the House passed the PERMIT Act (H.R. 3898) in December 2025, which would raise the farm thresholds, including 20,000 to 42,000 gallons and 2,500 to 3,000 (<a href="{HRPT}" rel="noopener">House Report 119-180</a>; <a href="{BDLAW}" rel="noopener">Beveridge &amp; Diamond</a>). As of our last check, it hadn't passed the Senate {src(LEGIS, 'Legislate')}. This guide will be updated if either changes.</p>

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
      <tr><td>Secondary containment</td><td>A dike, berm, double-wall tank, or similar that holds the entire contents of the largest container, plus room for rain</td><td><a href="{ECFR}" rel="noopener">112.8(c)(2)</a></td></tr>
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
    <li><strong>Test for microbes if you see slime or sludge.</strong> If the water tests positive, the usual sequence is: remove the water, add a biocide, let it work, remove the water bottom again, and retest over the following weeks {src(GILBERT, 'Gilbert')}. Biocides are EPA-registered pesticides, so follow the label exactly {src(PSAIL, 'Practical Sailor')}.</li>
    <li><strong>Expect filters to plug for a while after a biocide treatment.</strong> Dead microbes come loose from the tank walls and get caught in filters (<a href="{PSAIL}" rel="noopener">Practical Sailor</a>; <a href="{CRC672}" rel="noopener">CRC Report 672</a>). Keep spares on hand.</li>
    <li><strong>Change the dispenser filter</strong> when you're done, and look at the old one for rust or slime.</li>
  </ol>
  <p><strong>Call for a tank cleaning when</strong> there's heavy sludge, the water keeps coming back, or filters keep plugging after treatment. A badly infected tank usually needs the bottom material removed mechanically, not just treated {src(PSAIL, 'Practical Sailor')}. Your fuel supplier can often pump the tank out {src(CENEXW, 'Cenex')}.</p>
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

# ---------------- Home ----------------
home_body = f"""
<div class="wide">
  <section class="intro">
    <h1>Straight answers about the fuel in your tank</h1>
    <p class="lede">Practical guides for farms, contractors, and fleets that store their own diesel and gasoline: keeping fuel clean and flowing, choosing equipment, and understanding the rules for aboveground tanks.</p>
    <p>Every guide is written by a fuel-system technician who inspects and services tanks, pumps, and dispensers for a living, and every fact links to its source.</p>
  </section>

  <h2>Guides</h2>
  <ul class="guide-list">
    <li><a class="guide" href="{SPCC_PATH}"><span class="card-title">Do I need an SPCC plan?</span><p>The 1,320-gallon rule, the farm thresholds, which plan type you need, and a one-minute checker for your site.</p></a></li>
    <li><a class="guide" href="{WATER_PATH}"><span class="card-title">Water in your diesel tank</span><p>How water gets in, how to check for it with paste or a clear jar, how to get it out, and how to keep it out.</p></a></li>
    <li><a class="guide" href="{ADD_PATH}"><span class="card-title">Winter diesel additives: what anti-gel does and when to add it</span><p>How anti-gel works, how to treat a bulk tank before the cold, label treat rates, and when blending or heat makes more sense.</p></a></li>
    <li><a class="guide" href="{TT_PATH}"><span class="card-title">Diesel transfer tanks: sizing, legal limits, and setup</span><p>Why 119 gallons matters, the rules for gasoline, payload math for your pickup, and how to set one up.</p></a></li>
    <li><a class="guide" href="{PUMP_PATH}"><span class="card-title">How to choose a 12V fuel transfer pump</span><p>Flow rate, duty cycle, and wiring explained, Fill-Rite and GPI models compared, and which size fits your tank.</p></a></li>
    <li><a class="guide" href="{GEL_PATH}"><span class="card-title">Diesel gelling: when it happens and how to prevent it</span><p>Cloud point, CFPP, and pour point explained, why bulk tanks gel first, and a winter checklist for tank owners.</p></a></li>
  </ul>
</div>
"""
page("/", "FuelStorageGuide: Practical Guides for Farm and Fleet Fuel Tanks",
     "Practical, sourced guides for farms, contractors, and fleets that store their own fuel, written by a working fuel-system technician.",
     home_body, current="/",
     schema=[{"@context": "https://schema.org", "@type": "WebSite", "name": "FuelStorageGuide", "url": DOMAIN}])

# ---------------- About ----------------
about_body = """
<div class="wrap">
  <h1>About FuelStorageGuide</h1>
  <p class="lede">FuelStorageGuide is written by a working fuel-system technician with eight years in the trade.</p>
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
     about_body, current="/about/")

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
  <p>FuelStorageGuide is a reading site. There are no accounts, logins, comments, or forms.</p>
  <h2>What is collected</h2>
  <ul>
    <li><strong>Visit statistics.</strong> The site uses Cloudflare Web Analytics to count page views and see which guides are useful. It doesn't use cookies or track you across other sites.</li>
    <li><strong>Server logs.</strong> The site is hosted on Cloudflare, which processes standard request information such as IP addresses to deliver pages and protect against attacks. See <a href="https://www.cloudflare.com/privacypolicy/" rel="noopener">Cloudflare's privacy policy</a>.</li>
    <li><strong>Email.</strong> If you email us, your message and address are used only to reply.</li>
  </ul>
  <h2>Fonts</h2>
  <p>Pages load fonts from Google Fonts, which receives your IP address when the fonts are downloaded. See <a href="https://policies.google.com/privacy" rel="noopener">Google's privacy policy</a>.</p>
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

# ---------------- sitemap, robots, favicon ----------------
urls = ["/", SPCC_PATH, ADD_PATH, WATER_PATH, TT_PATH, PUMP_PATH, GEL_PATH,"/about/", "/contact/", "/privacy/", "/affiliate-disclosure/"]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls:
    sitemap += f"  <url><loc>{DOMAIN}{u}</loc><lastmod>{UPDATED}</lastmod></url>\n"
sitemap += "</urlset>\n"
(SITE / "sitemap.xml").write_text(sitemap)
(SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
(SITE / "favicon.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<rect width="32" height="32" rx="4" fill="#1c272c"/>'
    '<rect x="4" y="9" width="24" height="14" rx="7" fill="#1d6a48"/>'
    '<rect x="4" y="19" width="24" height="4" fill="#f0c02b"/>'
    '</svg>'
)
print("built", sorted(str(p.relative_to(SITE)) for p in SITE.rglob("*") if p.is_file()))
