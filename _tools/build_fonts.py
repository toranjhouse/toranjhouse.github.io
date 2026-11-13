"""Build the self-hosted web fonts for the site (subset + woff2).

Sources (all SIL OFL 1.1): Vazirmatn, Markazi Text, Noto Nastaliq Urdu.
Run:  python3 _tools/build_fonts.py
"""
from io import BytesIO
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset

HERE = Path(__file__).parent
SRC = HERE / "fonts"
OUT = HERE.parent / "assets" / "fonts"
OUT.mkdir(parents=True, exist_ok=True)

UNICODES = (
    "U+0020-007E,U+00A0,U+00AB,U+00B7,U+00BB,U+00D7,"
    "U+060C,U+061B,U+061F,U+0621-063A,U+0640-0656,U+0660-066D,U+0670,"
    "U+067E,U+0686,U+0698,U+06A9,U+06AF,U+06BE,U+06C0-06C3,U+06CC,U+06D2,U+06D4,U+06D5,U+06F0-06F9,"
    "U+200B-200F,U+2010-2015,U+2018-201D,U+2022,U+2026,U+2039,U+203A,U+2212,U+FDFC"
)

def reload(font: TTFont) -> TTFont:
    buf = BytesIO(); font.save(buf); buf.seek(0)
    return TTFont(buf)

def do_subset(font: TTFont, out: Path, extra_features=()):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = list(opts.layout_features) + list(extra_features)
    opts.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]
    opts.notdef_outline = True
    opts.drop_tables += ["DSIG"]
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=subset.parse_unicodes(UNICODES))
    sub.subset(font)
    font.flavor = "woff2"
    font.save(out)
    print(f"{out.name}: {out.stat().st_size/1024:.1f} KB, {len(font.getGlyphOrder())} glyphs")

# --- Vazirmatn (body / UI): keep wght 300..800
f = TTFont(SRC / "Vazirmatn-VF.ttf")
f = instancer.instantiateVariableFont(f, {"wght": (300, 800)})
f = reload(f)  # normalise gvar after instancing
do_subset(f, OUT / "vazirmatn-var.woff2", extra_features=["tnum"])

# --- Markazi Text (display): font has no ZWNJ/ZWJ glyphs -> map them to its zero-width blank
f = TTFont(SRC / "MarkaziText-VF.ttf")
for table in f["cmap"].tables:
    if table.isUnicode():
        table.cmap[0x200C] = "uni200B"
        table.cmap[0x200D] = "uni200B"
do_subset(f, OUT / "markazi-text-var.woff2")

# --- Noto Nastaliq Urdu: static instance used only to draw SVG outlines (logo + verse)
f = TTFont(SRC / "NotoNastaliqUrdu-VF.ttf")
f = instancer.instantiateVariableFont(f, {"wght": 500})
f.save(SRC / "NotoNastaliq-500.ttf")
print("NotoNastaliq-500.ttf written (outline source)")
