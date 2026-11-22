"""Retro red / black / gray profile assets for github.com/Sujoymoulick.
Everything animates with SMIL + CSS inside the SVG, because GitHub READMEs
cannot run JavaScript. The scroll-reactive three.js version lives in index.html.

Usage: python3 build.py <out_dir> <fonts_dir> <portrait.jpg>
"""
import base64, math, os, sys

OUT, FONTS, PORTRAIT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)

BG, PANEL, LINE, DIM = "#0b0b0b", "#111111", "#262626", "#4a4a4a"
GRAY, PAPER, RED, DRED = "#8c8c8c", "#ece8e1", "#e1251b", "#7a120d"
MONO = "'SM Mono','Courier New',monospace"
DISP = "'SM Display',Impact,'Arial Narrow',sans-serif"


def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()


FONT_CSS = (
    "@font-face{font-family:'SM Display';src:url(data:font/woff2;base64,%s) format('woff2')}"
    "@font-face{font-family:'SM Mono';font-weight:400;src:url(data:font/woff2;base64,%s) format('woff2')}"
    "@font-face{font-family:'SM Mono';font-weight:700;src:url(data:font/woff2;base64,%s) format('woff2')}"
) % (b64(f"{FONTS}/anton-latin-400-normal.sub.woff2"),
     b64(f"{FONTS}/space-mono-latin-400-normal.sub.woff2"),
     b64(f"{FONTS}/space-mono-latin-700-normal.sub.woff2"))

BASE_CSS = """
.m{font-family:%s}.d{font-family:%s}
@keyframes blink{50%%{opacity:0}}
@keyframes roll{from{transform:translateY(0)}to{transform:translateY(8px)}}
@keyframes flick{0%%,100%%{opacity:.07}50%%{opacity:.11}93%%{opacity:.07}94%%{opacity:.16}95%%{opacity:.07}}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes draw{to{stroke-dashoffset:0}}
.blink{animation:blink 1.1s steps(1) infinite}
.scan{animation:roll .6s linear infinite}
.flick{animation:flick 4s infinite}
""" % (MONO, DISP)


def svg(w, h, body, css="", label="", fonts=True):
    style = (FONT_CSS if fonts else "") + BASE_CSS + css
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(label)}">'
            f'<style>{style}</style>'
            f'<defs><pattern id="sl" width="4" height="4" patternUnits="userSpaceOnUse">'
            f'<rect width="4" height="1.4" fill="#000"/></pattern>'
            f'<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">'
            f'<path d="M40 0H0V40" fill="none" stroke="#171717" stroke-width="1"/></pattern></defs>'
            f'{body}</svg>')


def save(name, s):
    open(os.path.join(OUT, name), "w").write(s)
    print(f"{name:28s} {len(s)/1024:7.1f} KB")


def scanlines(w, h):
    return (f'<g pointer-events="none"><rect y="-8" width="{w}" height="{h+16}" fill="url(#sl)" opacity=".35" class="scan"/>'
            f'<rect width="{w}" height="{h}" fill="{PAPER}" class="flick" style="mix-blend-mode:overlay" opacity=".07"/></g>')


def crops(w, h, m=14, l=18, c=DIM):
    p = []
    for x, y, dx, dy in [(m, m, 1, 1), (w-m, m, -1, 1), (m, h-m, 1, -1), (w-m, h-m, -1, -1)]:
        p.append(f'<path d="M{x} {y+dy*l}V{y}H{x+dx*l}" fill="none" stroke="{c}" stroke-width="1.5"/>')
    return "".join(p)


def arrow(x, y, s=1, color=RED, diag=False):
    if diag:
        return (f'<g transform="translate({x} {y}) scale({s})" stroke="{color}" stroke-width="2.4" fill="none" stroke-linecap="square">'
                f'<path d="M0 12L12 0M3 0H12V9"/></g>')
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{color}" stroke-width="2.4" fill="none" stroke-linecap="square">'
            f'<path d="M0 6H14M9 1L14 6L9 11"/></g>')


from fontTools.ttLib import TTFont
_anton = TTFont(f"{FONTS}/anton-latin-400-normal.sub.woff2")
def disp_width(text, size):
    cmap, hm, upm = _anton.getBestCmap(), _anton["hmtx"], _anton["head"].unitsPerEm
    return sum(hm[cmap[ord(c)]][0] for c in text if ord(c) in cmap) * size / upm


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------ 3D helpers
F = 72


