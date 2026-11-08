"""Generate animated pseudo-3D SVGs for the GitHub profile README.
Real 3D math (rotation + perspective projection) baked into SMIL keyframes,
because GitHub READMEs can't run JavaScript / Three.js."""
import math, random, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"
os.makedirs(OUT, exist_ok=True)
random.seed(7)
F = 90          # keyframes per loop
DUR = 18        # seconds per full rotation
MONO = "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"
SANS = "'Segoe UI','Inter',Helvetica,Arial,sans-serif"


def f(v):
    return f"{v:.1f}"


def rot(p, ax, ay, az):
    x, y, z = p
    c, s = math.cos(ax), math.sin(ax); y, z = y*c - z*s, y*s + z*c
    c, s = math.cos(ay), math.sin(ay); x, z = x*c + z*s, -x*s + z*c
    c, s = math.cos(az), math.sin(az); x, y = x*c - y*s, x*s + y*c
    return x, y, z


def proj(p, cx, cy, scale, cam=4.0):
    x, y, z = p
    k = cam / (cam - z)
    return cx + x*scale*k, cy + y*scale*k, z


def vals(seq):
    return ";".join(seq + [seq[0]])


def anim(attr, seq, dur=DUR):
    return f'<animate attributeName="{attr}" dur="{dur}s" repeatCount="indefinite" values="{vals(seq)}"/>'


