# -*- coding: utf-8 -*-
"""برش پس‌زمینهٔ لاجوردی تصویرهای کنار سفره و خروجی webp (با همان تابع cutout)."""
import io
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

for k in ["sangak", "salad", "mast", "zeytun", "doogh", "torshi", "ash", "halva", "spread"]:
    cutout(f"kenar-{k}.png", f"dish-kenar-{k}")

for k in ["chai", "damanoush", "ghahve", "bastani", "qalyan-miveh", "qalyan-asal"]:
    cutout(f"tea-{k}.png", f"dish-tea-{k}")
