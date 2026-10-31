"""More inline SVG diagrams used in guides. Imported by build.py."""

_FONT = 'font-family="Barlow Condensed, Arial Narrow, Arial, sans-serif"'
_ARROW = lambda i: f'<marker id="{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#56666d"/></marker>'

# ---------------------------------------------------------------- overfill
OVERFILL_SVG = f"""<figure class="diagram">
<svg viewBox="0 0 680 420" role="img" aria-labelledby="of-title of-desc" xmlns="http://www.w3.org/2000/svg" {_FONT}>
  <title id="of-title">Where each overfill device acts in an underground tank</title>
  <desc id="of-desc">Side view of a buried tank. An overfill alarm at the fill must sound by 90 percent full. A ball float in the vent line must start slowing the delivery by 90 percent full. A shutoff valve in the drop tube must close by 95 percent full.</desc>
  <defs>{_ARROW('of-arrow')}<clipPath id="of-clip"><rect x="60" y="130" width="420" height="200" rx="100"/></clipPath></defs>
  <text x="24" y="34" font-size="21" font-weight="700" fill="#1c272c">Each device has to act before the tank is full</text>
  <!-- alarm on post -->
  <rect x="246" y="74" width="6" height="56" fill="#1c272c"/>
  <rect x="234" y="56" width="30" height="20" rx="3" fill="#b4462d"/>
  <text x="276" y="72" font-size="17" fill="#1c272c">Alarm at the fill sounds by 90%</text>
  <g transform="translate(0,40)">
  <!-- ground -->
  <rect x="0" y="90" width="680" height="290" fill="#efe9dc"/>
  <line x1="0" y1="90" x2="680" y2="90" stroke="#8a7a5c" stroke-width="2"/>
  <!-- fuel -->
  <g clip-path="url(#of-clip)">
    <rect x="60" y="130" width="420" height="200" fill="#f4f6f5"/>
    <rect x="60" y="160" width="420" height="180" fill="#e9d9a8"/>
  </g>
  <rect x="60" y="130" width="420" height="200" rx="100" fill="none" stroke="#1c272c" stroke-width="3"/>
  <!-- level lines -->
  <line x1="60" y1="148" x2="520" y2="148" stroke="#b4462d" stroke-width="2.5" stroke-dasharray="7 5"/>
  <line x1="60" y1="160" x2="520" y2="160" stroke="#1d6a48" stroke-width="2.5" stroke-dasharray="7 5"/>
  <!-- fill riser, spill bucket, drop tube with shutoff valve -->
  <rect x="150" y="78" width="60" height="22" fill="#c9cfcc" stroke="#1c272c" stroke-width="2"/>
  <rect x="172" y="100" width="16" height="32" fill="#1c272c"/>
  <rect x="175" y="132" width="10" height="180" fill="#56666d"/>
  <rect x="166" y="140" width="28" height="12" rx="2" fill="#f0c02b" stroke="#1c272c" stroke-width="2"/>
  <!-- vent riser with ball float -->
  <rect x="352" y="60" width="10" height="72" fill="#1c272c"/>
  <circle cx="357" cy="150" r="9" fill="#f0c02b" stroke="#1c272c" stroke-width="2"/>
  <!-- labels -->
  <g font-size="17" fill="#1c272c">
    <text x="530" y="140" font-weight="700" fill="#b4462d">95% full</text>
    <text x="530" y="176" font-weight="700" fill="#1d6a48">90% full</text>
    <text x="24" y="368">Shutoff valve in the drop tube closes by 95%</text>
    <text x="374" y="78">Ball float in the vent line</text>
    <text x="374" y="96">slows the delivery by 90%</text>
    <text x="230" y="250">Fuel</text>
  </g>
  <g stroke="#56666d" stroke-width="1.5" fill="none">
    <path d="M150 352 L176 160" marker-end="url(#of-arrow)"/>
    <path d="M370 102 L362 138" marker-end="url(#of-arrow)"/>
  </g>
  </g>
</svg>
<figcaption>Levels are by volume. In a round tank, 90% full sits well above the middle. Ball floats can't be used on new or replacement equipment.</figcaption>
</figure>"""