# ---------- geometry ----------
def icosahedron():
    t = (1 + 5 ** .5) / 2
    v = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t),
         (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    n = math.sqrt(1 + t*t)
    v = [(a/n, b/n, c/n) for a, b, c in v]
    e = [(i, j) for i in range(12) for j in range(i+1, 12)
         if abs(math.dist(v[i], v[j]) - 2/n) < 1e-6]
    return v, e


def wire_edges(verts, edges, cx, cy, scale, spin, color, width, dur=DUR):
    """Return SVG for a rotating wireframe: one <line> per edge, coords keyed per frame."""
    frames = []
    for k in range(F):
        a = 2*math.pi*k/F
        frames.append([proj(rot(p, *spin(a)), cx, cy, scale) for p in verts])
    out = []
    for i, j in edges:
        x1 = [f(fr[i][0]) for fr in frames]; y1 = [f(fr[i][1]) for fr in frames]
        x2 = [f(fr[j][0]) for fr in frames]; y2 = [f(fr[j][1]) for fr in frames]
        op = [f"{0.25 + 0.75*((fr[i][2]+fr[j][2])/2+1)/2:.2f}" for fr in frames]
        out.append(f'<line stroke="{color}" stroke-width="{width}" stroke-linecap="round">'
                   + anim("x1", x1, dur) + anim("y1", y1, dur) + anim("x2", x2, dur)
                   + anim("y2", y2, dur) + anim("stroke-opacity", op, dur) + '</line>')
    nodes = []
    for i in range(len(verts)):
        cxs = [f(fr[i][0]) for fr in frames]; cys = [f(fr[i][1]) for fr in frames]
        rs = [f"{1.6 + 2.2*(fr[i][2]+1)/2:.2f}" for fr in frames]
        nodes.append('<circle fill="#e8fbff">' + anim("cx", cxs, dur) + anim("cy", cys, dur)
                     + anim("r", rs, dur) + '</circle>')
    return "\n".join(out + nodes)


# =====================================================================
# 1. HERO COVER  1280 x 440
# =====================================================================
def cover():
    W, H, HOR = 1280, 440, 300
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Sujoy Moulick — AI Developer and Full-Stack Engineer">')
    p.append(f'''<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#04050d"/><stop offset=".62" stop-color="#0a0f2e"/><stop offset="1" stop-color="#14062a"/>
  </linearGradient>
  <radialGradient id="glowC" cx=".76" cy=".45" r=".42"><stop offset="0" stop-color="#00f7ff" stop-opacity=".28"/><stop offset="1" stop-color="#00f7ff" stop-opacity="0"/></radialGradient>
  <radialGradient id="glowV" cx=".18" cy=".9" r=".55"><stop offset="0" stop-color="#a855f7" stop-opacity=".30"/><stop offset="1" stop-color="#a855f7" stop-opacity="0"/></radialGradient>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#00f7ff"><animate attributeName="stop-color" values="#00f7ff;#a855f7;#ff3d9a;#00f7ff" dur="8s" repeatCount="indefinite"/></stop>
    <stop offset=".5" stop-color="#ffffff"/>
    <stop offset="1" stop-color="#a855f7"><animate attributeName="stop-color" values="#a855f7;#ff3d9a;#00f7ff;#a855f7" dur="8s" repeatCount="indefinite"/></stop>
  </linearGradient>
  <linearGradient id="gridFade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".35" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff"/></linearGradient>
  <mask id="gm"><rect x="0" y="{HOR}" width="{W}" height="{H-HOR}" fill="url(#gridFade)"/></mask>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="soft"><feGaussianBlur stdDeviation="18"/></filter>
  <clipPath id="roleClip"><rect x="70" y="214" width="0" height="34"><animate attributeName="width" values="0;560;560;0;0" keyTimes="0;.3;.75;.9;1" dur="3.6s" repeatCount="indefinite"/></rect></clipPath>
</defs>''')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#glowC)"/><rect width="{W}" height="{H}" fill="url(#glowV)"/>')

    # stars
    stars = []
    for _ in range(90):
        x, y = random.uniform(0, W), random.uniform(0, HOR - 10)
        r = random.choice([.6, .8, 1, 1.3])
        d = random.uniform(2, 6); b = random.uniform(0, 5)
        stars.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="#cfe9ff"><animate attributeName="opacity" values=".15;1;.15" dur="{d:.1f}s" begin="{b:.1f}s" repeatCount="indefinite"/></circle>')
    p.append("<g>" + "".join(stars) + "</g>")

    # sun / horizon glow
    p.append(f'<ellipse cx="640" cy="{HOR}" rx="520" ry="26" fill="#00f7ff" opacity=".35" filter="url(#soft)"/>')

    # perspective grid floor — horizontal lines scroll toward viewer (real 1/z projection)
    g = []
    VP = 640; FOCAL = 140; CAMH = 1.0; N = 14; DZ = 1.0; FR = 40
    for i in range(N):
        ys = []
        for k in range(FR):
            z = (i + 1 - k / FR) * DZ + 0.15
            ys.append(f(HOR + FOCAL * CAMH / z))
        seq = vals(ys)
        g.append(f'<line x1="0" x2="{W}" stroke="#00f7ff" stroke-width="1.2"><animate attributeName="y1" values="{seq}" dur="1.6s" repeatCount="indefinite"/><animate attributeName="y2" values="{seq}" dur="1.6s" repeatCount="indefinite"/></line>')
    for i in range(-18, 19):
        x_far = VP + i * 6; x_near = VP + i * 120
        g.append(f'<line x1="{x_far}" y1="{HOR}" x2="{x_near}" y2="{H+40}" stroke="#a855f7" stroke-width="1.1"/>')
    p.append(f'<g mask="url(#gm)" opacity=".75">' + "".join(g) + '</g>')
    p.append(f'<line x1="0" y1="{HOR}" x2="{W}" y2="{HOR}" stroke="#00f7ff" stroke-width="1.5" opacity=".9" filter="url(#glow)"/>')

    # 3D icosahedron + inner counter-rotating one
    v, e = icosahedron()
    p.append('<g filter="url(#glow)">')
    p.append(wire_edges(v, e, 985, 175, 118, lambda a: (a*.6 + .4, a, a*.25), "#00f7ff", 1.6))
    p.append(wire_edges(v, e, 985, 175, 52, lambda a: (-a*1.2, -a*2, .3), "#ff3d9a", 1.2))
    p.append('</g>')

    # orbit ring of particles around the shape (tilted 3D circle)
    orb = []
    for n in range(14):
        xs, ys, rs, ops = [], [], [], []
        for k in range(F):
            th = 2*math.pi*(k/F + n/14)
            pt = rot((math.cos(th)*1.55, 0, math.sin(th)*1.55), 0.42, 0, -0.25)
            x, y, z = proj(pt, 985, 175, 118)
            xs.append(f(x)); ys.append(f(y)); rs.append(f"{1.2+2.3*(z+1.55)/3.1:.2f}"); ops.append(f"{.25+.75*(z+1.55)/3.1:.2f}")
        orb.append('<circle fill="#a855f7">' + anim("cx", xs, 9) + anim("cy", ys, 9) + anim("r", rs, 9) + anim("opacity", ops, 9) + '</circle>')
    p.append('<g filter="url(#glow)">' + "".join(orb) + '</g>')

    # left text block
    p.append(f'''<g font-family="{MONO}">
  <text x="72" y="96" fill="#00f7ff" font-size="16" letter-spacing="3" opacity=".9">&gt; hello_world.init()<animate attributeName="opacity" values="0;.9" dur="1s" fill="freeze"/></text>
  <text x="70" y="168" font-family="{SANS}" font-weight="800" font-size="68" letter-spacing="2" fill="url(#name)" filter="url(#glow)">SUJOY MOULICK</text>
  <g clip-path="url(#roleClip)" font-size="22" fill="#e6edf3">
    <text x="72" y="238" opacity="0"><animate attributeName="opacity" values="1;1;0;0;0;0" keyTimes="0;.33;.3334;.99;.999;1" dur="10.8s" repeatCount="indefinite"/>AI Developer · LLM Tools &amp; Automation</text>
    <text x="72" y="238" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.3333;.3334;.6666;.6667;1" dur="10.8s" repeatCount="indefinite"/>Full-Stack Engineer · React / Astro / Node</text>
    <text x="72" y="238" opacity="0"><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;.6666;.6667;1" dur="10.8s" repeatCount="indefinite"/>SaaS Builder · Open Source · Dev Tools</text>
  </g>
  <rect x="72" y="248" width="12" height="3" fill="#00f7ff"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>
</g>''')

    # live-product chips
    chips = [("FreePDFly", "#00f7ff"), ("SendVirtualGift", "#ff3d9a"), ("EchoToDo", "#a855f7")]
    x = 72; cs = []
    for i, (t, c) in enumerate(chips):
        w = 18 + len(t) * 9.2
        cs.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" begin="{.4+i*.25:.2f}s" dur=".6s" fill="freeze"/>'
                  f'<rect x="{f(x)}" y="{H-62}" width="{f(w)}" height="30" rx="15" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-opacity=".7"/>'
                  f'<circle cx="{f(x+13)}" cy="{H-47}" r="3.5" fill="{c}"><animate attributeName="opacity" values="1;.3;1" dur="1.8s" begin="{i*.4:.1f}s" repeatCount="indefinite"/></circle>'
                  f'<text x="{f(x+24)}" y="{H-42}" font-family="{MONO}" font-size="14" fill="#e6edf3">{t}</text></g>')
        x += w + 14
    p.append(f'<text x="72" y="{H-76}" font-family="{MONO}" font-size="12" fill="#8b9bb4" letter-spacing="2">LIVE PRODUCTS</text>')
    p.append("".join(cs))
    p.append(f'<text x="{W-24}" y="{H-18}" text-anchor="end" font-family="{MONO}" font-size="12" fill="#8b9bb4">B.Tech CSE (AIML) · UEM Jaipur</text>')
    p.append('</svg>')
    return "\n".join(p)


