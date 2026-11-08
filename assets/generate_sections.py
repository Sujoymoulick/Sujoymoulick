"""Animated minimal section cards: about, section titles, project cards, connect buttons.
Usage: python3 assets/generate_sections.py assets"""
import os, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"
MONO = "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"
SANS = "'Segoe UI','Inter',Helvetica,Arial,sans-serif"
BG, LINE, TXT, MUTED = "#0b0f1a", "#1f2a44", "#e6edf3", "#8b9bb4"
CY, VI, PK, GR = "#00f7ff", "#a855f7", "#ff3d9a", "#7cff9b"


def save(name, s):
    open(os.path.join(OUT, name), "w").write(s); print(name, f"{len(s)/1024:.1f} KB")


def fade(begin, dy=10):
    return (f'<animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur=".7s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 {dy}" to="0 0" begin="{begin}s" dur=".7s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/>')


def title(label, accent):
    """Small centered section title: // LABEL with a line that draws out on both sides."""
    W, H = 1280, 64
    tw = len(label) * 15 + 50
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{accent}" stop-opacity="0"/><stop offset="1" stop-color="{accent}"/></linearGradient>
<linearGradient id="r" x1="1" x2="0"><stop offset="0" stop-color="{accent}" stop-opacity="0"/><stop offset="1" stop-color="{accent}"/></linearGradient></defs>
<rect x="{W/2-tw/2-20}" y="31" height="1.5" width="0" fill="url(#l)"><animate attributeName="x" from="{W/2-tw/2-20}" to="40" dur="1s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/><animate attributeName="width" from="0" to="{W/2-tw/2-60:.0f}" dur="1s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>
<rect x="{W/2+tw/2+20}" y="31" height="1.5" width="0" fill="url(#r)"><animate attributeName="width" from="0" to="{W/2-tw/2-60:.0f}" dur="1s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>
<g opacity="0">{fade(.2, 6)}
<text x="{W/2}" y="39" text-anchor="middle" font-family="{MONO}" font-size="20" font-weight="700" letter-spacing="4" fill="{TXT}"><tspan fill="{accent}">// </tspan>{label}</text></g>
</svg>'''


def about():
    W, H = 1280, 280
    rows = [
        [("I'm ", TXT, 400), ("Sujoy Moulick", CY, 700), (" — B.Tech CSE student &amp; full-stack developer.", TXT, 400)],
        [("I build ", MUTED, 400), ("digital products", TXT, 600), (", ", MUTED, 400), ("AI-powered tools", TXT, 600), (", ", MUTED, 400),
         ("browser extensions", TXT, 600), (" and ", MUTED, 400), ("open-source apps", TXT, 600), (".", MUTED, 400)],
        [("This profile is my ", MUTED, 400), ("workspace &amp; portfolio", VI, 700), (" — experiment, learn, ship.", MUTED, 400)],
    ]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'''<defs><linearGradient id="b" x1="0" x2="1"><stop offset="0" stop-color="{CY}"/><stop offset=".5" stop-color="{VI}"/><stop offset="1" stop-color="{PK}"/></linearGradient></defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="{BG}" stroke="{LINE}"/>
<rect x="1" y="1" width="0" height="3" rx="1.5" fill="url(#b)"><animate attributeName="width" from="0" to="{W-2}" dur="1.2s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>''']
    y = 82
    for i, row in enumerate(rows):
        spans = "".join(f'<tspan fill="{c}" font-weight="{w}">{t}</tspan>' for t, c, w in row)
        size = 26 if i == 0 else 20
        out.append(f'<g opacity="0">{fade(.3 + i * .35)}<text x="{W/2}" y="{y}" text-anchor="middle" font-family="{SANS}" font-size="{size}">{spans}</text></g>')
        y += 54 if i == 0 else 46
    # tiny status chips
    chips = [("AI / ML", CY), ("Full-Stack", VI), ("SaaS", PK), ("Open Source", GR)]
    total = sum(len(t) * 8.4 + 34 for t, _ in chips) + 12 * (len(chips) - 1)
    x = W / 2 - total / 2
    for i, (t, c) in enumerate(chips):
        w = len(t) * 8.4 + 34
        out.append(f'<g opacity="0">{fade(1.4 + i * .12, 6)}<rect x="{x:.0f}" y="{H-58}" width="{w:.0f}" height="28" rx="14" fill="{c}" fill-opacity=".08" stroke="{c}" stroke-opacity=".45"/>'
                   f'<circle cx="{x+14:.0f}" cy="{H-44}" r="3" fill="{c}"><animate attributeName="opacity" values="1;.25;1" dur="2s" begin="{i*.3:.1f}s" repeatCount="indefinite"/></circle>'
                   f'<text x="{x+24:.0f}" y="{H-39}" font-family="{MONO}" font-size="13" fill="{TXT}">{t}</text></g>')
        x += w + 12
    out.append('</svg>')
    return "\n".join(out)


