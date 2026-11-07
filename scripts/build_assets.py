"""Genera il banner animato del profilo nello stile "Cantiere" di buildwithbelletz.

Stesso design system del sito: carta, inchiostro e giallo cantiere, quote e
segni del disegno tecnico. Vengono prodotte due versioni, scelte dal README in
base al tema di GitHub:

    assets/banner-light.svg   tema "Carta"
    assets/banner-dark.svg    tema "Inchiostro"

Insieme al banner escono i piccoli segni del kit usati nel README:

    assets/logo-light.svg     marchio ufficiale V3.1 su carta (cartiglio)
    assets/logo-dark.svg      marchio ufficiale V3.1 su inchiostro
    assets/beacon.svg         beacon quadrato giallo (stato dei progetti)
    assets/icons/*.svg        icone duotone del kit (scripts/icons/), una per tema

I font del brand (Bricolage Grotesque, JetBrains Mono, licenza OFL, sorgenti in
scripts/fonts/) vengono istanziati, ridotti ai soli glifi usati e incorporati
nell'SVG in base64: il banner appare identico ovunque, senza richieste esterne.
Ogni glifo è posizionato con coordinate x calcolate dalle metriche del font,
così l'animazione macchina da scrivere avanza esattamente di un carattere.

Il resto del README è markdown nativo, leggibile anche da mobile.

Requisiti: pip install fonttools brotli
Uso:       python scripts/build_assets.py
"""
from __future__ import annotations

import base64
import io
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
FONTS = Path(__file__).resolve().parent / "fonts"

W, H = 1200, 440
PAD = 56

THEMES = {
    "light": dict(bg="#f2eee5", surface="#faf8f3", ink="#17150f", subtle="#6b655a", line="#d6cebd",
                  grid="#17150f", grid_op=(0.05, 0.085), accent="#ffc400", accent_ink="#8a6200",
                  word_fill="#17150f", word_band=True),
    "dark": dict(bg="#14130f", surface="#1c1a16", ink="#f2ede3", subtle="#8f887b", line="#2f2c26",
                 grid="#f2ede3", grid_op=(0.035, 0.065), accent="#ffc933", accent_ink="#ffd45c",
                 word_fill="#ffc933", word_band=False),
}

PHRASES = ["Build.", "Build projects.", "Build experiments.", "Build results.", "Build with Belletz."]
NAME = "Belletz"
ICONS = Path(__file__).resolve().parent / "icons"
MARK_W, MARK_H = 265, 246  # official mark master, Identity Kit V3.1
SPECS = [
    ("ROLE", "Full Stack & AI Engineer"),
    ("FOCUS", "AI · Full stack · B2B"),
    ("BASE", "Italy"),
    ("STATUS", "Open to projects"),
]


# --------------------------------------------------------------------------- fonts
class Face:
    """Static instance of a variable font: metrics for layout, subset for embedding."""

    def __init__(self, family: str, src: str, axes: dict[str, float]):
        self.family = family
        self.font = instantiateVariableFont(TTFont(FONTS / src), axes)
        self.upm = self.font["head"].unitsPerEm
        self.cmap = self.font.getBestCmap()
        self.hmtx = self.font["hmtx"]
        self.used: set[str] = set()

    def advance(self, ch: str, size: float) -> float:
        self.used.add(ch)
        glyph = self.cmap.get(ord(ch)) or self.cmap[ord("?")]
        return self.hmtx[glyph][0] * size / self.upm

    def css(self) -> str:
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = []  # no kerning or ligatures: glyph positions are explicit
        opts.name_IDs = []
        opts.notdef_outline = True
        font = TTFont(io.BytesIO(_dump(self.font)))
        sub = subset.Subsetter(opts)
        sub.populate(text="".join(sorted(self.used)) + " ")
        sub.subset(font)
        data = base64.b64encode(_dump(font, "woff2")).decode()
        return f"@font-face{{font-family:'{self.family}';src:url(data:font/woff2;base64,{data}) format('woff2')}}"


def _dump(font: TTFont, flavor: str | None = None) -> bytes:
    buf = io.BytesIO()
    font.flavor = flavor
    font.save(buf)
    return buf.getvalue()