# =====================================================================
# 2. TECH GLOBE  — rotating wireframe sphere with orbiting skill labels
# =====================================================================
def globe():
    global F
    F_SAVE, F = F, 60
    W, H, CX, CY, R = 1280, 520, 640, 260, 165
    dur = 24
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Tech stack globe">']
    p.append(f'''<defs>
  <radialGradient id="gbg" cx=".5" cy=".5" r=".6"><stop offset="0" stop-color="#101a44"/><stop offset="1" stop-color="#04050d"/></radialGradient>
  <radialGradient id="core" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#00f7ff" stop-opacity=".35"/><stop offset="1" stop-color="#00f7ff" stop-opacity="0"/></radialGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#gbg)"/>
<circle cx="{CX}" cy="{CY}" r="{R*1.5}" fill="url(#core)"/>
<text x="40" y="54" font-family="{MONO}" font-size="14" fill="#00f7ff" letter-spacing="3">// TECH_UNIVERSE</text>
<text x="{W-40}" y="54" text-anchor="end" font-family="{MONO}" font-size="12" fill="#8b9bb4">rotating · rendered in 3D</text>''')

    tilt = 0.38
    # build latitude/longitude polylines as dotted points (cheaper than paths w/ hidden-line)
    pts = []
    for lat in range(-60, 61, 30):
        for lon in range(0, 360, 12):
            pts.append((lat, lon))
    for lon in range(0, 180, 30):
        for lat in range(-80, 81, 10):
            pts.append((lat, lon)); pts.append((lat, lon + 180))
    pts = list(dict.fromkeys(pts))
    dots = []
    for lat, lon in pts:
        xs, ys, op = [], [], []
        la = math.radians(lat)
        for k in range(F):
            lo = math.radians(lon) + 2*math.pi*k/F
            q = (math.cos(la)*math.sin(lo), -math.sin(la), math.cos(la)*math.cos(lo))
            x, y, z = proj(rot(q, tilt, 0, 0), CX, CY, R)
            xs.append(f(x)); ys.append(f(y)); op.append(f"{.08+.85*max(0,(z+1)/2)**1.6:.2f}")
        dots.append('<circle r="1.7" fill="#00f7ff">' + anim("cx", xs, dur) + anim("cy", ys, dur) + anim("opacity", op, dur) + '</circle>')
    p.append('<g filter="url(#glow)">' + "".join(dots) + '</g>')

    # equator ring
    p.append(f'<ellipse cx="{CX}" cy="{CY}" rx="{R*1.02:.0f}" ry="{R*1.02*math.sin(tilt):.0f}" fill="none" stroke="#a855f7" stroke-opacity=".5"/>')

    # orbiting labels on two tilted rings
    skills_a = ["Python", "JavaScript", "C++", "Java", "LangChain", "LLM Tools", "Node.js", "Express"]
    skills_b = ["React", "Next.js", "Astro", "Tailwind", "MongoDB", "Supabase", "Docker", "AWS", "Vercel", "Cloudflare"]
    colors = ["#00f7ff", "#ff3d9a", "#a855f7", "#7cff9b", "#ffd166"]
    labels = []
    for ring, (skills, rad, tlt, spd) in enumerate([(skills_a, 2.05, 0.25, 1), (skills_b, 2.7, -0.18, -1)]):
        for n, s in enumerate(skills):
            xs, ys, op, fs = [], [], [], []
            for k in range(F):
                th = spd * 2*math.pi*k/F + 2*math.pi*n/len(skills)
                q = rot((math.cos(th)*rad, 0, math.sin(th)*rad), tlt, 0, 0.08 if ring else -0.06)
                x, y, z = proj(q, CX, CY, R*0.95, cam=7)
                d = (z + rad) / (2*rad)
                xs.append(f(x)); ys.append(f(y)); op.append(f"{.25+.75*d:.2f}"); fs.append(f"{11+9*d:.1f}")
            c = colors[(n + ring) % len(colors)]
            labels.append(f'<text text-anchor="middle" font-family="{MONO}" font-weight="600" fill="{c}">'
                          + anim("x", xs, dur) + anim("y", ys, dur) + anim("opacity", op, dur)
                          + anim("font-size", fs, dur) + s + '</text>')
    p.append('<g filter="url(#glow)">' + "".join(labels) + '</g>')
    p.append('</svg>')
    F = F_SAVE
    return "\n".join(p)