def rot(p, ax, ay, az):
    x, y, z = p
    c, s = math.cos(ax), math.sin(ax); y, z = y*c - z*s, y*s + z*c
    c, s = math.cos(ay), math.sin(ay); x, z = x*c + z*s, -x*s + z*c
    c, s = math.cos(az), math.sin(az); x, y = x*c - y*s, x*s + y*c
    return x, y, z


def proj(p, cx, cy, sc, cam=4.2):
    x, y, z = p
    k = cam / (cam - z)
    return cx + x*sc*k, cy + y*sc*k, z


def A(attr, seq, dur):
    return f'<animate attributeName="{attr}" dur="{dur}s" repeatCount="indefinite" values="{";".join(seq + [seq[0]])}"/>'


def wire(verts, edges, cx, cy, sc, spin, dur, color, width=1.6, nodes=True, node_color=PAPER):
    frames = [[proj(rot(p, *spin(2*math.pi*k/F)), cx, cy, sc) for p in verts] for k in range(F)]
    out = []
    for i, j in edges:
        g = lambda idx, n: [f"{fr[idx][n]:.1f}" for fr in frames]
        op = [f"{.12 + .88*((fr[i][2]+fr[j][2])/2+1)/2:.2f}" for fr in frames]
        out.append(f'<line stroke="{color}" stroke-width="{width}" stroke-linecap="round">'
                   + A("x1", g(i, 0), dur) + A("y1", g(i, 1), dur) + A("x2", g(j, 0), dur) + A("y2", g(j, 1), dur)
                   + A("stroke-opacity", op, dur) + '</line>')
    if nodes:
        for i in range(len(verts)):
            out.append(f'<rect width="5" height="5" fill="{node_color}">'
                       + A("x", [f"{fr[i][0]-2.5:.1f}" for fr in frames], dur)
                       + A("y", [f"{fr[i][1]-2.5:.1f}" for fr in frames], dur)
                       + A("opacity", [f"{.15+.85*(fr[i][2]+1)/2:.2f}" for fr in frames], dur) + '</rect>')
    return "".join(out)