def project(name, desc, tag, url_label, accent, delay):
    W, H = 400, 210
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  <linearGradient id="t" x1="0" x2="1"><stop offset="0" stop-color="{accent}" stop-opacity="0"/><stop offset=".5" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient>
  <radialGradient id="g" cx=".85" cy=".1" r=".7"><stop offset="0" stop-color="{accent}" stop-opacity=".16"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
  <clipPath id="c"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16"/></clipPath>
</defs>
<g opacity="0">{fade(delay, 14)}
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="{BG}" stroke="{LINE}"/>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#g)"/>
  <rect y="1" width="160" height="2" fill="url(#t)"><animate attributeName="x" values="-160;{W}" dur="3s" begin="{delay}s" repeatCount="indefinite"/></rect>
</g>
<circle cx="32" cy="38" r="4" fill="{accent}"><animate attributeName="r" values="4;9;4" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0;1" dur="2s" repeatCount="indefinite"/></circle>
<circle cx="32" cy="38" r="4" fill="{accent}"/>
<text x="46" y="43" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{accent}">{tag}</text>
<text x="28" y="100" font-family="{SANS}" font-size="30" font-weight="800" fill="{TXT}">{name}</text>
<text x="28" y="132" font-family="{SANS}" font-size="15" fill="{MUTED}">{desc}</text>
<line x1="28" y1="160" x2="{W-28}" y2="160" stroke="{LINE}"/>
<text x="28" y="186" font-family="{MONO}" font-size="13" fill="{MUTED}">{url_label}</text>
<g font-family="{MONO}" font-size="16" fill="{accent}"><text x="{W-44}" y="187">→<animateTransform attributeName="transform" type="translate" values="0 0;6 0;0 0" dur="1.6s" repeatCount="indefinite"/></text></g>
</g>
</svg>'''


def button(label, glyph, accent, delay):
    W, H = 230, 56
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs><linearGradient id="s" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".18"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="c"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="28"/></clipPath></defs>
<g opacity="0">{fade(delay, 8)}
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="28" fill="{BG}" stroke="{accent}" stroke-opacity=".55"/>
<g clip-path="url(#c)"><rect y="0" width="70" height="{H}" fill="url(#s)" transform="skewX(-20)"><animate attributeName="x" values="-120;{W+60}" dur="3.2s" begin="{delay+.5}s" repeatCount="indefinite"/></rect></g>
<circle cx="30" cy="28" r="15" fill="{accent}" fill-opacity=".14"/>
<text x="30" y="33" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700" fill="{accent}">{glyph}</text>
<text x="56" y="34" font-family="{MONO}" font-size="16" font-weight="700" letter-spacing="2" fill="{TXT}">{label}</text>
<text x="{W-28}" y="34" font-family="{MONO}" font-size="16" fill="{accent}">↗</text>
</g>
</svg>'''


save("title-about.svg", title("ABOUT_ME", CY))
save("title-projects.svg", title("SAAS_PROJECTS", PK))
save("title-connect.svg", title("CONNECT", VI))
save("about.svg", about())
save("project-echotodo.svg", project("EchoToDo", "Voice-powered productivity &amp; todo", "EXTENSION", "chrome extension", VI, .1))
save("project-freepdfly.svg", project("FreePDFly", "Browser-based PDF toolkit", "LIVE SAAS", "freepdfly.com", CY, .3))
save("project-sendvirtualgift.svg", project("SendVirtualGift", "Send virtual gifts online", "LIVE SAAS", "sendvirtualgift.com", PK, .5))
save("btn-linkedin.svg", button("LINKEDIN", "in", "#0a66c2", .1))
save("btn-github.svg", button("GITHUB", "&lt;/&gt;", GR, .25))
save("btn-portfolio.svg", button("PORTFOLIO", "◆", CY, .4))