# ---------------------------------------------------------------- anti-siphon
ASV_SVG = f"""<figure class="diagram">
<svg viewBox="0 0 680 390" role="img" aria-labelledby="as-title as-desc" xmlns="http://www.w3.org/2000/svg" {_FONT}>
  <title id="as-title">How an elevated tank siphons and where the anti-siphon valve goes</title>
  <desc id="as-desc">A tank on a stand feeds a dispenser on the ground. The piping leaves the top of the tank, then runs down to the dispenser. If the line breaks, gravity and siphoning drain the tank. An anti-siphon valve at the tank outlet, after the shutoff valve, holds the fuel back. Size the valve to the head: the height from the highest fuel level down to the lowest point in the piping.</desc>
  <defs>{_ARROW('as-arrow')}<clipPath id="as-clip"><rect x="60" y="80" width="230" height="110" rx="50"/></clipPath></defs>
  <text x="24" y="34" font-size="21" font-weight="700" fill="#1c272c">Size the valve to the head: top fuel level to lowest piping</text>
  <!-- ground -->
  <line x1="0" y1="330" x2="680" y2="330" stroke="#8a7a5c" stroke-width="2"/>
  <!-- stand -->
  <rect x="90" y="190" width="10" height="140" fill="#56666d"/><rect x="250" y="190" width="10" height="140" fill="#56666d"/>
  <!-- tank and fuel -->
  <g clip-path="url(#as-clip)"><rect x="60" y="80" width="230" height="110" fill="#f4f6f5"/><rect x="60" y="94" width="230" height="100" fill="#e9d9a8"/></g>
  <rect x="60" y="80" width="230" height="110" rx="50" fill="none" stroke="#1c272c" stroke-width="3"/>
  <!-- outlet: suction tube, shutoff valve, anti-siphon valve -->
  <rect x="226" y="66" width="8" height="110" fill="#56666d"/>
  <path d="M230 66 L230 56 L560 56 L560 300" fill="none" stroke="#1c272c" stroke-width="7" stroke-linejoin="round"/>
  <rect x="246" y="46" width="18" height="20" fill="#1c272c"/>
  <rect x="282" y="42" width="34" height="28" rx="4" fill="#f0c02b" stroke="#1c272c" stroke-width="2.5"/>
  <!-- dispenser -->
  <rect x="530" y="250" width="70" height="80" rx="4" fill="#1d6a48"/>
  <!-- break -->
  <g stroke="#b4462d" stroke-width="3"><line x1="548" y1="160" x2="572" y2="176"/><line x1="548" y1="176" x2="572" y2="160"/></g>
  <g fill="#7fb0d6"><circle cx="578" cy="190" r="4"/><circle cx="584" cy="204" r="4"/><circle cx="578" cy="218" r="4"/></g>
  <!-- head dimension -->
  <line x1="330" y1="94" x2="330" y2="300" stroke="#1d6a48" stroke-width="2.5" marker-start="url(#as-arrow)" marker-end="url(#as-arrow)"/>
  <line x1="290" y1="94" x2="344" y2="94" stroke="#1d6a48" stroke-width="1.5" stroke-dasharray="4 4"/>
  <line x1="316" y1="300" x2="556" y2="300" stroke="#1d6a48" stroke-width="1.5" stroke-dasharray="4 4"/>
  <!-- labels -->
  <g font-size="17" fill="#1c272c">
    <text x="344" y="82" font-weight="700">Shutoff valve, then</text><text x="344" y="100" font-weight="700">anti-siphon valve</text>
    <text x="340" y="190" font-weight="700" fill="#1d6a48">Head</text>
    <text x="340" y="210">Highest fuel level down</text>
    <text x="340" y="228">to lowest piping</text>
    <text x="596" y="160">Line break:</text>
    <text x="596" y="178">the valve</text>
    <text x="596" y="196">stops the</text>
    <text x="596" y="214">siphon</text>
    <text x="540" y="356">Dispenser</text>
    <text x="120" y="356">Tank on a stand</text>
  </g>
</svg>
<figcaption>The valve stays shut against the weight of the fuel and opens only when the pump pulls or pushes.</figcaption>
</figure>"""