# =====================================================================
# 3. Divider + footer wave
# =====================================================================
def divider():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 24" width="1280" height="24">
<defs><linearGradient id="d" x1="0" x2="1"><stop offset="0" stop-color="#00f7ff" stop-opacity="0"/><stop offset=".5" stop-color="#a855f7"/><stop offset="1" stop-color="#00f7ff" stop-opacity="0"/></linearGradient>
<radialGradient id="pulse"><stop offset="0" stop-color="#fff"/><stop offset=".4" stop-color="#00f7ff"/><stop offset="1" stop-color="#00f7ff" stop-opacity="0"/></radialGradient></defs>
<rect x="0" y="11" width="1280" height="2" fill="url(#d)"/>
<ellipse cy="12" rx="60" ry="5" fill="url(#pulse)"><animate attributeName="cx" values="-60;1340" dur="3.5s" repeatCount="indefinite"/></ellipse>
</svg>'''


def footer():
    W, H = 1280, 160
    def wave(amp, ph, y0, n=5):
        pts = []
        for k in range(F//3):
            t = 2*math.pi*k/(F//3)
            d = f"M0 {H}"
            for x in range(0, W+1, 40):
                y = y0 + amp*math.sin(x/W*2*math.pi*n/2 + t + ph)
                d += f" L{x} {f(y)}"
            d += f" L{W} {H} Z"
            pts.append(d)
        return pts
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           '<defs><linearGradient id="fw" x1="0" x2="1"><stop offset="0" stop-color="#00f7ff"/><stop offset=".5" stop-color="#a855f7"/><stop offset="1" stop-color="#ff3d9a"/></linearGradient></defs>']
    for amp, ph, y0, op, dur in [(14, 0, 70, .25, 7), (18, 2, 90, .35, 5), (12, 4, 112, .9, 4)]:
        out.append(f'<path fill="url(#fw)" opacity="{op}">' + anim("d", wave(amp, ph, y0), dur) + '</path>')
    out.append(f'<text x="640" y="146" text-anchor="middle" font-family="{MONO}" font-size="14" fill="#04050d" font-weight="700" letter-spacing="3">THANKS FOR VISITING · KEEP BUILDING</text>')
    out.append('</svg>')
    return "\n".join(out)


for name, fn in [("cover.svg", cover), ("tech-globe.svg", globe), ("divider.svg", divider), ("footer.svg", footer)]:
    s = fn()
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(s)
    print(f"{name}: {len(s)/1024:.0f} KB")
