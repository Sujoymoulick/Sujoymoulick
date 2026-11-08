"""Builds assets/profile-card.svg: holographic portrait (left) + animated neofetch terminal (right).
Usage: python3 assets/generate_card.py <portrait.png> assets"""
import base64, io, sys, os
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
W, H = 1280, 760
MONO = "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"
SANS = "'Segoe UI','Inter',Helvetica,Arial,sans-serif"

# ---- portrait (embedded, so it works inside an <img>-rendered SVG) ----
LX, LY, LW = 24, 24, 440
PX, PY, PW, PH = LX + 20, 178, LW - 40, H - 178 - 44
im = Image.open(src).convert("RGB")
w, h = im.size
ch = int(w * PH / PW)
im = im.crop((0, h - ch, w, h)).resize((int(PW*1.5), int(PH*1.5)), Image.LANCZOS)
buf = io.BytesIO(); im.save(buf, "JPEG", quality=80)
IMG = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

e = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
p = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Sujoy Moulick — portrait and developer profile">']
p.append(f'''<defs>
  <linearGradient id="frame" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#00f7ff"><animate attributeName="stop-color" values="#00f7ff;#a855f7;#ff3d9a;#00f7ff" dur="6s" repeatCount="indefinite"/></stop>
    <stop offset="1" stop-color="#a855f7"><animate attributeName="stop-color" values="#a855f7;#ff3d9a;#00f7ff;#a855f7" dur="6s" repeatCount="indefinite"/></stop>
  </linearGradient>
  <linearGradient id="title" x1="0" x2="1"><stop offset="0" stop-color="#7cff9b"/><stop offset=".55" stop-color="#e8fff0"/><stop offset="1" stop-color="#00f7ff"/></linearGradient>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".28"/></pattern>
  <linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7cff9b" stop-opacity="0"/><stop offset=".5" stop-color="#7cff9b" stop-opacity=".35"/><stop offset="1" stop-color="#7cff9b" stop-opacity="0"/></linearGradient>
  <linearGradient id="vign" x1="0" y1="0" x2="0" y2="1"><stop offset=".55" stop-color="#0b0f1a" stop-opacity="0"/><stop offset="1" stop-color="#0b0f1a" stop-opacity=".85"/></linearGradient>
  <linearGradient id="fill1" x1="0" x2="1"><stop offset="0" stop-color="#a855f7"/><stop offset="1" stop-color="#ff3d9a"/></linearGradient>
  <linearGradient id="fill2" x1="0" x2="1"><stop offset="0" stop-color="#00f7ff"/><stop offset="1" stop-color="#7cff9b"/></linearGradient>
  <linearGradient id="shine" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="bigglow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
  <clipPath id="pclip"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="10"/></clipPath>
  <clipPath id="g1"><rect x="{PX}" y="0" width="{PW}" height="14"><animate attributeName="y" values="{PY+120};{PY+120};{PY+300};{PY+300};{PY+460}" keyTimes="0;.86;.88;.94;1" dur="5s" repeatCount="indefinite"/></rect></clipPath>
  <clipPath id="g2"><rect x="{PX}" y="0" width="{PW}" height="8"><animate attributeName="y" values="{PY+380};{PY+380};{PY+200};{PY+200};{PY+60}" keyTimes="0;.87;.89;.95;1" dur="5s" repeatCount="indefinite"/></rect></clipPath>
</defs>''')

# ---------------- LEFT PANEL ----------------
p.append(f'<rect x="{LX}" y="{LY}" width="{LW}" height="{H-48}" rx="16" fill="#0b0f1a" stroke="url(#frame)" stroke-width="1.5"/>')
# glitch title (RGB split jitter)
TY = 104
for dx, col, op, vals in [(-3, "#ff3d9a", .7, "0;0;-5;3;0;0"), (3, "#00f7ff", .7, "0;0;5;-3;0;0")]:
    p.append(f'<text x="{LX+LW/2+dx}" y="{TY}" text-anchor="middle" font-family="{SANS}" font-weight="900" font-size="72" letter-spacing="10" fill="{col}" opacity="{op}">SUJOY'
             f'<animateTransform attributeName="transform" type="translate" values="{";".join(v+" 0" for v in vals.split(";"))}" keyTimes="0;.9;.92;.95;.97;1" dur="4s" repeatCount="indefinite"/></text>')
p.append(f'<text x="{LX+LW/2}" y="{TY}" text-anchor="middle" font-family="{SANS}" font-weight="900" font-size="72" letter-spacing="10" fill="url(#title)" filter="url(#glow)">SUJOY</text>')

