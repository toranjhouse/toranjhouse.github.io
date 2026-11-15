# -*- coding: utf-8 -*-
"""برش عکس‌های سفالِ فیروزه‌ای و رونویسی webp های منو."""
import io, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image

HERE = Path(__file__).parent
src = io.open(HERE / "build_images.py", encoding="utf-8").read()
code = src[src.index("def _lin"): src.index("if __name__")]
ROOT = HERE.parent
RAW, OUT = ROOT / "_raw", ROOT / "assets" / "img"
ns = dict(np=np, cv2=cv2, Image=Image, ROOT=ROOT, RAW=RAW, OUT=OUT, Path=Path)
exec(code, ns)
cutout = ns["cutout"]

for k in sys.argv[1:]:
    cutout(f"turq-{k}.png", f"dish-{k}")