DISPLAY = Face("BwB Display", "BricolageGrotesque-latin-opsz-wght.woff2", {"wght": 800, "opsz": 96})
DISPLAY_SM = Face("BwB Display Small", "BricolageGrotesque-latin-opsz-wght.woff2", {"wght": 700, "opsz": 24})
MONO = Face("BwB Mono", "JetBrainsMono-latin-wght.woff2", {"wght": 500})


def layout(face: Face, s: str, x: float, size: float, tracking: float) -> tuple[list[float], list[float]]:
    """Start and end x of every glyph, with tracking in em."""
    starts, ends, cur = [], [], x
    for ch in s:
        adv = face.advance(ch, size)
        starts.append(cur)
        ends.append(cur + adv)
        cur += adv + tracking * size
    return starts, ends


def text(face: Face, x: float, y: float, s: str, size: float, fill: str, tracking=0.0) -> tuple[str, float]:
    starts, ends = layout(face, s, x, size, tracking)
    xattr = " ".join(f"{p:.2f}" for p in starts)
    svg = (f'<text x="{xattr}" y="{y}" font-family="{face.family}" font-size="{size}" fill="{fill}">'
           f"{escape(s)}</text>")
    return svg, ends[-1] - x


# --------------------------------------------------------------------------- mark
def mark_paths(t: dict) -> str:
    """Official Identity Kit V3.1 geometry, on its 265x246 master. Never redraw it."""
    return (f'<path fill="{t["accent"]}" d="M110 125 H191 C225 125 250 148 250 178 C250 210 226 231 190 231 '
            'H54 L76 199 H190 C208 199 222 190 222 177 C222 164 211 156 190 156 H89 Z"/>'
            f'<rect x="12" y="174" width="28" height="28" fill="{t["accent"]}"/>'
            f'<rect x="48" y="143" width="28" height="28" fill="{t["accent"]}"/>'
            f'<path fill="{t["ink"]}" d="M18 110 L80 13 H102 L40 110 Z M62 110 L124 13 H146 L84 110 Z"/>'
            f'<path fill="{t["ink"]}" d="M166 13 H191 C227 13 249 36 249 69 C249 99 228 120 195 120 H103 '
            'L124 87 H192 C210 87 221 81 221 69 C221 53 211 46 192 46 H146 Z"/>')


