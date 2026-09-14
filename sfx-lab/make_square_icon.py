"""make_square_icon.py — آیکون مربعی ۵۱۲×۵۱۲ هماهنگ با Social Preview (برای آواتار مخزن)"""
import os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg
from make_social_preview import (S, C_BG, C_GLOW_A, C_GLOW_B, C_ACC1, C_ACC2, C_TX, C_LINE,
                                 font, spectrum, FF)

W = H = 512 * S
ASSETS = os.environ.get("ASSETS", "assets")
AUDIO = os.environ.get("AUDIO", "audio-pack/mp3/sfx/impact_deep.wav")

img = Image.new("RGBA", (W, H), C_BG + (255,))
d = ImageDraw.Draw(img)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
arr = np.zeros((H, W, 3), np.float32) + np.array(C_BG, np.float32)
arr[:] += np.array(C_GLOW_A, np.float32) * (np.exp(-(((xx - W * .2) ** 2 + (yy - H * .1) ** 2)) / (2 * (H * .8) ** 2)))[..., None] * .45
arr[:] += np.array(C_GLOW_B, np.float32) * (np.exp(-(((xx - W * .95) ** 2 + (yy - H * 1.0) ** 2)) / (2 * (H * .85) ** 2)))[..., None] * .38
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")

step = 34 * S
d = ImageDraw.Draw(img)
for x in range(step, W, step):
    for y in range(step, H, step):
        d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(255, 255, 255, 24))

# طیف دایره‌ای
vals = spectrum(os.environ.get("SPECTRUM_AUDIO", "audio-pack/mp3/bgm/bgm_tech_explainer.mp3"), bands=64)
cx = cy = W // 2
r_in, r_out = int(96 * S), int(196 * S)
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dl = ImageDraw.Draw(layer)
n = len(vals)
for i, v in enumerate(vals):
    a0 = -90 + i * (360 / n) - (360 / n) * .3
    a1 = -90 + i * (360 / n) + (360 / n) * .3
    rr = r_in + (r_out - r_in) * (.1 + .9 * v)
    t = i / n
    col = (int(C_ACC1[0] * (1 - t) + C_ACC2[0] * t),
           int(C_ACC1[1] * (1 - t) + C_ACC2[1] * t),
           int(C_ACC1[2] * (1 - t) + C_ACC2[2] * t))
    dl.pieslice([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1, fill=col + (240,))
img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(14 * S)))
img.alpha_composite(layer)
d = ImageDraw.Draw(img)
d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], outline=(255, 255, 255, 100), width=2 * S)
d.ellipse([cx - r_in + 30 * S, cy - r_in + 30 * S, cx + r_in - 30 * S, cy + r_in - 30 * S],
          fill=(13, 18, 38, 240), outline=(129, 140, 248, 130), width=2 * S)

# موج سینوسی برند در مرکز
pts = []
amp = 26 * S
for i in range(121):
    t = i / 120
    x = cx - 60 * S + 120 * S * t
    y = cy + amp * np.sin(t * np.pi * 3) * (0.25 + 0.75 * np.sin(np.pi * t))
    pts.append((x, y))
for i in range(len(pts) - 1):
    t = i / len(pts)
    col = (int(C_ACC1[0] * (1 - t) + C_ACC2[0] * t),
           int(C_ACC1[1] * (1 - t) + C_ACC2[1] * t),
           int(C_ACC1[2] * (1 - t) + C_ACC2[2] * t))
    d.line([pts[i], pts[i + 1]], fill=col, width=7 * S)

# خط گرادیانی بالا
for i in range(W):
    t = i / W
    c = (int(C_ACC1[0] * (1 - t) + C_ACC2[0] * t),
         int(C_ACC1[1] * (1 - t) + C_ACC2[1] * t),
         int(C_ACC1[2] * (1 - t) + C_ACC2[2] * t))
    d.line([(i, 0), (i, 6 * S)], fill=c)

out = img.convert("RGB").resize((512, 512), Image.LANCZOS)
p = os.environ.get("OUTFILE", "repo-icon.png")
out.save(p, optimize=True)
print("saved", p, os.path.getsize(p) // 1024, "KB")
