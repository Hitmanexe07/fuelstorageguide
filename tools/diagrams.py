"""Inline SVG diagrams used in guides. Imported by build.py."""

WATER_TANK_SVG = """<figure class="diagram">
<svg viewBox="0 0 680 380" role="img" aria-labelledby="wt-title wt-desc" xmlns="http://www.w3.org/2000/svg" font-family="Barlow Condensed, Arial Narrow, Arial, sans-serif">
  <title id="wt-title">Where water collects in a diesel storage tank</title>
  <desc id="wt-desc">Side view of an aboveground tank. Humid air enters the vent and condenses on the walls. Rain gets in at loose caps. Water sinks below the fuel and collects at the low end, where microbes grow at the fuel-water line. The pump pickup sits at least 3 inches off the bottom, and a drain at the low end removes water.</desc>
  <defs>
    <marker id="wt-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#56666d"/></marker>
    <clipPath id="wt-clip"><rect x="80" y="110" width="440" height="190" rx="70"/></clipPath>
  </defs>
  <!-- fuel and water inside the tank -->
  <g clip-path="url(#wt-clip)">
    <rect x="80" y="110" width="440" height="190" fill="#f4f6f5"/>
    <rect x="80" y="165" width="440" height="140" fill="#e9d9a8"/>
    <polygon points="80,268 520,288 520,305 80,305" fill="#7fb0d6"/>
    <path d="M80 268 L520 288" stroke="#1d6a48" stroke-width="3" stroke-dasharray="6 5"/>
    <line x1="80" y1="165" x2="520" y2="165" stroke="#c8b67a" stroke-width="2"/>
  </g>
  <rect x="80" y="110" width="440" height="190" rx="70" fill="none" stroke="#1c272c" stroke-width="3"/>
  <!-- condensation drops -->
  <g fill="#7fb0d6"><circle cx="150" cy="130" r="4"/><circle cx="175" cy="142" r="3"/><circle cx="450" cy="128" r="4"/><circle cx="470" cy="145" r="3"/></g>
  <!-- vent -->
  <rect x="190" y="70" width="16" height="42" fill="#1c272c"/><rect x="180" y="62" width="36" height="12" rx="3" fill="#1c272c"/>
  <!-- fill cap -->
  <rect x="380" y="92" width="34" height="20" rx="3" fill="#1c272c"/>
  <!-- pump and pickup tube -->
  <rect x="290" y="74" width="44" height="38" rx="4" fill="#1d6a48"/>
  <rect x="307" y="112" width="10" height="160" fill="#1c272c"/>
  <!-- drain at low (right) end -->
  <rect x="434" y="300" width="12" height="22" fill="#1c272c"/><rect x="426" y="320" width="28" height="10" rx="2" fill="#1c272c"/>
  <!-- labels -->
  <g font-size="17" fill="#1c272c">
    <text x="24" y="34" font-size="21" font-weight="700">Water sinks, collects at the low end, and feeds microbes</text>
    <text x="172" y="78" text-anchor="end">Humid air in</text><text x="172" y="96" text-anchor="end">through the vent</text>
    <text x="430" y="70">Rain at loose caps and gaskets</text>
    <text x="96" y="152" fill="#56666d">Condensation on cold walls</text>
    <text x="210" y="212">Diesel</text>
    <text x="330" y="245">Pickup at least 3 in. off the bottom</text>
    <text x="96" y="352">Microbes grow at the fuel-water line</text>
    <text x="476" y="340">Drain water</text>
    <text x="476" y="358">from the low end</text>
    <text x="360" y="298" font-size="15" fill="#ffffff" font-weight="700">Water</text>
  </g>
  <g stroke="#56666d" stroke-width="1.5" fill="none">
    
    <path d="M428 74 L412 90" marker-end="url(#wt-arrow)"/>
    <path d="M326 240 L318 240" marker-end="url(#wt-arrow)"/>
    <path d="M200 340 L250 284" marker-end="url(#wt-arrow)"/>
    <path d="M472 334 L458 326" marker-end="url(#wt-arrow)"/>
  </g>
</svg>
<figcaption>Water is heavier than diesel, so it sinks to the bottom and runs to the low end of the tank.</figcaption>
</figure>"""