def icosa():
    t = (1 + 5**.5) / 2
    v = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t),
         (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    n = math.sqrt(1 + t*t); v = [(a/n, b/n, c/n) for a, b, c in v]
    e = [(i, j) for i in range(12) for j in range(i+1, 12) if abs(math.dist(v[i], v[j]) - 2/n) < 1e-6]
    return v, e


def cube(s=1):
    v = [(x*s, y*s, z*s) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    e = [(i, j) for i in range(8) for j in range(i+1, 8) if sum(a != b for a, b in zip(v[i], v[j])) == 1]
    return v, e


def ring(r, n, tilt=0):
    v = [(r*math.cos(2*math.pi*k/n), r*math.sin(2*math.pi*k/n)*math.sin(tilt), r*math.sin(2*math.pi*k/n)*math.cos(tilt)) for k in range(n)]
    return v, [(k, (k+1) % n) for k in range(n)]


# ------------------------------------------------------------------ typewriter
def typewriter(x, y, roles, size=26, color=PAPER, cw=None, slot=4.6):
    cw = cw or size * 0.612  # Space Mono advance
    T = slot * len(roles)
    out = []
    for i, r in enumerate(roles):
        n = len(r)
        t_type, t_hold, t_erase = n*0.045, slot - n*0.045 - n*0.018 - .25, n*0.018
        times, widths = [], []
        for k in range(n+1):
            times.append(k*0.045); widths.append(k*cw)
        hold_end = t_type + t_hold
        for k in range(n, -1, -1):
            times.append(hold_end + (n-k)*0.018); widths.append(k*cw)
        times.append(T); widths.append(0)
        kt = ";".join(f"{t/T:.5f}" for t in times)
        wv = ";".join(f"{w:.1f}" for w in widths)
        xv = ";".join(f"{x+w:.1f}" for w in widths)
        begin = f"{i*slot:.2f}s"
        cid = f"tw{i}"
        out.append(f'<clipPath id="{cid}"><rect x="{x}" y="{y-size}" height="{size*1.4}" width="0">'
                   f'<animate attributeName="width" dur="{T}s" begin="{begin}" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{wv}"/></rect></clipPath>')
        out.append(f'<text x="{x}" y="{y}" class="m" font-size="{size}" fill="{color}" clip-path="url(#{cid})">{esc(r)}</text>')
        out.append(f'<rect y="{y-size*.82}" width="{cw*.9:.1f}" height="{size*.98:.1f}" fill="{RED}" x="{x}" opacity="0">'
                   f'<animate attributeName="x" dur="{T}s" begin="{begin}" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{xv}"/>'
                   f'<animate attributeName="opacity" dur="{T}s" begin="{begin}" repeatCount="indefinite" calcMode="discrete" keyTimes="0;{(slot-.05)/T:.4f}" values="1;0"/></rect>')
    return "".join(out)


def ticker(y, w, items, size=18, color=GRAY, speed=40, sep_color=RED):
    """Seamless marquee: two copies of the same strip translating by one strip width."""
    cw = size * 0.612
    parts, x = [], 0
    for it in items:
        parts.append(f'<text x="{x:.1f}" y="{y}" class="m" font-size="{size}" fill="{color}" letter-spacing="0">{esc(it)}</text>')
        x += len(it)*cw + 22
        parts.append(f'<rect x="{x:.1f}" y="{y-size*.55:.1f}" width="8" height="8" fill="{sep_color}" transform="rotate(45 {x+4:.1f} {y-size*.55+4:.1f})"/>')
        x += 30
    strip = "".join(parts)
    reps = math.ceil(w / x) + 1
    copies = "".join(f'<g transform="translate({k*x:.1f} 0)">{strip}</g>' for k in range(reps))
    dur = x / speed
    return (f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="{-x:.1f} 0" dur="{dur:.1f}s" repeatCount="indefinite"/>'
            f'{copies}</g>')


# ================================================================== HERO
def hero():
    W, H = 1280, 560
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#grid)"/>']
    # top meta bar
    b.append(f'<g class="m" font-size="15" fill="{GRAY}" letter-spacing="2">'
             f'<text x="48" y="52">SM/26</text><text x="150" y="52" fill="{DIM}">────</text>'
             f'<text x="230" y="52">PROFILE.SYS</text><text x="410" y="52" fill="{DIM}">────</text><text x="490" y="52">JAIPUR, IN</text>'
             f'<circle cx="{W-150}" cy="47" r="6" fill="{RED}" class="blink"/><text x="{W-134}" y="52" fill="{PAPER}">ONLINE</text></g>')
    b.append(f'<line x1="48" y1="72" x2="{W-48}" y2="72" stroke="{LINE}"/>')
    # 3D object (right)
    cx, cy = 1000, 300
    v, e = icosa()
    b.append(f'<circle cx="{cx}" cy="{cy}" r="190" fill="none" stroke="{LINE}" stroke-dasharray="2 8"/>')
    b.append(f'<g><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="40s" repeatCount="indefinite"/>'
             f'<circle cx="{cx}" cy="{cy}" r="214" fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="60 1284" />'
             f'<circle cx="{cx}" cy="{cy}" r="214" fill="none" stroke="{DIM}" stroke-width="1" stroke-dasharray="4 10" /></g>')
    b.append(f'<ellipse cx="{cx}" cy="{cy}" ry="60" fill="none" stroke="{GRAY}" stroke-opacity=".5" transform="rotate(-18 {cx} {cy})">' + A("rx", [f"{190*abs(math.cos(2*math.pi*k/F)):.1f}" for k in range(F)], 24) + '</ellipse>')
    b.append(wire(v, e, cx, cy, 128, lambda a: (a*0.6, a, a*0.25), 20, RED, 1.8))
    vi, ei = cube(.34)
    b.append(wire(vi, ei, cx, cy, 128, lambda a: (-a, a*2, 0), 20, PAPER, 1.2, nodes=False))
    b.append(f'<g class="m" font-size="13" fill="{GRAY}" letter-spacing="2"><text x="{cx-210}" y="{cy+250}">FIG.00 — ICOSA_R1</text>'
             f'<text x="{cx+210}" y="{cy+250}" text-anchor="end">ROT 360°/20S</text></g>')
    # name block
    b.append(f'<g style="animation:fade .6s .1s both"><text x="48" y="112" class="m" font-size="17" fill="{RED}" letter-spacing="3">B.TECH CSE (AIML) · UEM JAIPUR · CLASS OF 2028</text></g>')
    for i, (word, y) in enumerate([("SUJOY", 272), ("MOULICK", 400)]):
        cid = f"nm{i}"
        b.append(f'<clipPath id="{cid}"><rect x="40" y="{y-140}" height="160" width="0">'
                 f'<animate attributeName="width" from="0" to="820" begin="{.2+i*.25}s" dur=".9s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".7 0 .2 1"/></rect></clipPath>')
        b.append(f'<rect x="40" y="{y-128}" height="138" width="0" fill="{RED}">'
                 f'<animate attributeName="width" values="0;{560 if i==0 else 700};0" keyTimes="0;.5;1" begin="{.1+i*.25}s" dur=".9s" fill="freeze"/>'
                 f'<animate attributeName="x" values="40;40;{600 if i==0 else 740}" keyTimes="0;.5;1" begin="{.1+i*.25}s" dur=".9s" fill="freeze"/></rect>')
        b.append(f'<text x="44" y="{y}" class="d" font-size="152" fill="{PAPER}" letter-spacing="2" clip-path="url(#{cid})">{word}</text>')
    b.append(f'<path d="M48 430H360" stroke="{RED}" stroke-width="6" stroke-dasharray="312" stroke-dashoffset="312" style="animation:draw 1s 1.1s forwards"/>')
    b.append(f'<text x="48" y="476" class="m" font-size="19" fill="{GRAY}">$</text>')
    b.append(typewriter(74, 476, ["AI developer — LLM tools & automation",
                                  "Full-stack engineer — React / Astro / Node",
                                  "SaaS builder — FreePDFly, SendVirtualGift"], size=22))
    # bottom bar + ticker
    b.append(f'<line x1="0" y1="506" x2="{W}" y2="506" stroke="{LINE}"/><rect y="507" width="{W}" height="{H-507}" fill="{PANEL}"/>')
    b.append(f'<svg x="0" y="507" width="{W-300}" height="{H-507}">{ticker(33, W, ["AI DEVELOPER", "FULL-STACK ENGINEER", "SAAS BUILDER", "OPEN SOURCE", "TECHNICAL HEAD @ TSS", "FOUNDER @ ASCELSTACK"], 16)}</svg>')
    b.append(f'<rect x="{W-300}" y="507" width="300" height="{H-507}" fill="{RED}"/>'
             f'<text x="{W-276}" y="540" class="m" font-size="15" font-weight="700" fill="{BG}" letter-spacing="2">ENTER 3D SITE</text>'
             + arrow(W-62, 528, 1, BG))
    b.append(crops(W, H))
    b.append(scanlines(W, H))
    return svg(W, H, "".join(b), label="Sujoy Moulick — AI developer, full-stack engineer, SaaS builder")


# ================================================================== PROFILE
def profile():
    W, H = 1280, 640
    img = "data:image/jpeg;base64," + b64(PORTRAIT)
    PX, PY, PW, PH = 48, 48, 448, 558
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    b.append(f'<clipPath id="pc"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}"/></clipPath>')
    b.append(f'<g clip-path="url(#pc)"><image x="{PX}" y="{PY-6}" width="{PW}" height="{PH*1.0+6}" preserveAspectRatio="xMidYMin slice" href="{img}" xlink:href="{img}">'
             f'<animate attributeName="opacity" values="0;1;.6;1" keyTimes="0;.5;.7;1" dur="1s" fill="freeze"/></image>'
             f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="url(#sl)" opacity=".45"/>'
             f'<rect x="{PX}" width="{PW}" height="70" fill="{RED}" opacity=".18"><animate attributeName="y" from="{PY-70}" to="{PY+PH}" dur="3.2s" repeatCount="indefinite"/></rect>'
             f'<rect x="{PX}" width="{PW}" height="2" fill="{RED}"><animate attributeName="y" from="{PY}" to="{PY+PH+70}" dur="3.2s" repeatCount="indefinite"/></rect></g>')
    b.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="none" stroke="{LINE}"/>')
    b.append(f'<rect x="{PX}" y="{PY+PH-40}" width="{PW}" height="40" fill="{BG}" opacity=".85"/>'
             f'<g class="m" font-size="14" fill="{PAPER}" letter-spacing="2"><text x="{PX+16}" y="{PY+PH-14}">FIG.01 — S.MOULICK</text>'
             f'<text x="{PX+PW-16}" y="{PY+PH-14}" text-anchor="end" fill="{RED}">REC</text></g>'
             f'<circle cx="{PX+PW-62}" cy="{PY+PH-19}" r="5" fill="{RED}" class="blink"/>')
    # spec sheet
    X = 548; R = W - 48
    b.append(f'<text x="{X}" y="74" class="m" font-size="15" fill="{RED}" letter-spacing="3">SPEC SHEET / NO.0001</text>'
             f'<text x="{R}" y="74" class="m" font-size="15" fill="{GRAY}" text-anchor="end" letter-spacing="2">REV.2026</text>'
             f'<line x1="{X}" y1="90" x2="{R}" y2="90" stroke="{LINE}"/>')
    b.append(f'<text x="{X}" y="150" class="d" font-size="58" fill="{PAPER}" letter-spacing="1" style="animation:rise .6s .2s both">SUJOY MOULICK</text>')
    b.append(f'<text x="{X}" y="184" class="m" font-size="17" fill="{GRAY}" style="animation:rise .6s .35s both">Developer · Builder · Content Creator</text>')
    rows = [("LANGUAGES", "C / C++ / Java / Python / JavaScript"),
            ("AI", "LangChain / AI automation / LLM tools"),
            ("FRONTEND", "React / Next.js / Astro / Tailwind"),
            ("BACKEND", "Node.js / Express"),
            ("DATA", "MongoDB / MySQL / Supabase"),
            ("INFRA", "Docker / AWS / Vercel / Cloudflare"),
            ("TOOLS", "Git / Postman / Linux / VS Code"),
            ("ROLES", "Technical Head @ TSS · Founder @ Ascelstack")]
    y = 236
    for i, (k, v) in enumerate(rows):
        d = .5 + i*.12
        b.append(f'<g style="animation:rise .45s {d:.2f}s both">'
                 f'<text x="{X}" y="{y}" class="m" font-size="14" fill="{RED}">{i+1:02d}</text>'
                 f'<text x="{X+40}" y="{y}" class="m" font-size="15" font-weight="700" fill="{GRAY}" letter-spacing="2">{k}</text>'
                 f'<text x="{X+200}" y="{y}" class="m" font-size="17" fill="{PAPER}">{esc(v)}</text>'
                 f'<line x1="{X}" y1="{y+14}" x2="{R}" y2="{y+14}" stroke="#1b1b1b"/></g>')
        y += 40
    # meters
    y += 26
    for i, (k, pct, val) in enumerate([("STATUS: BUILDING", .82, "82%"), ("LEARNING", 1.0, "DAILY")]):
        d = 1.6 + i*.2
        bw = R - X - 280
        segs = 34
        sw = bw / segs
        b.append(f'<text x="{X}" y="{y+4}" class="m" font-size="14" fill="{GRAY}" letter-spacing="2">{k}</text>')
        for s in range(segs):
            on = s < round(segs*pct)
            col = RED if on else "#1d1d1d"
            b.append(f'<rect x="{X+200+s*sw:.1f}" y="{y-10}" width="{sw-3:.1f}" height="16" fill="{col}" opacity="{0 if on else 1}">'
                     + (f'<set attributeName="opacity" to="1" begin="{d+s*.03:.2f}s"/>' if on else '') + '</rect>')
        b.append(f'<text x="{R}" y="{y+4}" class="m" font-size="14" fill="{PAPER}" text-anchor="end">{val}</text>')
        y += 34
    b.append(crops(W, H))
    b.append(scanlines(W, H))
    return svg(W, H, "".join(b), label="Sujoy Moulick — portrait and spec sheet: languages, AI, frontend, backend, data, infra, tools")


# ================================================================== SECTION HEAD
def head(num, label, note):
    W, H = 1280, 120
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    b.append(f'<text x="48" y="92" class="d" font-size="80" fill="none" stroke="{RED}" stroke-width="1.6">{num}</text>')
    b.append(f'<text x="160" y="92" class="d" font-size="80" fill="{PAPER}" style="animation:rise .6s both">{label}</text>')
    lx = 160 + disp_width(label, 80) + 30
    b.append(f'<line x1="{lx}" y1="62" x2="{W-48}" y2="62" stroke="{LINE}" stroke-width="2" stroke-dasharray="{W}" stroke-dashoffset="{W}" style="animation:draw 1.2s .3s forwards"/>')
    b.append(f'<rect x="{lx}" y="58" width="40" height="8" fill="{RED}"><animate attributeName="x" values="{lx};{W-88};{lx}" dur="7s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".6 0 .4 1;.6 0 .4 1"/></rect>')
    b.append(f'<text x="{W-48}" y="96" class="m" font-size="14" fill="{GRAY}" text-anchor="end" letter-spacing="3">{note}</text>')
    return svg(W, H, "".join(b), label=f"{num} {label}")


# ================================================================== ABOUT
def about():
    W, H = 1280, 330
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    b.append(f'<rect x="48" y="20" width="4" height="{H-120}" fill="{RED}"/>')
    lines = [
        [("I'm ", PAPER), ("Sujoy Moulick", RED), (" — B.Tech CSE (AIML) student and", PAPER)],
        [("full-stack developer. I build ", PAPER), ("digital products", RED), (", AI-powered", PAPER)],
        [("tools, browser extensions and open-source apps.", PAPER)],
        [("This profile is my workspace: experiment, learn, ship.", GRAY)],
    ]
    y = 64
    for i, ln in enumerate(lines):
        spans = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in ln)
        size = 30 if i < 3 else 22
        b.append(f'<text x="80" y="{y}" class="m" font-size="{size}" style="animation:rise .6s {.15+i*.18:.2f}s both">{spans}</text>')
        y += 50 if i < 2 else 56
    chips = ["AI / ML", "FULL-STACK", "SAAS", "OPEN SOURCE", "CONTENT"]
    x = 80
    for i, c in enumerate(chips):
        w = len(c)*9.2 + 44
        b.append(f'<g style="animation:fade .4s {1+i*.12:.2f}s both"><rect x="{x}" y="{H-62}" width="{w:.0f}" height="34" fill="none" stroke="{DIM}"/>'
                 f'<rect x="{x+12}" y="{H-49}" width="8" height="8" fill="{RED if i==0 else GRAY}"/>'
                 f'<text x="{x+28}" y="{H-39}" class="m" font-size="15" fill="{PAPER}" letter-spacing="1">{c}</text></g>')
        x += w + 12
    return svg(W, H, "".join(b), label="I'm Sujoy Moulick — B.Tech CSE (AIML) student and full-stack developer building digital products, AI tools, browser extensions and open-source apps.")


# ================================================================== PROJECT CARD
def project(no, name, desc, tag, url, delay, glyph):
    W, H = 420, 300
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/><rect x="1" y="1" width="{W-2}" height="{H-2}" fill="{PANEL}" stroke="{LINE}"/>']
    b.append(f'<rect x="1" y="1" width="0" height="5" fill="{RED}"><animate attributeName="width" from="0" to="{W-2}" begin="{delay}s" dur=".9s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".7 0 .2 1"/></rect>')
    b.append(f'<text x="26" y="44" class="m" font-size="14" fill="{RED}" letter-spacing="2">NO.{no}</text>'
             f'<text x="{W-26}" y="44" class="m" font-size="14" fill="{GRAY}" letter-spacing="2" text-anchor="end">{tag}</text>')
    b.append(glyph)
    b.append(f'<text x="26" y="200" class="d" font-size="40" fill="{PAPER}" style="animation:rise .6s {delay+.2:.2f}s both">{esc(name)}</text>')
    b.append(f'<text x="26" y="230" class="m" font-size="15" fill="{GRAY}">{esc(desc)}</text>')
    b.append(f'<line x1="26" y1="252" x2="{W-26}" y2="252" stroke="{LINE}"/>')
    b.append(f'<circle cx="32" cy="273" r="4" fill="{RED}" class="blink"/><text x="44" y="278" class="m" font-size="14" fill="{PAPER}">{esc(url)}</text>')
    b.append(f'<g>{arrow(W-44, 266, 1, RED, diag=True)}<animateTransform attributeName="transform" type="translate" values="0 0;4 -4;0 0" dur="1.6s" repeatCount="indefinite"/></g>')
    return svg(W, H, "".join(b), label=f"{name} — {desc}")


def glyph_voice():
    bars = []
    for i in range(16):
        x = 26 + i*16
        hs = [8 + abs(math.sin(i*.7 + k))*44 for k in range(6)]
        vals = ";".join(f"{h:.0f}" for h in hs + [hs[0]])
        ys = ";".join(f"{125-h/2:.0f}" for h in hs + [hs[0]])
        bars.append(f'<rect x="{x}" width="8" fill="{RED if i%5==0 else DIM}"><animate attributeName="height" values="{vals}" dur="1.8s" repeatCount="indefinite"/>'
                    f'<animate attributeName="y" values="{ys}" dur="1.8s" repeatCount="indefinite"/></rect>')
    return "".join(bars)


def glyph_pdf():
    out = []
    for i in range(3):
        x, y = 26 + i*22, 72 + i*8
        out.append(f'<g><rect x="{x}" y="{y}" width="64" height="80" fill="{BG}" stroke="{RED if i==2 else DIM}" stroke-width="1.5"/>'
                   + "".join(f'<rect x="{x+10}" y="{y+16+k*12}" width="{44 - (k%2)*14}" height="4" fill="{DIM}"/>' for k in range(4))
                   + f'<animateTransform attributeName="transform" type="translate" values="0 0;{i*10} 0;0 0" dur="3s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".6 0 .4 1;.6 0 .4 1"/></g>')
    out.append(f'<text x="168" y="118" class="m" font-size="14" fill="{GRAY}">MERGE · SPLIT · COMPRESS</text>')
    return "".join(out)


def glyph_gift():
    cx, cy = 70, 112
    return (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" dur="2.4s" repeatCount="indefinite"/>'
            f'<rect x="{cx-36}" y="{cy-18}" width="72" height="50" fill="{BG}" stroke="{DIM}" stroke-width="1.5"/>'
            f'<rect x="{cx-42}" y="{cy-34}" width="84" height="18" fill="{BG}" stroke="{RED}" stroke-width="1.5"/>'
            f'<rect x="{cx-5}" y="{cy-34}" width="10" height="66" fill="{RED}"/>'
            f'<path d="M{cx} {cy-34}C{cx-30} {cy-60} {cx-36} {cy-30} {cx} {cy-34}C{cx+30} {cy-60} {cx+36} {cy-30} {cx} {cy-34}" fill="none" stroke="{RED}" stroke-width="2"/></g>'
            f'<text x="150" y="118" class="m" font-size="14" fill="{GRAY}">NO SIGN-UP · INSTANT LINK</text>')


# ================================================================== STACK
def stack():
    W, H = 1280, 560
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#grid)" opacity=".6"/>']
    cx, cy, sc, dur = 880, 290, 150, 30
    # globe: static latitude ellipses + longitude ellipses whose rx sweeps (cheap 3D rotation)
    R = sc*1.02
    g = [f'<circle cx="{cx}" cy="{cy}" r="{R:.0f}" fill="none" stroke="{DIM}" stroke-width="1.2"/>']
    for lat in [-60, -30, 0, 30, 60]:
        ry = R*math.cos(math.radians(lat)); yy = cy - R*math.sin(math.radians(lat))
        g.append(f'<ellipse cx="{cx}" cy="{yy:.1f}" rx="{ry:.1f}" ry="{ry*.18:.1f}" fill="none" stroke="#262626"/>')
    for k in range(6):
        ph = k*30
        vals = [f"{abs(R*math.cos(math.radians(ph + 360*i/F))):.1f}" for i in range(F)]
        ops = [f"{.25+.75*abs(math.sin(math.radians(ph + 360*i/F))):.2f}" for i in range(F)]
        g.append(f'<ellipse cx="{cx}" cy="{cy}" ry="{R:.0f}" fill="none" stroke="{DIM}">{A("rx", vals, dur)}{A("stroke-opacity", ops, dur)}</ellipse>')
    b.append("".join(g))
    # orbiting labels
    groups = [(["Python", "JavaScript", "C++", "Java", "LangChain", "Node.js"], 1.45, .3, 1, PAPER),
              (["React", "Next.js", "Astro", "Tailwind", "MongoDB", "Supabase", "Docker", "AWS", "Vercel", "Cloudflare"], 1.85, -.22, -1, GRAY)]
    for skills, rad, tilt, spd, col in groups:
        for n, s in enumerate(skills):
            xs, ys, ops, szs = [], [], [], []
            for k in range(F):
                th = spd*2*math.pi*k/F + 2*math.pi*n/len(skills)
                p = rot((rad*math.cos(th), 0, rad*math.sin(th)), tilt, 0, tilt*.4)
                X, Y, Z = proj(p, cx, cy, sc)
                xs.append(f"{X:.1f}"); ys.append(f"{Y:.1f}")
                ops.append(f"{.18+.82*(Z/rad+1)/2:.2f}"); szs.append(f"{13+7*(Z/rad+1)/2:.1f}")
            b.append(f'<g>{A("opacity", ops, dur)}<text class="m" text-anchor="middle" fill="{col}" font-weight="700">'
                     f'{A("x", xs, dur)}{A("y", ys, dur)}{A("font-size", szs, dur)}{esc(s)}</text>'
                     f'<rect width="6" height="6" fill="{RED}">{A("x", [f"{float(v)-3:.1f}" for v in xs], dur)}{A("y", [f"{float(v)+8:.1f}" for v in ys], dur)}</rect></g>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="{RED}"><animate attributeName="r" values="8;12;8" dur="2s" repeatCount="indefinite"/></circle>')
    # left legend
    cats = [("LANG", "Python · JS · C++ · Java"), ("AI", "LangChain · LLM tooling"), ("WEB", "React · Next · Astro"),
            ("DATA", "MongoDB · MySQL · Supabase"), ("SHIP", "Docker · AWS · Vercel · CF")]
    y = 120
    b.append(f'<text x="48" y="80" class="m" font-size="15" fill="{RED}" letter-spacing="3">FIG.02 — STACK ORBIT</text>')
    for i, (k, v) in enumerate(cats):
        b.append(f'<g style="animation:rise .5s {.2+i*.12:.2f}s both"><text x="48" y="{y}" class="d" font-size="34" fill="{PAPER}">{k}</text>'
                 f'<text x="48" y="{y+26}" class="m" font-size="15" fill="{GRAY}">{esc(v)}</text></g>')
        y += 82
    b.append(crops(W, H))
    b.append(scanlines(W, H))
    return svg(W, H, "".join(b), label="Tech stack: Python, JavaScript, C++, Java, LangChain, Node.js, React, Next.js, Astro, Tailwind, MongoDB, Supabase, Docker, AWS, Vercel, Cloudflare")


# ================================================================== BUTTON
def button(label, glyph_svg, delay):
    W, H = 300, 64
    b = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="{PANEL}" stroke="{LINE}"/>'
         f'<rect x="1" y="1" width="64" height="{H-2}" fill="{BG}" stroke="{LINE}"/>{glyph_svg}'
         f'<text x="84" y="40" class="m" font-size="18" font-weight="700" fill="{PAPER}" letter-spacing="3">{label}</text>'
         f'<rect x="1" y="{H-5}" width="0" height="4" fill="{RED}"><animate attributeName="width" from="0" to="{W-2}" begin="{delay}s" dur=".8s" fill="freeze"/></rect>'
         + arrow(W-40, 26, 1, RED, diag=True)]
    return svg(W, H, "".join(b), label=label)


