#!/usr/bin/env python3
"""Genera los fondos del tema Claude (oscuro y claro) y los sprites de la capa animada.

Uso: tools/build.sh (llama a este script y convierte los SVG con rsvg-convert)
Escribe SVG; luego conviértelos con rsvg-convert (ver build.sh).
"""
import math, random, sys

W, H = 3840, 2400  # 16:10, como la pantalla del Yoga

TERRA, TERRA_DEEP, TERRA_LIGHT = "#D97757", "#B65A3B", "#E8956F"
CREAM, CREAM_DEEP = "#FAF9F5", "#E8E4D8"
INK, INK_DEEP = "#262624", "#171615"


def starburst(cx, cy, r, color, opacity=1.0, seed=7, rays=12, width=0.13, rot=0):
    """Asterisco de rayos redondeados con longitudes desiguales, al estilo del logo de Claude."""
    rnd = random.Random(seed)
    lens = [1.00, 0.72, 0.88, 0.62, 0.95, 0.70, 1.00, 0.66, 0.90, 0.74, 0.84, 0.68]
    w = r * width
    out = []
    for i in range(rays):
        l = lens[i % len(lens)] * rnd.uniform(0.92, 1.05)
        a = math.radians(i * (360 / rays) + 15 + rot + rnd.uniform(-4, 4))
        x2 = cx + math.cos(a) * r * l
        y2 = cy + math.sin(a) * r * l
        out.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-opacity="{opacity:.3f}" stroke-width="{w:.1f}" stroke-linecap="round"/>'
        )
    return "\n".join(out)


_glow_n = [0]
def glow(cx, cy, rx, ry, color, opacity, blur=None):
    """Halo suave con degradado radial (sin filtro: evita bandas en zonas oscuras)."""
    _glow_n[0] += 1
    gid = f"glow{_glow_n[0]}"
    return (
        f'<radialGradient id="{gid}"><stop offset="0" stop-color="{color}" stop-opacity="{opacity:.3f}"/>'
        f'<stop offset="0.5" stop-color="{color}" stop-opacity="{opacity*0.35:.3f}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
        f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx*1.25:.0f}" ry="{ry*1.25:.0f}" fill="url(#{gid})"/>'
    )


def rings(cx, cy, r0, step, n, color, opacity, width=3):
    return "\n".join(
        f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r0 + i * step:.0f}" fill="none" stroke="{color}" '
        f'stroke-opacity="{opacity * (1 - i / (n + 1)):.3f}" stroke-width="{width}"/>'
        for i in range(n)
    )


def streaks(seed, color, opacity, n=5):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x = rnd.uniform(-W * 0.2, W * 1.1)
        y = rnd.uniform(-H * 0.2, H * 0.9)
        L = rnd.uniform(W * 0.5, W * 1.2)
        t = rnd.uniform(40, 140)
        out.append(
            f'<rect x="{x:.0f}" y="{y:.0f}" width="{L:.0f}" height="{t:.0f}" rx="{t/2:.0f}" fill="{color}" '
            f'fill-opacity="{opacity * rnd.uniform(0.5, 1.0):.3f}" transform="rotate(-28 {x:.0f} {y:.0f})" filter="url(#blur80)"/>'
        )
    return "\n".join(out)