TRANSFER_RULE_SVG = """<figure class="diagram">
<svg viewBox="0 0 680 300" role="img" aria-labelledby="tr-title tr-desc" xmlns="http://www.w3.org/2000/svg" font-family="Barlow Condensed, Arial Narrow, Arial, sans-serif">
  <title id="tr-title">The 119-gallon rule for diesel transfer tanks</title>
  <desc id="tr-desc">Three cases. A diesel tank of 119 gallons or less needs no placards under federal hazmat rules. A diesel tank over 119 gallons is bulk packaging and needs placards. Two tanks connected so fuel can flow between them count as one bulk package.</desc>
  <text x="24" y="34" font-size="21" font-weight="700" fill="#1c272c">For diesel, the tank's capacity decides it, not how full it is</text>
  <!-- card 1 -->
  <rect x="24" y="60" width="200" height="216" rx="6" fill="#ffffff" stroke="#1d6a48" stroke-width="3"/>
  <rect x="64" y="96" width="120" height="66" rx="18" fill="#e9d9a8" stroke="#1c272c" stroke-width="2.5"/>
  <text x="124" y="136" text-anchor="middle" font-size="22" font-weight="700" fill="#1c272c">119 gal</text>
  <text x="124" y="200" text-anchor="middle" font-size="20" font-weight="700" fill="#1d6a48">119 gallons or less</text>
  <text x="124" y="226" text-anchor="middle" font-size="17" fill="#1c272c">No placards or</text>
  <text x="124" y="246" text-anchor="middle" font-size="17" fill="#1c272c">shipping papers</text>
  <!-- card 2 -->
  <rect x="240" y="60" width="200" height="216" rx="6" fill="#ffffff" stroke="#b4462d" stroke-width="3"/>
  <rect x="270" y="90" width="140" height="78" rx="20" fill="#e9d9a8" stroke="#1c272c" stroke-width="2.5"/>
  <text x="340" y="136" text-anchor="middle" font-size="22" font-weight="700" fill="#1c272c">150 gal</text>
  <text x="340" y="200" text-anchor="middle" font-size="20" font-weight="700" fill="#b4462d">Over 119 gallons</text>
  <text x="340" y="226" text-anchor="middle" font-size="17" fill="#1c272c">Bulk package:</text>
  <text x="340" y="246" text-anchor="middle" font-size="17" fill="#1c272c">placards required</text>
  <!-- card 3 -->
  <rect x="456" y="60" width="200" height="216" rx="6" fill="#ffffff" stroke="#b4462d" stroke-width="3"/>
  <rect x="474" y="104" width="70" height="50" rx="14" fill="#e9d9a8" stroke="#1c272c" stroke-width="2.5"/>
  <rect x="568" y="104" width="70" height="50" rx="14" fill="#e9d9a8" stroke="#1c272c" stroke-width="2.5"/>
  <rect x="544" y="134" width="24" height="7" fill="#1c272c"/>
  <circle cx="556" cy="137" r="7" fill="#f0c02b" stroke="#1c272c" stroke-width="2"/>
  <text x="556" y="184" text-anchor="middle" font-size="15" fill="#56666d">valve open</text>
  <text x="556" y="210" text-anchor="middle" font-size="19" font-weight="700" fill="#b4462d">Two tanks connected</text>
  <text x="556" y="234" text-anchor="middle" font-size="17" fill="#1c272c">One bulk package;</text>
  <text x="556" y="254" text-anchor="middle" font-size="17" fill="#1c272c">close valves to drive</text>
</svg>
<figcaption>Federal hazmat rules for diesel. Gasoline is regulated more tightly; see the table below. States can add their own rules.</figcaption>
</figure>"""