# ================================================================== FOOTER
def footer():
    W, H = 1280, 200
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/><line x1="0" y1="1" x2="{W}" y2="1" stroke="{LINE}"/>']
    b.append(f'<svg y="20" width="{W}" height="70">{ticker(52, W, ["THANKS FOR SCROLLING", "LET\'S BUILD SOMETHING", "SUJOY MOULICK"], 40, color="#2a2a2a", speed=50)}</svg>')
    b.append(f'<line x1="48" y1="110" x2="{W-48}" y2="110" stroke="{LINE}"/>')
    b.append(f'<g class="m" font-size="14" fill="{GRAY}" letter-spacing="2"><text x="48" y="150">© 2026 SUJOY MOULICK</text>'
             f'<text x="{W/2}" y="150" text-anchor="middle">BUILT WITH CODE, NOT TEMPLATES</text>'
             f'<text x="{W-48}" y="150" text-anchor="end" fill="{RED}">EOF_</text></g>')
    b.append(f'<rect x="{W-48+2}" y="137" width="10" height="16" fill="{RED}" class="blink"/>')
    b.append(scanlines(W, H))
    return svg(W, H, "".join(b), label="Footer")


def divider():
    W, H = 1280, 40
    b = [f'<line x1="48" y1="20" x2="{W-48}" y2="20" stroke="{LINE}" stroke-dasharray="2 6"/>'
         f'<rect x="{W/2-5}" y="15" width="10" height="10" fill="{RED}" transform="rotate(45 {W/2} 20)"/>'
         f'<rect x="44" y="16" width="8" height="8" fill="{DIM}"/><rect x="{W-52}" y="16" width="8" height="8" fill="{DIM}"/>']
    return svg(W, H, "".join(b), fonts=False)