# --------------------------------------------------------------------------- banner
def banner(theme: str) -> str:
    t = THEMES[theme]
    parts: list[str] = []
    css: list[str] = []

    # Brand lockup: the official mark + "BUILD WITH / Belletz"
    # 18px between mark and name is the kit's clear space (0.25 x mark width).
    scale = 66 / MARK_H
    parts.append(f'<g transform="translate({PAD} 40) scale({scale:.4f})">{mark_paths(t)}</g>')
    name_x = PAD + round(MARK_W * scale) + 18
    parts.append(text(MONO, name_x, 70, "BUILD WITH", 12, t["subtle"], 0.14)[0])
    parts.append(text(DISPLAY_SM, name_x, 96, "Belletz", 26, t["ink"], -0.03)[0])

    # Status chip, right aligned, with a blinking square beacon
    label = "AVAILABLE FOR PROJECTS"
    lw = text(MONO, 0, 0, label, 12, "", 0.14)[1]
    cw = lw + 50
    cx = W - PAD - cw
    parts.append(f'<rect x="{cx:.1f}" y="58.5" width="{cw:.1f}" height="34" fill="{t["surface"]}" stroke="{t["line"]}"/>')
    parts.append(f'<rect class="beacon" x="{cx + 16:.1f}" y="71" width="9" height="9" fill="{t["accent"]}"/>')
    parts.append(text(MONO, cx + 34, 80, label, 12, t["ink"], 0.14)[0])

    # Dimension line with end ticks and a centred label
    dy, mid = 150, W / 2
    dlw = text(MONO, 0, 0, "SCALE 1:1", 11, "", 0.14)[1]
    parts.append(text(MONO, mid - dlw / 2, dy + 4, "SCALE 1:1", 11, t["subtle"], 0.14)[0])
    for x1, x2 in ((PAD, mid - dlw / 2 - 14), (mid + dlw / 2 + 14, W - PAD)):
        parts.append(f'<path d="M{x1:.1f} {dy}.5H{x2:.1f}" stroke="{t["subtle"]}" stroke-opacity="0.7"/>')
    parts.append(f'<path d="M{PAD + 0.5} {dy - 5}V{dy + 6}M{W - PAD - 0.5} {dy - 5}V{dy + 6}" stroke="{t["subtle"]}"/>')

    # Typewriter title: one group per phrase, revealed glyph by glyph
    size, ty, track = 120, 270, -0.028
    type_s, del_s, hold_s, gap_s, tail_s = 0.065, 0.032, 1.1, 0.24, 7.0
    timeline, t0 = [], 0.5
    for i, p in enumerate(PHRASES):
        a = t0
        b = a + len(p) * type_s
        c = b + (tail_s if i == len(PHRASES) - 1 else hold_s)
        d = c + len(p) * del_s
        timeline.append((a, c))
        t0 = d + gap_s
    total = t0
    pct = lambda s: f"{100 * s / total:.3f}%"

    cursor: list[tuple[float, float]] = []
    final_end = 0.0
    for i, (p, (a, c)) in enumerate(zip(PHRASES, timeline)):
        starts, ends = layout(DISPLAY, p, PAD, size, track)
        edge = lambda k: ends[k - 1] if k else PAD  # right edge after k glyphs
        steps = [(a + k * type_s, k) for k in range(len(p) + 1)]
        steps += [(c + (len(p) - k) * del_s, k) for k in range(len(p), -1, -1)]
        frames = "".join(f"{pct(s)}{{clip-path:inset(0 {W - edge(k):.1f}px 0 0)}}" for s, k in steps)
        css.append(f"@keyframes p{i}{{0%{{clip-path:inset(0 {W}px 0 0)}}{frames}}}"
                   f".p{i}{{clip-path:inset(0 {W}px 0 0);animation:p{i} {total:.2f}s step-end infinite}}")
        cursor += [(s, edge(k) - PAD) for s, k in steps]

        # Full-canvas transparent rect: makes the group's box the whole banner,
        # so the clip-path insets above are absolute pixel positions.
        inner, word = [f'<rect width="{W}" height="{H}" fill="transparent"/>'], range(-1, -1)
        if i == len(PHRASES) - 1:
            final_end = ends[-1] - PAD
            n0 = p.index(NAME)
            word = range(n0, n0 + len(NAME))
            if t["word_band"]:  # highlighter band behind the name, on paper only
                bx0, bx1 = starts[n0] - 4, ends[n0 + len(NAME) - 1] + 4
                inner.append(f'<rect x="{bx0:.1f}" y="{ty - size * 0.36:.1f}" width="{bx1 - bx0:.1f}" '
                             f'height="{size * 0.36:.1f}" fill="{t["accent"]}"/>')
        spans = "".join(
            f'<tspan x="{starts[k]:.2f}"{f" fill=\"{t["word_fill"]}\"" if k in word else ""}>{escape(ch)}</tspan>'
            for k, ch in enumerate(p))
        inner.append(f'<text y="{ty}" font-family="{DISPLAY.family}" font-size="{size}" fill="{t["ink"]}">{spans}</text>')
        parts.append(f'<g class="p{i}">{"".join(inner)}</g>')

    cursor.sort()
    frames = "".join(f"{pct(s)}{{transform:translateX({x:.1f}px)}}" for s, x in cursor)
    css.append(f"@keyframes cur{{0%{{transform:translateX(0)}}{frames}}}"
               f".cur{{animation:cur {total:.2f}s step-end infinite}}")
    css.append("@keyframes blink{0%,50%{opacity:1}51%,100%{opacity:0}}.blink{animation:blink 1s steps(1) infinite}")
    css.append("@keyframes beacon{0%,60%{opacity:1}61%,100%{opacity:.25}}.beacon{animation:beacon 1.6s steps(1) infinite}")
    css.append("@media (prefers-reduced-motion: reduce){"
               + "".join(f".p{i}{{display:none}}" for i in range(len(PHRASES) - 1))
               + f".p{len(PHRASES) - 1}{{animation:none;clip-path:none}}"
               + f".cur{{animation:none;transform:translateX({final_end:.1f}px)}}.blink,.beacon{{animation:none}}}}")
    parts.append(f'<g class="cur"><rect class="blink" x="{PAD + 6}" y="{ty - size * 0.74:.1f}" '
                 f'width="{size * 0.09:.1f}" height="{size * 0.78:.1f}" fill="{t["accent"]}"/></g>')

    # Spec strip: the drawing's title block
    sy, sb = 316, H - 32
    parts.append(f'<path d="M{PAD} {sy}H{W - PAD}" stroke="{t["ink"]}" stroke-width="2"/>')
    parts.append(f'<path d="M{PAD} {sb}.5H{W - PAD}" stroke="{t["line"]}"/>')
    col = (W - 2 * PAD) / len(SPECS)
    for i, (k, v) in enumerate(SPECS):
        x = PAD + i * col + (18 if i else 0)
        if i:
            parts.append(f'<path d="M{PAD + i * col:.1f} {sy + 1}V{sb}" stroke="{t["line"]}"/>')
        parts.append(text(MONO, x, sy + 34, k, 11, t["subtle"], 0.14)[0])
        parts.append(text(DISPLAY_SM, x, sy + 70, v, 22, t["accent_ink"] if k == "STATUS" else t["ink"], -0.01)[0])

    # Background: engineering paper, faded towards the edges
    g1, g2 = t["grid_op"]
    defs = (f'<pattern id="minor" width="16" height="16" patternUnits="userSpaceOnUse">'
            f'<path d="M16 0H0V16" fill="none" stroke="{t["grid"]}" stroke-opacity="{g1}"/></pattern>'
            f'<pattern id="major" width="80" height="80" patternUnits="userSpaceOnUse">'
            f'<path d="M80 0H0V80" fill="none" stroke="{t["grid"]}" stroke-opacity="{g2}"/></pattern>'
            f'<radialGradient id="fade" cx="0.72" cy="0.35" r="0.75">'
            f'<stop offset="0.25" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>')

    fonts = DISPLAY.css() + DISPLAY_SM.css() + MONO.css()
    label = "Build with Belletz. Full Stack & Forward Deployed AI Engineer."
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{escape(label)}">\n<title>{escape(label)}</title>\n'
            f"<defs>{defs}</defs>\n<style>{fonts}text{{font-kerning:none}}{''.join(css)}</style>\n"
            f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>\n'
            f'<g mask="url(#m)"><rect width="{W}" height="{H}" fill="url(#minor)"/>'
            f'<rect width="{W}" height="{H}" fill="url(#major)"/></g>\n'
            + "\n".join(parts) + "\n</svg>\n")


