"""Genera il banner animato del profilo nello stile "Dark Lab" di buildwithbelletz.

Il resto del README è markdown nativo, leggibile anche da mobile.
Uso: python scripts/build_assets.py  (scrive assets/banner.svg)
I testi hanno larghezza fissata con textLength, così il layout non dipende dal font installato.
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

BG, BORDER = "#080808", "#1f1f1f"
TEXT, MUTED, SUBTLE, ACCENT = "#ededed", "#a3a3a3", "#777777", "#2bff9b"
MONO = "'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "Inter,system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
W = 1200
CW = 0.6  # larghezza di un carattere monospace in em

GRID = f"""<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
  <path d="M32 0H0V32" fill="none" stroke="#ffffff" stroke-opacity="0.035"/>
</pattern>"""


def mono(x, y, text, size, fill, weight=400, spacing=0.0, anchor="start", extra=""):
    width = len(text) * size * (CW + spacing)
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" textLength="{width:.1f}" lengthAdjust="spacingAndGlyphs"{extra}>'
            f'{escape(text)}</text>')


def svg(height, body, label, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" '
            f'role="img" aria-label="{escape(label)}">\n<title>{escape(label)}</title>\n<defs>{GRID}{defs}</defs>\n'
            f'<rect width="{W}" height="{height}" fill="{BG}"/>\n'
            f'<rect width="{W}" height="{height}" fill="url(#grid)"/>\n'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" fill="none" stroke="{BORDER}"/>\n'
            f'{body}\n</svg>\n')


def banner():
    phrases = ["Build.", "Build projects.", "Build experiments.", "Build results.", "Build with Belletz."]
    size, x0, y0 = 88, 56, 200
    cw = size * CW
    type_s, hold_s, erase_s = 0.07, 1.1, 0.35
    starts, t = [], 0.4
    for p in phrases:
        starts.append(t)
        t += len(p) * type_s + hold_s + erase_s
    total = t + 6  # la frase finale resta a schermo prima di ricominciare
    pct = lambda s: f"{100 * s / total:.3f}%"

    css, groups = [], []
    for i, p in enumerate(phrases):
        n, final = len(p), i == len(phrases) - 1
        a, b = starts[i], starts[i] + n * type_s
        c = total - 0.4 if final else b + hold_s
        d = total if final else c + erase_s
        # Visibilità del testo: rivelato da sinistra a destra a scatti (un carattere per volta).
        css.append(f"@keyframes p{i}{{0%,{pct(a)}{{clip-path:inset(0 100% 0 0)}}"
                   f"{pct(a)}{{animation-timing-function:steps({n},end)}}"
                   f"{pct(b)},{pct(c)}{{clip-path:inset(0 0 0 0)}}"
                   f"{pct(c)}{{animation-timing-function:steps({n},end)}}"
                   f"{pct(d)},100%{{clip-path:inset(0 100% 0 0)}}}}")
        css.append(f".p{i}{{animation:p{i} {total:.2f}s linear infinite;clip-path:inset(0 100% 0 0)}}")
        groups.append(f'<g class="p{i}">{mono(x0, y0, p, size, TEXT, 800)}</g>')

    # Il cursore segue la fine della frase corrente.
    frames = [f"0%{{transform:translateX(0)}}"]
    for i, p in enumerate(phrases):
        n, final = len(p), i == len(phrases) - 1
        a, b = starts[i], starts[i] + n * type_s
        c = total - 0.4 if final else b + hold_s
        d = total if final else c + erase_s
        end = n * cw
        frames.append(f"{pct(a)}{{transform:translateX(0);animation-timing-function:steps({n},end)}}")
        frames.append(f"{pct(b)},{pct(c)}{{transform:translateX({end:.1f}px);animation-timing-function:steps({n},end)}}")
        frames.append(f"{pct(d)}{{transform:translateX(0)}}")
    css.append("@keyframes cur{" + "".join(frames) + "}")
    css.append(f".cur{{animation:cur {total:.2f}s linear infinite}}")
    css.append("@keyframes blink{50%{opacity:0}} .blink{animation:blink 1s steps(1) infinite}")
    css.append("@media (prefers-reduced-motion: reduce){[class^=p]{animation:none!important;clip-path:none!important}"
               ".p0,.p1,.p2,.p3{display:none}.cur{animation:none;transform:translateX(" + f"{len(phrases[-1]) * cw:.1f}px" + ")}}")

    body = f"""<style>{''.join(css)}</style>
<g>
  {mono(56, 84, "~/belletz", 30, ACCENT, 500)}
  {mono(56 + 10 * 30 * CW, 84, "$", 30, SUBTLE)}
  {mono(56 + 12 * 30 * CW, 84, "./run --output", 30, MUTED)}
  {''.join(groups)}
  <g class="cur"><rect class="blink" x="{x0 + 8}" y="{y0 - size * 0.74:.1f}" width="{size * 0.5:.1f}" height="{size * 0.8:.1f}" fill="{ACCENT}"/></g>
  {mono(56, 296, ">", 36, ACCENT, 700)}
  <text x="104" y="296" font-family="{SANS}" font-size="36" font-weight="500" fill="{TEXT}">Full Stack &amp; Forward Deployed AI Engineer</text>
</g>"""
    return svg(350, body, "Build with Belletz. Full Stack & Forward Deployed AI Engineer.")


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "banner.svg").write_text(banner(), encoding="utf-8")
    print(f"wrote {OUT / 'banner.svg'}")


if __name__ == "__main__":
    main()