# role typing (cycled, clipped reveal)
roles = ["Full Stack Engineer", "AI Developer", "Open Source Builder"]
p.append(f'<clipPath id="rc"><rect x="{LX+LW/2-150}" y="{TY+20}" width="0" height="32"><animate attributeName="width" values="0;300;300;0;0" keyTimes="0;.35;.75;.9;1" dur="3.5s" repeatCount="indefinite"/></rect></clipPath>')
n = len(roles); T = 3.5 * n
p.append(f'<g clip-path="url(#rc)" font-family="{MONO}" font-size="20" fill="#00f7ff" text-anchor="middle" filter="url(#glow)">')
for i, r in enumerate(roles):
    a, b = i / n, (i + 1) / n
    kt = sorted(set([0, max(0, a - 1e-4), a, b - 1e-4, b, 1]))
    v = ["1" if a <= k < b else "0" for k in kt]
    p.append(f'<text x="{LX+LW/2}" y="{TY+44}" opacity="0"><animate attributeName="opacity" calcMode="discrete" values="{";".join(v)}" keyTimes="{";".join(f"{k:.4f}" for k in kt)}" dur="{T}s" repeatCount="indefinite"/>{r}</text>')
p.append('</g>')

# portrait with hologram effects
p.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="10" fill="#0f1420"/>')
p.append(f'<g clip-path="url(#pclip)">')
p.append(f'<image href="{IMG}" xlink:href="{IMG}" x="{PX}" y="{PY}" width="{PW}" height="{PH}" preserveAspectRatio="xMidYMax slice"><animate attributeName="opacity" values="1;1;.82;1;1" keyTimes="0;.6;.62;.64;1" dur="3s" repeatCount="indefinite"/></image>')
# glitch slices: displaced + tinted copies
for cid, dx, col in [("g1", 14, "#ff3d9a"), ("g2", -12, "#00f7ff")]:
    p.append(f'<g clip-path="url(#{cid})" opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1;0;1;0" keyTimes="0;.86;.9;.92;.95" dur="5s" repeatCount="indefinite"/>'
             f'<image href="{IMG}" xlink:href="{IMG}" x="{PX+dx}" y="{PY}" width="{PW}" height="{PH}" preserveAspectRatio="xMidYMax slice"/>'
             f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="{col}" opacity=".35"/></g>')
p.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="url(#scan)"/>')
p.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="url(#vign)"/>')
p.append(f'<rect x="{PX}" width="{PW}" height="70" fill="url(#bar)"><animate attributeName="y" values="{PY-70};{PY+PH}" dur="4s" repeatCount="indefinite"/></rect>')
p.append('</g>')
# HUD corners + labels
c, L = "#7cff9b", 22
for (x, y, sx, sy) in [(PX, PY, 1, 1), (PX+PW, PY, -1, 1), (PX, PY+PH, 1, -1), (PX+PW, PY+PH, -1, -1)]:
    p.append(f'<path d="M{x} {y+sy*L} V{y} H{x+sx*L}" fill="none" stroke="{c}" stroke-width="2.5" filter="url(#glow)"/>')
p.append(f'''<g font-family="{MONO}" font-size="12" fill="#7cff9b">
  <circle cx="{PX+20}" cy="{PY+24}" r="4.5" fill="#ff3d9a"><animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/></circle>
  <text x="{PX+32}" y="{PY+28}">LIVE · ID SM-2028</text>
  <text x="{PX+PW-14}" y="{PY+28}" text-anchor="end" opacity=".8">UEM JAIPUR</text>
  <text x="{PX+14}" y="{PY+PH-16}" opacity=".9">&gt; scanning developer<tspan><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>_</tspan></text>
  <text x="{PX+PW-14}" y="{PY+PH-16}" text-anchor="end" opacity=".8">B.TECH CSE · AIML</text>
</g>''')

# ---------------- RIGHT PANEL: terminal ----------------
RX, RY, RW = LX + LW + 24, 24, W - (LX + LW + 24) - 24
RH = H - 48
p.append(f'<rect x="{RX}" y="{RY}" width="{RW}" height="{RH}" rx="16" fill="#0d1117" stroke="#1f2a44" stroke-width="1.5"/>')
p.append(f'<path d="M{RX} {RY+16} a16 16 0 0 1 16 -16 H{RX+RW-16} a16 16 0 0 1 16 16 V{RY+40} H{RX} Z" fill="#161b26"/>')
for i, col in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
    p.append(f'<circle cx="{RX+24+i*20}" cy="{RY+20}" r="6" fill="{col}"/>')
p.append(f'<text x="{RX+RW/2}" y="{RY+25}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#8b9bb4">sujoy@github: ~ — zsh</text>')

KEY, VAL, DIM, HEAD, PINK = "#00f7ff", "#e6edf3", "#3b4a66", "#a855f7", "#ff3d9a"
lines = [("cmd", "neofetch --profile"), ("user",), ("rule",), ("kv", "OS", "macOS"), ("kv", "Host", "github.com/Sujoymoulick"),
         ("kv", "Kernel", "curiosity"), ("kv", "Runtime", "Python / JavaScript / C++"), ("kv", "IDE", "VS Code"), ("gap",),
         ("head", "CAPABILITIES"), ("kv", "Languages", "C / C++ / Java / Python / JavaScript"), ("kv", "AI", "LangChain / AI Automation / LLM Tools"),
         ("kv", "Backend", "Node.js / Express"), ("kv", "Databases", "MongoDB / MySQL / Supabase"), ("kv", "Frontend", "React / Next.js / Tailwind / Astro"),
         ("kv", "Infra", "Docker / AWS / Vercel / Cloudflare"), ("kv", "Tools", "Git / GitHub / Postman / Linux"), ("gap",),
         ("head", "INTERESTS"), ("li", "AI & Automation"), ("li", "Open Source Development"), ("li", "Browser Extensions & Dev Tools"),
         ("li", "Full Stack Web Products"), ("li", "Understanding how things work under the hood"), ("gap",),
         ("bar", "STATUS: BUILDING", .80, "fill1"), ("bar", "LEARNING DAILY", .20, "fill2")]
x0, y, LH, FS = RX + 28, RY + 74, 21, 15
t, step = 0.9, 0.07
p.append(f'<g font-family="{MONO}" font-size="{FS}">')
for ln in lines:
    kind = ln[0]
    rev = f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur=".25s" fill="freeze"/>'
    if kind == "cmd":
        p.append(f'<text x="{x0}" y="{y}" fill="#7cff9b">❯ <tspan fill="{VAL}">{e(ln[1])}</tspan></text>')
        p.append(f'<rect x="{x0+18}" y="{y-16}" width="{len(ln[1])*9.1:.0f}" height="20" fill="#0d1117"><animate attributeName="x" from="{x0+18}" to="{x0+18+len(ln[1])*9.1:.0f}" dur=".7s" begin=".1s" fill="freeze"/></rect>')
        y += LH + 6
    elif kind == "user":
        p.append(f'<text x="{x0}" y="{y}" opacity="0" font-weight="700">{rev}<tspan fill="{KEY}">sujoy</tspan><tspan fill="{VAL}">@</tspan><tspan fill="{KEY}">github</tspan></text>'); y += 10
    elif kind == "rule":
        p.append(f'<rect x="{x0}" y="{y}" width="0" height="2" fill="url(#fill2)"><animate attributeName="width" from="0" to="160" begin="{t:.2f}s" dur=".5s" fill="freeze"/></rect>'); y += LH + 6
    elif kind == "kv":
        k = ln[1]; dots = "." * (16 - len(k))
        p.append(f'<text x="{x0}" y="{y}" opacity="0">{rev}<tspan fill="{KEY}">{e(k)}</tspan> <tspan fill="{DIM}">{dots}</tspan> <tspan x="{x0+190}" fill="{VAL}">{e(ln[2])}</tspan></text>'); y += LH
    elif kind == "head":
        p.append(f'<text x="{x0}" y="{y}" opacity="0" fill="{HEAD}" font-weight="700" letter-spacing="2">{rev}{ln[1]}</text>'); y += LH
    elif kind == "li":
        p.append(f'<text x="{x0}" y="{y}" opacity="0">{rev}<tspan fill="{PINK}">&gt;</tspan> <tspan fill="{VAL}">{e(ln[1])}</tspan></text>'); y += LH
    elif kind == "gap":
        y += LH * .6; continue
    elif kind == "bar":
        label, pct, fid = ln[1], ln[2], ln[3]
        bw = RW - 56 - 70
        p.append(f'<g opacity="0">{rev}<text x="{x0}" y="{y}" fill="{VAL}" font-weight="700">{label}</text>')
        if "BUILDING" in label:
            p.append(f'<circle cx="{x0+len(label)*9.1+12:.0f}" cy="{y-5}" r="4" fill="#7cff9b"><animate attributeName="opacity" values="1;.2;1" dur="1.2s" repeatCount="indefinite"/></circle>')
        by = y + 10
        p.append(f'<rect x="{x0}" y="{by}" width="{bw}" height="14" rx="7" fill="#161b26" stroke="#1f2a44"/>')
        p.append(f'<rect x="{x0}" y="{by}" width="0" height="14" rx="7" fill="url(#{fid})" filter="url(#glow)"><animate attributeName="width" from="0" to="{bw*pct:.0f}" begin="{t+.2:.2f}s" dur="1.6s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>')
        p.append(f'<clipPath id="c{fid}"><rect x="{x0}" y="{by}" width="{bw*pct:.0f}" height="14" rx="7"/></clipPath>')
        p.append(f'<rect clip-path="url(#c{fid})" y="{by}" width="80" height="14" fill="url(#shine)"><animate attributeName="x" values="{x0-80};{x0+bw*pct:.0f}" dur="2.2s" begin="{t+1.8:.2f}s" repeatCount="indefinite"/></rect>')
        p.append(f'<text x="{x0+bw+14}" y="{by+12}" fill="{VAL}" font-weight="700">{int(pct*100)}%</text></g>')
        y += LH + 32
    t += step
# trailing prompt + blinking cursor
p.append(f'<text x="{x0}" y="{y+4}" fill="#7cff9b" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur=".2s" fill="freeze"/>❯ <tspan fill="#00f7ff">█<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>')
p.append('</g></svg>')

svg = "\n".join(p)
open(os.path.join(out, "profile-card.svg"), "w").write(svg)
print(f"profile-card.svg {len(svg)/1024:.0f} KB, terminal content ends at y={y:.0f} of {RY+RH}")