# ---------------------------------------------------------------- line leak detector
LLD_SVG = f"""<figure class="diagram">
<svg viewBox="0 0 680 360" role="img" aria-labelledby="ld-title ld-desc" xmlns="http://www.w3.org/2000/svg" {_FONT}>
  <title id="ld-title">What a mechanical line leak detector does when the pump turns on</title>
  <desc id="ld-desc">Line pressure over time after the pump starts. With a tight line, pressure rises, pauses at the low metering pressure for about 2 to 5 seconds, then climbs to full pump pressure and the detector opens to full flow. With a leak, pressure never gets past the metering pressure, and the detector stays in its slow-flow position.</desc>
  <text x="24" y="34" font-size="21" font-weight="700" fill="#1c272c">A tight line opens to full flow; a leaking one stays slow</text>
  <!-- axes -->
  <line x1="90" y1="70" x2="90" y2="300" stroke="#1c272c" stroke-width="2"/>
  <line x1="90" y1="300" x2="640" y2="300" stroke="#1c272c" stroke-width="2"/>
  <!-- reference levels -->
  <line x1="90" y1="110" x2="640" y2="110" stroke="#d3dbd9" stroke-width="1.5" stroke-dasharray="5 5"/>
  <line x1="90" y1="230" x2="640" y2="230" stroke="#d3dbd9" stroke-width="1.5" stroke-dasharray="5 5"/>
  <!-- tight line -->
  <path d="M90 300 L140 230 L260 230 L300 110 L640 110" fill="none" stroke="#1d6a48" stroke-width="4" stroke-linejoin="round"/>
  <!-- leaking line -->
  <path d="M90 300 L140 232 L640 232" fill="none" stroke="#b4462d" stroke-width="4" stroke-dasharray="10 6"/>
  <!-- pause bracket -->
  <path d="M140 250 L140 258 L260 258 L260 250" fill="none" stroke="#56666d" stroke-width="1.5"/>
  <g font-size="17" fill="#1c272c">
    <text x="82" y="115" text-anchor="end" font-size="15">Full</text>
    <text x="82" y="133" text-anchor="end" font-size="15">pressure</text>
    <text x="82" y="227" text-anchor="end" font-size="15">Metering</text>
    <text x="82" y="245" text-anchor="end" font-size="15">pressure</text>
    <text x="640" y="326" text-anchor="end" font-size="15" fill="#56666d">Time after the pump turns on</text>
    <text x="200" y="278" text-anchor="middle" font-size="15" fill="#56666d">pause, about 2 to 5 s</text>
    <text x="330" y="96" font-weight="700" fill="#1d6a48">No leak: detector opens, full flow</text>
    <text x="330" y="216" font-weight="700" fill="#b4462d">Leak: stuck at metering pressure, slow flow</text>
  </g>
</svg>
<figcaption>The annual test opens a calibrated 3 gallon-per-hour leak and checks that the line stays at metering pressure. Shape based on Mississippi DEQ's test procedure.</figcaption>
</figure>"""

# ---------------------------------------------------------------- nozzle
def _nozzle_panel(x0, full):
    fuel_y = 196 if full else 250
    air = "" if full else (
        f'<path d="M{x0+150} 214 L{x0+130} 196" stroke="#56666d" stroke-width="1.5" fill="none" marker-end="url(#nz-arrow)"/>'
    )
    return f"""
  <g>
    <rect x="{x0}" y="60" width="300" height="250" rx="6" fill="#ffffff" stroke="{'#b4462d' if full else '#1d6a48'}" stroke-width="3"/>
    <!-- fill neck walls -->
    <path d="M{x0+90} 150 L{x0+90} 300 M{x0+210} 150 L{x0+210} 300" stroke="#1c272c" stroke-width="3"/>
    <rect x="{x0+92}" y="{fuel_y}" width="116" height="{300-fuel_y}" fill="#e9d9a8"/>
    <!-- nozzle body and spout -->
    <rect x="{x0+20}" y="84" width="120" height="44" rx="10" fill="#56666d"/>
    <path d="M{x0+130} 110 L{x0+160} 110 L{x0+160} 210" stroke="#56666d" stroke-width="16" fill="none" stroke-linejoin="round"/>
    <!-- sensing tube back to diaphragm -->
    <path d="M{x0+156} 206 L{x0+156} 118 L{x0+64} 118" stroke="#f0c02b" stroke-width="3" fill="none"/>
    <circle cx="{x0+156}" cy="206" r="4" fill="#ffffff" stroke="#1c272c" stroke-width="1.5"/>
    <ellipse cx="{x0+56}" cy="106" rx="14" ry="14" fill="#f0c02b" stroke="#1c272c" stroke-width="2"/>
    {air}
  </g>"""

