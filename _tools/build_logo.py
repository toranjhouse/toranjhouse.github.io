"""Draw the site's Nastaliq word-mark and hero verse as crisp SVG outlines.

Noto Nastaliq Urdu (OFL) is used only as an outline source; the SVGs ship instead of the font.
Run:  python3 _tools/build_logo.py
"""
from pathlib import Path
import uharfbuzz as uh
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = Path(__file__).parent
FONT = HERE / "fonts" / "NotoNastaliq-500.ttf"
OUT = HERE.parent / "assets" / "img"

def text_to_svg(text: str, out: Path, color: str, pad: int = 6):
    face = TTFont(FONT)
    upem = face["head"].unitsPerEm
    hb_font = uh.Font(uh.Face(FONT.read_bytes()))
    buf = uh.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    uh.shape(hb_font, buf)
    gs = face.getGlyphSet()
    from fontTools.pens.boundsPen import BoundsPen
    parts, x, y = [], 0.0, 0.0
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gid = info.codepoint
        name = hb_font.get_glyph_name(gid)
        tx, ty = x + pos.x_offset, -(y + pos.y_offset)
        bpen = BoundsPen(gs)
        gs[name].draw(TransformPen(bpen, (1, 0, 0, -1, tx, ty)))
        if bpen.bounds is None:
            x += pos.x_advance; y += pos.y_advance; continue
        bx0, by0, bx1, by1 = bpen.bounds
        x0, y0 = min(x0, bx0), min(y0, by0)
        x1, y1 = max(x1, bx1), max(y1, by1)
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (1, 0, 0, -1, tx, ty)))
        d = pen.getCommands()
        if d:
            parts.append(f'<path d="{d}"/>')
        x += pos.x_advance
        y += pos.y_advance
    vb = f"{x0-pad:.0f} {y0-pad:.0f} {x1-x0+2*pad:.0f} {y1-y0+2*pad:.0f}"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" fill="{color}" '
           f'role="img" aria-hidden="true" focusable="false">{"".join(parts)}</svg>\n')
    out.write_text(svg, encoding="utf-8")
    print(f"{out.name}: {out.stat().st_size/1024:.1f} KB  viewBox={vb}")

text_to_svg("ارسی", OUT / "logo.svg", "#f2ede3")
text_to_svg("ارسی", OUT / "logo-gold.svg", "#f0c46a")
text_to_svg("حکایتِ نور و رنگ و خاطره", OUT / "hero-verse.svg", "#f0c46a")
