"""Apply a warm vintage film treatment to the shop photos."""
import os
import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

SRC = "/Users/ilwoong/Documents/vintage"
OUT = os.path.join(SRC, "docs", "images")
os.makedirs(OUT, exist_ok=True)

MAX_W = 1600


def vintage(im: Image.Image, max_w: int = MAX_W) -> Image.Image:
    im = ImageOps.exif_transpose(im).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)

    # Desaturate and warm the tones toward sepia
    im = ImageEnhance.Color(im).enhance(0.62)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, v * 1.10 + 12))
    g = g.point(lambda v: min(255, v * 1.02 + 6))
    b = b.point(lambda v: v * 0.88)
    im = Image.merge("RGB", (r, g, b))

    # Lift blacks / soften highlights for a faded film curve
    im = im.point(lambda v: 28 + (v / 255) ** 1.05 * (235 - 28))
    im = ImageEnhance.Contrast(im).enhance(1.06)

    # Vignette
    mask = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(mask)
    w, h = im.size
    d.ellipse((-w * 0.35, -h * 0.35, w * 1.35, h * 1.35), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w * 0.18))
    dark = ImageEnhance.Brightness(im).enhance(0.62)
    im = Image.composite(im, dark, mask)

    # Film grain
    random.seed(7)
    grain = Image.effect_noise(im.size, 22).convert("L")
    im = Image.composite(
        ImageEnhance.Brightness(im).enhance(1.06),
        ImageEnhance.Brightness(im).enhance(0.94),
        grain,
    )
    return im


for i in range(1, 5):
    src = os.path.join(SRC, f"photo{i}.jpeg")
    out = os.path.join(OUT, f"photo{i}.jpg")
    if not os.path.exists(src):
        print("skip (missing source):", src)
        continue
    img = vintage(Image.open(src))
    img.save(out, quality=82, optimize=True)
    print(out, img.size)

# Curated underground-shop shots (portrait) for the film-strip section.
# Sources are the raw .jpeg files dropped straight into docs/images.
FILMSTRIP = [10, 6, 8, 11, 7, 9, 12, 13]
for i in FILMSTRIP:
    src = os.path.join(OUT, f"photo{i}.jpeg")
    out = os.path.join(OUT, f"photo{i}.jpg")
    if not os.path.exists(src):
        print("skip (missing source):", src)
        continue
    img = vintage(Image.open(src), max_w=1100)
    img.save(out, quality=82, optimize=True)
    print(out, img.size)