NOZZLE_SVG = f"""<figure class="diagram">
<svg viewBox="0 0 680 400" role="img" aria-labelledby="nz-title nz-desc" xmlns="http://www.w3.org/2000/svg" {_FONT}>
  <title id="nz-title">How an automatic nozzle shuts off</title>
  <desc id="nz-desc">Two panels. While filling, air is drawn in through a small hole near the spout tip, so the nozzle stays open. When fuel rises and covers the hole, the air stops, a vacuum builds, and it pulls a diaphragm that trips the nozzle closed.</desc>
  <defs>{_ARROW('nz-arrow')}</defs>
  <text x="24" y="34" font-size="21" font-weight="700" fill="#1c272c">Fuel covering a hole at the spout tip is what shuts it off</text>
  {_nozzle_panel(24, False)}
  {_nozzle_panel(356, True)}
  <g font-size="17" fill="#1c272c">
    <text x="44" y="290" font-size="15" fill="#56666d">Fill neck</text>
    <text x="240" y="204" font-size="15">Sensing</text><text x="240" y="220" font-size="15">hole</text>
    <text x="40" y="150" font-size="15">Diaphragm</text>
    <text x="118" y="192" font-size="15" fill="#56666d">air in</text>
    <text x="174" y="338" text-anchor="middle" font-weight="700" fill="#1d6a48">Filling: air flows in,</text>
    <text x="174" y="358" text-anchor="middle" font-weight="700" fill="#1d6a48">nozzle stays open</text>
    <text x="506" y="338" text-anchor="middle" font-weight="700" fill="#b4462d">Full: fuel covers the hole,</text>
    <text x="506" y="358" text-anchor="middle" font-weight="700" fill="#b4462d">vacuum trips it closed</text>
  </g>
</svg>
<figcaption>Splash-back that covers the hole early is why a nozzle clicks off before the tank is full. Based on PEI's description of the automatic nozzle.</figcaption>
</figure>"""

# ---------------------------------------------------------------- spill bucket
SPILL_SVG = f"""<figure class="diagram">
<svg viewBox="0 0 680 400" role="img" aria-labelledby="sb-title sb-desc" xmlns="http://www.w3.org/2000/svg" {_FONT}>
  <title id="sb-title">Parts of a UST spill bucket</title>
  <desc id="sb-desc">Cross-section at the fill of an underground tank. A lid sits flush with the pavement. Below it, the spill bucket surrounds the top of the fill riser. The fill cap has a gasket, and the drop tube runs down into the tank. A drain valve in the bottom of the bucket can let liquid into the tank.</desc>
  <defs>{_ARROW('sb-arrow')}</defs>
  <text x="24" y="34" font-size="21" font-weight="700" fill="#1c272c">The spill bucket catches drips when the hose comes off</text>
  <!-- ground -->
  <rect x="0" y="80" width="680" height="320" fill="#efe9dc"/>
  <rect x="0" y="80" width="680" height="12" fill="#9aa3a0"/>
  <!-- lid -->
  <rect x="190" y="70" width="200" height="12" rx="2" fill="#1c272c"/>
  <!-- bucket -->
  <path d="M206 92 L224 230 L356 230 L374 92" fill="#f4f6f5" stroke="#1c272c" stroke-width="3"/>
  <!-- riser -->
  <rect x="276" y="150" width="28" height="200" fill="#56666d"/>
  <rect x="270" y="138" width="40" height="14" rx="2" fill="#1c272c"/>
  <rect x="270" y="150" width="40" height="5" fill="#f0c02b"/>
  <!-- drop tube -->
  <rect x="282" y="230" width="16" height="150" fill="#c9cfcc" stroke="#1c272c" stroke-width="1.5"/>
  <rect x="276" y="226" width="28" height="6" fill="#f0c02b"/>
  <!-- drain valve -->
  <rect x="326" y="220" width="16" height="12" fill="#1d6a48"/>
  <!-- tank top -->
  <path d="M120 360 Q290 340 460 360" fill="none" stroke="#1c272c" stroke-width="3"/>
  <g font-size="17" fill="#1c272c">
    <text x="400" y="66">Lid: keeps water and debris out</text>
    <text x="400" y="132">Spill bucket</text>
    <text x="24" y="132">Fill cap and gasket</text>
    <text x="24" y="196">Drop tube gasket</text>
    <text x="400" y="216">Drain valve</text>
    <text x="400" y="290">Fill riser and drop tube</text>
    <text x="400" y="308">down to the tank</text>
    <text x="474" y="378" fill="#56666d">Tank</text>
  </g>
  <g stroke="#56666d" stroke-width="1.5" fill="none">
    <path d="M396 128 L366 128" marker-end="url(#sb-arrow)"/>
    <path d="M160 128 L266 144" marker-end="url(#sb-arrow)"/>
    <path d="M148 192 L272 228" marker-end="url(#sb-arrow)"/>
    <path d="M396 212 L346 224" marker-end="url(#sb-arrow)"/>
    <path d="M396 286 L302 286" marker-end="url(#sb-arrow)"/>
  </g>
</svg>
<figcaption>Single-wall buckets get a liquid-tightness test every 3 years. Check the gaskets whenever the bucket is open.</figcaption>
</figure>"""