save("hero.svg", hero())
save("profile-card.svg", profile())
save("head-about.svg", head("01", "ABOUT", "WHO / WHAT"))
save("head-work.svg", head("02", "WORK", "SHIPPED PRODUCTS"))
save("head-stack.svg", head("03", "STACK", "TOOLS OF THE TRADE"))
save("head-connect.svg", head("04", "CONNECT", "SAY HELLO"))
save("about.svg", about())
save("project-echotodo.svg", project("01", "EchoToDo", "Voice-powered todo extension", "EXTENSION", "docs / chrome", .1, glyph_voice()))
save("project-freepdfly.svg", project("02", "FreePDFly", "Browser-based PDF toolkit", "LIVE SAAS", "freepdfly.com", .3, glyph_pdf()))
save("project-sendvirtualgift.svg", project("03", "SendVirtualGift", "Digital gifts & greetings", "LIVE SAAS", "sendvirtualgift.com", .5, glyph_gift()))
save("stack.svg", stack())
LI = f'<text x="33" y="41" text-anchor="middle" class="d" font-size="24" fill="{RED}">in</text>'
GH = f'<g stroke="{RED}" stroke-width="2.4" fill="none"><path d="M24 24L16 32L24 40M42 24L50 32L42 40"/></g>'
PF = f'<rect x="23" y="22" width="20" height="20" fill="none" stroke="{RED}" stroke-width="2.4"/><rect x="29" y="28" width="8" height="8" fill="{RED}"/>'
save("btn-linkedin.svg", button("LINKEDIN", LI, .1))
save("btn-github.svg", button("GITHUB", GH, .25))
save("btn-portfolio.svg", button("PORTFOLIO", PF, .4))
save("footer.svg", footer())
save("divider.svg", divider())
