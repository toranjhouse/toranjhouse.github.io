"""Prepare the site's images from the raw sources in _raw/.

- photos  -> resized WebP (two widths each)
- dishes  -> background removed (solid navy backdrop keyed out), cropped square, WebP with alpha
Run:  python3 _tools/build_images.py
"""
from pathlib import Path
import numpy as np, cv2
from PIL import Image

ROOT = Path(__file__).parent.parent
RAW = ROOT / "_raw"
OUT = ROOT / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)

def save_webp(im: Image.Image, name: str, width: int, quality=80):
    w, h = im.size
    if width < w:
        im = im.resize((width, round(h * width / w)), Image.LANCZOS)
    p = OUT / f"{name}-{im.size[0]}.webp"
    im.save(p, "WEBP", quality=quality, method=6)
    print(f"{p.name:34s} {im.size}  {p.stat().st_size/1024:6.1f} KB")

# ---------- photos ----------
def photo(src, name, widths, crop=None, quality=80):
    im = Image.open(RAW / src).convert("RGB")
    if crop:
        W, H = im.size
        x0, y0, x1, y1 = crop
        im = im.crop((round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H)))
    for w in widths:
        save_webp(im, name, w, quality)

photo("hero-courtyard.jpg", "hero", [1376, 880], quality=82)
photo("story-fire.jpg", "story-fire", [928, 560])
photo("space-shahneshin.jpg", "space-shahneshin", [1200, 720])
photo("space-courtyard.jpg", "space-courtyard", [1200, 720])
# third "space" panel: the takht side of the courtyard at dusk (left part of the hero photo)
photo("hero-courtyard.jpg", "space-takht", [760], crop=(0.0, 0.10, 0.56, 1.0), quality=84)

# ---------- dishes: key out the navy backdrop ----------
def _lin(x):   # sRGB -> linear
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)

def _srgb(x):  # linear -> sRGB
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)

def cutout(src, name, sizes=(880, 480), thresh=11.0):
    """Key out the navy backdrop *and its cast shadow*.

    A shadow is just the backdrop colour scaled towards black, so every pixel is compared
    with the nearest colour on the line black -> backdrop instead of with the backdrop itself.
    """
    bgr = cv2.imread(str(RAW / src), cv2.IMREAD_COLOR)
    h, w = bgr.shape[:2]
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    lin = _lin(rgb)

    # backdrop model (soft vignette): quadratic surface fitted on the outer ring, robustly
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    xn, yn = xs / w - 0.5, ys / h - 0.5
    A = np.stack([np.ones_like(xn), xn, yn, xn * xn, xn * yn, yn * yn], -1)
    m = int(0.035 * w)
    ring = (xs < m) | (xs >= w - m) | (ys < m) | (ys >= h - m)
    sel = ring.copy()
    for _ in range(3):
        coef, *_ = np.linalg.lstsq(A[sel], lin[sel], rcond=None)
        bg = np.clip(A @ coef, 1e-4, 1)
        sel = ring & (np.abs(lin - bg).max(-1) < 0.02)

    k = np.clip((lin * bg).sum(-1) / (bg * bg).sum(-1), 0.0, 1.25)[..., None]
    nearest = _srgb(k * bg).astype(np.float32)          # closest "backdrop or shadow" colour
    d = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB) - cv2.cvtColor(nearest, cv2.COLOR_RGB2LAB)
    dist = np.sqrt((d ** 2).sum(-1))

    mask = (dist > thresh).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    n, lbl, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    k_big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    blob = (lbl == k_big).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    solid = np.zeros_like(blob)
    cv2.drawContours(solid, cnts, -1, 255, cv2.FILLED)
    solid = cv2.morphologyEx(solid, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))

    # soft, slightly contracted edge (avoids a backdrop-coloured fringe)
    soft = cv2.GaussianBlur(solid.astype(np.float32) / 255.0, (0, 0), 1.7)
    alpha = np.clip((soft - 0.52) / 0.36, 0, 1)

    x, y, bw, bh = cv2.boundingRect((alpha > 0.02).astype(np.uint8))
    side = int(max(bw, bh) * 1.03)
    cx, cy = x + bw / 2, y + bh / 2
    x0, y0 = int(round(cx - side / 2)), int(round(cy - side / 2))

    rgba = np.dstack([(rgb * 255).astype(np.uint8), (alpha * 255).astype(np.uint8)])
    canvas = np.zeros((side, side, 4), np.uint8)
    sx0, sy0 = max(x0, 0), max(y0, 0)
    sx1, sy1 = min(x0 + side, w), min(y0 + side, h)
    canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = rgba[sy0:sy1, sx0:sx1]
    im = Image.fromarray(canvas, "RGBA")
    for s_ in sizes:
        o = im.resize((s_, s_), Image.LANCZOS)
        p = OUT / f"{name}-{s_}.webp"
        o.save(p, "WEBP", quality=84, alpha_quality=92, method=6)
        print(f"{p.name:34s} {o.size}  {p.stat().st_size/1024:6.1f} KB   (object {bw}x{bh}px of {w})")
    return im

if __name__ == "__main__":
    sheet = [cutout(f"dish-{n}.png", f"dish-{n}") for n in ["soltani", "ghormeh", "fesenjan", "dizi", "zereshk", "tahchin"]]
    # contact sheet on the two page grounds to eyeball the edges (not shipped)
    S = 440
    cs = Image.new("RGB", (S * 3, S * 2), (19, 30, 78))
    for i, im in enumerate(sheet):
        t = im.resize((S - 30, S - 30), Image.LANCZOS)
        if i == 4:
            cs.paste(Image.new("RGB", (S, S), (242, 237, 227)), (S, S))
        cs.paste(t, ((i % 3) * S + 15, (i // 3) * S + 15), t)
    cs.save(ROOT / "_tools" / "_check_cutouts.png")
