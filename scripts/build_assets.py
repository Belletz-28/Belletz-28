"""Genera gli SVG del profilo nello stile "Dark Lab" di buildwithbelletz.

Uso: python scripts/build_assets.py  (scrive in assets/)
I testi hanno larghezza fissata con textLength, così il layout non dipende dal font installato.
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

BG, SURFACE, BORDER, BORDER_MID = "#080808", "#111111", "#1f1f1f", "#2a2a2a"
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
    size, x0, y0 = 76, 64, 210
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
    css.append("@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}} .pulse{animation:pulse 2.4s ease-in-out infinite}")
    css.append("@media (prefers-reduced-motion: reduce){[class^=p]{animation:none!important;clip-path:none!important}"
               ".p0,.p1,.p2,.p3{display:none}.cur{animation:none;transform:translateX(" + f"{len(phrases[-1]) * cw:.1f}px" + ")}}")

    chip_text = "AVAILABLE FOR PROJECTS"
    chip_w = len(chip_text) * 13 * (CW + 0.12) + 46
    meta_x = 64 + chip_w + 22
    meta = "/  FULL STACK  /  FORWARD DEPLOYED AI  /  FOUNDER @ CBM-SOLUTIONS"
    body = f"""<style>{''.join(css)}</style>
<g>
  {mono(64, 70, "[BELLETZ]", 15, ACCENT, 700, 0.1)}
  {mono(W - 64, 70, "// 2026", 13, SUBTLE, 400, 0.1, "end")}
  <line x1="64" y1="96" x2="{W - 64}" y2="96" stroke="{BORDER}"/>
  {mono(64, 128, "~/belletz", 18, ACCENT)}
  {mono(64 + 10 * 18 * CW, 128, "$", 18, SUBTLE)}
  {mono(64 + 12 * 18 * CW, 128, "./run --output", 18, MUTED)}
  {''.join(groups)}
  <g class="cur"><rect class="blink" x="{x0 + 6}" y="{y0 - size * 0.74:.1f}" width="{size * 0.5:.1f}" height="{size * 0.8:.1f}" fill="{ACCENT}"/></g>
  {mono(64, 270, ">", 22, ACCENT)}
  <text x="96" y="270" font-family="{SANS}" font-size="22" fill="{MUTED}">Full Stack &amp; Forward Deployed AI Engineer — from idea to production.</text>
  <rect x="64.5" y="304.5" width="{chip_w:.1f}" height="34" fill="{ACCENT}" fill-opacity="0.06" stroke="{ACCENT}" stroke-opacity="0.5"/>
  <circle class="pulse" cx="84" cy="321.5" r="4" fill="{ACCENT}"/>
  {mono(98, 326, chip_text, 13, ACCENT, 600, 0.12)}
  {mono(meta_x, 326, meta, 13, SUBTLE, 400, 0.08)}