def field(seed, n, colors, rmin, rmax, omin, omax, avoid=None):
    """Campo de asteriscos pequeños repartidos por la pantalla."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        for _ in range(30):
            x, y = rnd.uniform(0, W), rnd.uniform(0, H)
            if avoid is None or math.hypot(x - avoid[0], y - avoid[1]) > avoid[2]:
                break
        r = rnd.uniform(rmin, rmax)
        c = rnd.choice(colors)
        o = rnd.uniform(omin, omax)
        out.append(starburst(x, y, r, c, o, seed=seed * 100 + i, rot=rnd.uniform(0, 30), width=0.15))
    return "\n".join(out)



# Clawd, la mascota pixelada de Claude Code (10x7 celdas). X=cuerpo, o=ojo, .=nada
CLAWD_ROWS = [
    "..XXXXXX..",
    ".XXXXXXXX.",
    "XXoXXXXoXX",
    "XXXXXXXXXX",
    "XXXXXXXXXX",
    ".XXXXXXXX.",
    ".X.X..X.X.",
]
CLAWD_FEET = {"a": ".X.X..X.X.", "b": "..X.X.X.X.", "c": ".X.X.X.X..", "none": ".........."}


def clawd(x, y, px, body, eye="#141413", look=0, blink=False, feet="a", opacity=1.0, shadow=None):
    """Clawd con celdas de px píxeles, esquina superior izquierda en (x,y).
    look: -1 ojos a la izquierda, 0 al frente, 1 a la derecha. shadow: color de sombra o None."""
    rows = list(CLAWD_ROWS)
    rows[6] = CLAWD_FEET[feet]
    out = [f'<g opacity="{opacity:.3f}">']
    if shadow:
        out.append(f'<ellipse cx="{x + 5*px:.0f}" cy="{y + 7.2*px:.0f}" rx="{5.6*px:.0f}" ry="{0.9*px:.0f}" fill="{shadow}" fill-opacity="0.45" filter="url(#blur30)"/>')
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            out.append(f'<rect x="{x + c*px:.1f}" y="{y + r*px:.1f}" width="{px+0.6:.1f}" height="{px+0.6:.1f}" fill="{body}"/>')
    # ojos encima del cuerpo
    for c in (2, 7):
        ex = x + (c + look) * px
        ey = y + 2 * px
        if blink:
            out.append(f'<rect x="{ex:.1f}" y="{ey + px*0.55:.1f}" width="{px:.1f}" height="{px*0.3:.1f}" fill="{eye}"/>')
        else:
            out.append(f'<rect x="{ex:.1f}" y="{ey:.1f}" width="{px:.1f}" height="{px:.1f}" fill="{eye}"/>')
    out.append("</g>")
    return "\n".join(out)


def clawd_frame(path, body, eye, look=0, blink=False, feet="a"):
    """Sprite transparente de 100x70 para la capa animada (se escala sin suavizado)."""
    write(path, f'''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="70" viewBox="0 0 100 70" shape-rendering="crispEdges">
{clawd(0, 0, 10, body, eye, look, blink, feet)}</svg>''')

DEFS = f'''<defs>
  <filter id="blur80" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="80"/></filter>
  <filter id="blur160" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="160"/></filter>
  <filter id="blur320" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="320"/></filter>
  <filter id="blur30" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" result="n"/>
    <feColorMatrix in="n" type="saturate" values="0"/>
  </filter>
</defs>'''

GRAIN = f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.09" style="mix-blend-mode:soft-light"/>'


def svg(body, gradient):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{DEFS}
{gradient}
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{body}
{GRAIN}
</svg>'''


def write(path, content):
    open(path, "w").write(content)
    print("->", path)


out = sys.argv[1]

# 1) EMBER — brillo terracota, aro de luz y Clawd grande mirando al asterisco.
hx, hy = W * 0.68, H * 0.50
body = "\n".join([
    streaks(3, TERRA, 0.10),
    glow(hx, hy, 1500, 1200, TERRA_DEEP, 0.55),
    glow(hx, hy, 800, 700, TERRA, 0.45),
    glow(W * 0.12, H * 0.15, 900, 700, "#3A2E28", 0.8),
    rings(hx, hy, 640, 190, 6, TERRA_LIGHT, 0.22, 4),
    starburst(hx, hy, 560, INK_DEEP, 0.55, seed=7, width=0.16),
    starburst(hx - 14, hy - 14, 560, TERRA, 1.0, seed=7, width=0.15),
    starburst(hx - 14, hy - 14, 560, CREAM, 0.16, seed=7, width=0.05),
    clawd(W * 0.16, H * 0.66, 46, TERRA, look=1, shadow="#0E0D0C"),          # el grande, mirando a la derecha
    clawd(W * 0.31, H * 0.79, 22, TERRA_LIGHT, look=1, feet="b", shadow="#0E0D0C"),   # el pequeño
])
write(f"{out}/01-claude-ember.svg", svg(body, f'''<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#1B1A19"/><stop offset="0.55" stop-color="{INK}"/><stop offset="1" stop-color="#2C2724"/></linearGradient>'''))

# 2) PARADE — desfile de Clawds por el borde inferior bajo una nebulosa cálida.
hx, hy = W * 0.26, H * 0.36
parade = []
rnd = random.Random(5)
xcur = W * 0.06
for i, (px, col, look, feet) in enumerate([
    (30, TERRA, 1, "a"), (18, TERRA_LIGHT, 1, "b"), (40, TERRA, 1, "c"), (14, CREAM, 1, "a"),
    (24, TERRA, 1, "b"), (34, TERRA_LIGHT, -1, "a"), (20, TERRA, 1, "c"), (12, CREAM, 1, "b"), (28, TERRA, 1, "a"),
]):
    parade.append(clawd(xcur, H * 0.86 - 7 * px, px, col, look=look, feet=feet, blink=(i == 5), shadow="#0E0D0C"))
    xcur += 10 * px + rnd.uniform(90, 260)
body = "\n".join([
    glow(W * 0.28, H * 0.40, 1400, 1000, "#4A2E25", 0.9),
    glow(W * 0.85, H * 0.85, 1100, 900, "#2E2A26", 1.0),
    glow(hx, hy, 500, 450, TERRA, 0.35),
    starburst(W * 0.82, H * 0.30, 700, TERRA, 0.10, seed=9, width=0.12),
    rings(hx, hy, 420, 120, 3, CREAM, 0.14, 3),
    starburst(hx, hy, 340, TERRA, 1.0, seed=7, width=0.15),
    starburst(hx, hy, 340, CREAM, 0.2, seed=7, width=0.05),
    f'<rect x="0" y="{H*0.86:.0f}" width="{W}" height="{H*0.14:.0f}" fill="{INK_DEEP}" fill-opacity="0.55"/>',
    f'<rect x="0" y="{H*0.86-4:.0f}" width="{W}" height="4" fill="{TERRA}" fill-opacity="0.35"/>',
    *parade,
])
write(f"{out}/02-claude-parade.svg", svg(body, f'''<radialGradient id="bg" cx="0.3" cy="0.4" r="0.9">
  <stop offset="0" stop-color="#2A2523"/><stop offset="1" stop-color="{INK_DEEP}"/></radialGradient>'''))

# 3) TERRACOTTA BLOOM — todo terracota, asterisco crema y un Clawd crema gigante asomando por la esquina.
hx, hy = W * 0.80, H * 0.40
body = "\n".join([
    streaks(5, CREAM, 0.12),
    glow(W * 0.15, H * 0.10, 1400, 1000, TERRA_LIGHT, 0.7),
    glow(hx, hy, 1300, 1100, "#8E3F26", 0.55),
    rings(hx, hy, 900, 220, 5, CREAM, 0.18, 5),
    starburst(hx + 30, hy + 30, 860, "#7A3620", 0.35, seed=7, width=0.14),
    starburst(hx, hy, 860, CREAM, 1.0, seed=7, width=0.14),
    clawd(-3.2 * 110, H - 8.6 * 110, 110, CREAM, eye="#7A3620", look=1, shadow="#7A3620"),   # gigante, asomando por la izquierda
])
write(f"{out}/03-claude-terracotta-bloom.svg", svg(body, f'''<radialGradient id="bg" cx="0.35" cy="0.3" r="1.0">
  <stop offset="0" stop-color="{TERRA}"/><stop offset="0.7" stop-color="#C96442"/><stop offset="1" stop-color="{TERRA_DEEP}"/></radialGradient>'''))

# 4) CREAM BLOOM — claro, para Claude Light.
hx, hy = W * 0.70, H * 0.48
body = "\n".join([
    streaks(8, TERRA, 0.10),
    glow(hx, hy, 1500, 1200, "#F1C9B5", 0.9),
    glow(W * 0.10, H * 0.12, 1000, 800, "#E9E4D3", 1.0),
    rings(hx, hy, 640, 190, 6, TERRA, 0.16, 4),
    starburst(hx + 16, hy + 16, 560, "#B8A79A", 0.45, seed=7, width=0.15),
    starburst(hx, hy, 560, TERRA, 1.0, seed=7, width=0.15),
    starburst(hx, hy, 560, CREAM, 0.22, seed=7, width=0.05),
    clawd(W * 0.16, H * 0.66, 46, "#C96442", look=1, shadow="#B8A79A"),
    clawd(W * 0.31, H * 0.79, 22, TERRA, look=1, feet="b", shadow="#B8A79A"),
])
write(f"{out}/04-claude-cream-bloom.svg", svg(body, f'''<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{CREAM}"/><stop offset="0.6" stop-color="#F3F1E9"/><stop offset="1" stop-color="{CREAM_DEEP}"/></linearGradient>'''))

# --- sprites para la capa animada (fondo transparente) ---
S = 1024
write(f"{out}/sprite-glow-terra.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">
<defs><radialGradient id="g"><stop offset="0" stop-color="{TERRA}" stop-opacity="0.9"/><stop offset="0.45" stop-color="{TERRA}" stop-opacity="0.35"/><stop offset="1" stop-color="{TERRA}" stop-opacity="0"/></radialGradient></defs>
<circle cx="{S/2}" cy="{S/2}" r="{S/2}" fill="url(#g)"/></svg>''')
write(f"{out}/sprite-glow-cream.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">
<defs><radialGradient id="g"><stop offset="0" stop-color="{CREAM}" stop-opacity="0.8"/><stop offset="0.4" stop-color="{CREAM}" stop-opacity="0.25"/><stop offset="1" stop-color="{CREAM}" stop-opacity="0"/></radialGradient></defs>
<circle cx="{S/2}" cy="{S/2}" r="{S/2}" fill="url(#g)"/></svg>''')
T = 1400
write(f"{out}/sprite-star-terra.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{T}" height="{T}" viewBox="0 0 {T} {T}">
{starburst(T/2, T/2, T*0.46, TERRA, 1.0, seed=7, width=0.15)}</svg>''')
write(f"{out}/sprite-star-cream.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{T}" height="{T}" viewBox="0 0 {T} {T}">
{starburst(T/2, T/2, T*0.46, CREAM, 1.0, seed=7, width=0.15)}</svg>''')
for name, body_c, eye_c in (("terra", TERRA, "#141413"), ("cream", CREAM, "#7A3620")):
    clawd_frame(f"{out}/clawd-{name}-idle.svg", body_c, eye_c)
    clawd_frame(f"{out}/clawd-{name}-blink.svg", body_c, eye_c, blink=True)
    clawd_frame(f"{out}/clawd-{name}-left.svg", body_c, eye_c, look=-1)
    clawd_frame(f"{out}/clawd-{name}-right.svg", body_c, eye_c, look=1)
    clawd_frame(f"{out}/clawd-{name}-walk1.svg", body_c, eye_c, look=1, feet="b")
    clawd_frame(f"{out}/clawd-{name}-walk2.svg", body_c, eye_c, look=1, feet="c")
write(f"{out}/sprite-spark.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
{starburst(128, 128, 110, CREAM, 1.0, seed=3, width=0.16)}</svg>''')

# unlock: asterisco + palabra, transparente
def unlock(path, color):
    write(path, f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="188" viewBox="0 0 800 188">
{starburst(250, 94, 60, color)}
<text x="330" y="118" font-family="JetBrainsMono Nerd Font, Inter, Noto Sans, sans-serif" font-size="78" font-weight="500" fill="{color}" letter-spacing="1">Claude</text>
</svg>''')
unlock(f"{out}/unlock-dark.svg", TERRA)
unlock(f"{out}/unlock-light.svg", "#C96442")