# --------------------------------------------------------------------------- kit marks
def logo(theme: str) -> str:
    """The official mark on its own, same drawing as the kit's logos/svg/mark-*.svg."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{MARK_W}" height="{MARK_H}" '
            f'viewBox="0 0 {MARK_W} {MARK_H}" role="img" aria-label="Build with Belletz">'
            f'<title>Build with Belletz</title>{mark_paths(THEMES[theme])}</svg>\n')


def icon(src: str, theme: str) -> str:
    """A kit icon (drawn for paper) with the ink and yellow of the given theme."""
    t = THEMES[theme]
    return src.replace("#17150F", t["ink"]).replace("#FFC400", t["accent"]).rstrip() + "\n"


def beacon() -> str:
    """The square status beacon: a yellow fill, never a round dot."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 10 10" '
            'aria-hidden="true"><rect x="1" y="1" width="8" height="8" '
            f'fill="{THEMES["light"]["accent"]}"/></svg>\n')


def main() -> None:
    OUT.mkdir(exist_ok=True)
    # Lay out both themes once so every glyph is known before the fonts are subset.
    for theme in THEMES:
        banner(theme)
    for theme in THEMES:
        path = OUT / f"banner-{theme}.svg"
        path.write_text(banner(theme), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")
    marks = {f"logo-{theme}.svg": logo(theme) for theme in THEMES} | {"beacon.svg": beacon()}
    for name, svg in marks.items():
        (OUT / name).write_text(svg, encoding="utf-8")
        print(f"wrote assets/{name}")
    (OUT / "icons").mkdir(exist_ok=True)
    for src in sorted(ICONS.glob("*.svg")):
        for theme in THEMES:
            (OUT / "icons" / f"{src.stem}-{theme}.svg").write_text(icon(src.read_text(encoding="utf-8"), theme), encoding="utf-8")
    print("wrote assets/icons/")


if __name__ == "__main__":
    main()