</g>"""
    return svg(380, body, "Belletz — Build with Belletz. Full Stack & Forward Deployed AI Engineer, founder of CBM-Solutions.")


def section(num, title):
    label = f"// {num:02d} — {title.upper()}"
    body = (f'{mono(0, 34, label, 15, ACCENT, 500, 0.15)}\n'
            f'<line x1="0" y1="62" x2="{W}" y2="62" stroke="{BORDER}"/>')
    # Header senza sfondo: si appoggia alla pagina GitHub come le intestazioni del sito.
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="64" viewBox="0 0 {W} 64" role="img" '
            f'aria-label="{escape(title)}"><title>{escape(title)}</title>{body}</svg>\n')


def wrap(text, chars):
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > chars and cur:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur]


def cards(items, label):
    cols, gap, pad = 2, 24, 32
    cw = (W - 2 * pad - gap) / cols
    ch = 190
    rows = (len(items) + cols - 1) // cols
    out = []
    for i, (tag, title, desc, techs) in enumerate(items):
        x = pad + (i % cols) * (cw + gap)
        y = pad + (i // cols) * (ch + gap)
        out.append(f'<rect x="{x + .5:.1f}" y="{y + .5}" width="{cw - 1:.1f}" height="{ch - 1}" fill="{SURFACE}" stroke="{BORDER_MID}"/>')
        out.append(f'<rect x="{x:.1f}" y="{y}" width="3" height="{ch}" fill="{ACCENT}"/>')
        out.append(mono(x + 28, y + 40, f"[{tag}]", 12, ACCENT, 500, 0.15))
        out.append(mono(x + 28, y + 74, title, 22, TEXT, 700))
        for j, line in enumerate(wrap(desc, 58)):
            out.append(f'<text x="{x + 28:.1f}" y="{y + 108 + j * 24}" font-family="{SANS}" font-size="16" fill="{MUTED}">{escape(line)}</text>')
        out.append(mono(x + 28, y + ch - 24, "  ·  ".join(techs), 12, SUBTLE, 400, 0.05))
    return svg(2 * pad + rows * ch + (rows - 1) * gap, "\n".join(out), label)


def stack(groups, label):
    pad, row_h, size = 32, 58, 14
    out = []
    for r, (area, techs) in enumerate(groups):
        y = pad + r * row_h
        out.append(mono(pad, y + 26, area.upper(), 12, SUBTLE, 500, 0.15))
        x = pad + 200
        for t in techs:
            w = len(t) * size * CW + 28
            if x + w > W - pad:
                break
            out.append(f'<rect x="{x + .5:.1f}" y="{y + 4.5}" width="{w:.1f}" height="32" fill="{SURFACE}" stroke="{BORDER_MID}"/>')
            out.append(mono(x + 14, y + 25, t, size, TEXT))
            x += w + 10
        if r < len(groups) - 1:
            out.append(f'<line x1="{pad}" y1="{y + row_h - 7}" x2="{W - pad}" y2="{y + row_h - 7}" stroke="{BORDER}" stroke-dasharray="2 6"/>')
    return svg(2 * pad + len(groups) * row_h - 14, "\n".join(out), label)


def principles(items, label):
    pad, row_h = 36, 72
    out = []
    for i, (title, desc) in enumerate(items):
        y = pad + i * row_h
        out.append(mono(pad, y + 30, f"{i + 1:02d}", 28, ACCENT, 700))
        out.append(mono(pad + 80, y + 22, title, 17, TEXT, 700))
        out.append(f'<text x="{pad + 80}" y="{y + 48}" font-family="{SANS}" font-size="16" fill="{MUTED}">{escape(desc)}</text>')
    return svg(2 * pad + len(items) * row_h - 16, "\n".join(out), label)


def footer():
    body = f"""{mono(64, 52, "[BELLETZ]", 15, ACCENT, 700, 0.1)}
{mono(W - 64, 52, "Build with Belletz.", 15, MUTED, 500, 0, "end")}
<line x1="64" y1="78" x2="{W - 64}" y2="78" stroke="{BORDER}"/>
{mono(64, 108, "Crafting digital systems with precision — data, backend, web and AI.", 12, SUBTLE, 400, 0.05)}
{mono(W - 64, 108, "STATUS: BUILDING", 12, ACCENT, 500, 0.12, "end")}"""
    return svg(136, body, "Build with Belletz.")


SERVICES = [
    ("AI", "AI engineering", "LLM-based agents, automation and document intelligence applied to real business workflows.",
     ["Claude API", "LangGraph", "RAG", "OCR"]),
    ("FULL STACK", "Full stack development", "Web platforms, internal tools and APIs, from architecture to deployment.",
     ["Next.js", "FastAPI", "Go", "Postgres"]),
    ("B2B", "B2B & e-commerce", "Ordering, catalogues and operational back offices for companies that sell at scale.",
     ["Catalogues", "Orders", "Back office"]),
    ("DATA", "Data & finance", "Data analysis and financial tooling, where my journey started with Python.",
     ["Python", "pandas", "DuckDB", "Metabase"]),
]

STACK = [
    ("Languages", ["Python", "TypeScript", "Go", "Rust", "SQL"]),
    ("AI & LLM", ["Claude API", "LangGraph", "RAG", "RAGAS", "Docling", "MinerU", "OpenCV"]),
    ("Backend", ["FastAPI", "Flask", "Pydantic", "SQLAlchemy", "Node.js", "Bun"]),
    ("Frontend", ["Next.js", "React", "Astro", "Tailwind", "TanStack Query", "Sanity"]),
    ("Data", ["PostgreSQL", "pgvector", "Qdrant", "Supabase", "DuckDB", "pandas"]),
    ("Platform", ["Docker", "GitHub Actions", "Turborepo", "pnpm", "uv", "Fly.io"]),
    ("Quality", ["pytest", "Vitest", "Playwright", "Ruff", "Biome", "mypy"]),
]

PRINCIPLES = [
    ("Forward-deployed", "I embed with the team and the problem, then ship."),
    ("Pragmatic engineering", "Small iterations, working software, measurable outcomes."),
    ("Founder mindset", "Product, delivery and maintainability, not just code."),
]


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "banner.svg": banner(),
        "section-about.svg": section(1, "About"),
        "section-services.svg": section(2, "What I do"),
        "section-stack.svg": section(3, "Stack"),
        "section-principles.svg": section(4, "How I work"),
        "section-contact.svg": section(5, "Contact"),
        "services.svg": cards(SERVICES, "What I do: AI engineering, full stack development, B2B & e-commerce, data & finance."),
        "stack.svg": stack(STACK, "Tech stack: " + "; ".join(f"{a}: {', '.join(t)}" for a, t in STACK)),
        "principles.svg": principles(PRINCIPLES, "How I work: " + " ".join(f"{t} — {d}" for t, d in PRINCIPLES)),
        "footer.svg": footer(),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(files)} files to {OUT}")


if __name__ == "__main__":
    main()
