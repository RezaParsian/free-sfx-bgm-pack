"""
make_social_preview.py — ساخت تصویر Social Preview برای گیت‌هاب (۱۲۸۰×۶۴۰)
نکته: نوارهای طیف از FFT واقعیِ فایل bgm_tech_explainer.mp3 گرفته می‌شن.
"""
import os, glob, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

S = 2                      # سوپرسمپلینگ
W, H = 1280 * S, 640 * S
FF = imageio_ffmpeg.get_ffmpeg_exe()
ASSETS = os.environ.get("ASSETS", "assets")
OUTDIR = os.environ.get("OUTDIR", ".")
AUDIO = os.environ.get("AUDIO", "audio-pack/mp3/bgm/bgm_tech_explainer.mp3")
AUDIO2 = os.environ.get("AUDIO2", "audio-pack/mp3/bgm/bgm_hook_loop_8s.mp3")
HANDLE = os.environ.get("HANDLE", "")
N_SFX = len(glob.glob(os.environ.get("SFXDIR", "audio-pack/sfx") + "/*.wav"))
N_BGM = len(glob.glob(os.environ.get("BGMDIR", "audio-pack/bgm") + "/*.wav"))
TITLE1 = os.environ.get("TITLE1", "Code-Synthesized")
TITLE2 = os.environ.get("TITLE2", "SFX & BGM Library")

C_BG = (9, 12, 26)
C_GLOW_A = (58, 74, 190)      # ایندیگو
C_GLOW_B = (14, 132, 158)     # فیروزه‌ای
C_ACC1 = (129, 140, 248)      # indigo-400
C_ACC2 = (56, 189, 248)       # sky-400
C_TX = (238, 241, 252)
C_MUT = (168, 176, 205)
C_LINE = (46, 56, 94)
C_PILL = (26, 33, 62)


def font(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(ASSETS, name), int(size * S))
    if weight and name == "Inter.ttf":
        try:
            f.set_variation_by_axes([14, weight])
        except Exception:
            pass
    return f


# ─────────────── طیف واقعی از فایل صوتی ───────────────
def spectrum(path, bands=80):
    r = subprocess.run([FF, "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", "22050", "-"],
                       capture_output=True)
    a = np.frombuffer(r.stdout, dtype=np.float32)
    if len(a) < 1000:
        a = np.random.default_rng(1).standard_normal(22050 * 5).astype(np.float32) * .2
    win = a[: 22050 * 8] * np.hanning(len(a[: 22050 * 8]))
    mag = np.abs(np.fft.rfft(win))
    fr = np.fft.rfftfreq(len(win), 1 / 22050)
    out = []
    edges = np.geomspace(60, 12000, bands + 1)
    for i in range(bands):
        m = (fr >= edges[i]) & (fr < edges[i + 1])
        out.append(float(mag[m].mean()) if m.any() else 0.0)
    v = np.array(out, dtype=float)
    v = np.log1p(v / (v.max() + 1e-9) * 60)          # فشرده‌سازی لگاریتمی
    v = (v - v.min()) / (v.max() - v.min() + 1e-9)
    return np.clip(v ** 1.25, 0.04, 1.0)


# ─────────────── پس‌زمینه ───────────────
def background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.zeros((H, W, 3), np.float32) + np.array(C_BG, np.float32)

    def glow(cx, cy, sigma, color, amp):
        d2 = (xx - cx) ** 2 + (yy - cy) ** 2
        g = np.exp(-d2 / (2 * sigma ** 2))[..., None] * amp
        img[:] += np.array(color, np.float32) * g

    glow(W * 0.16, H * 0.02, H * 0.72, C_GLOW_A, 0.42)
    glow(W * 0.94, H * 1.02, H * 0.80, C_GLOW_B, 0.34)
    glow(W * 0.62, H * 0.46, H * 0.46, (40, 48, 110), 0.22)

    base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(base)

    # شبکه‌ی نقطه‌ای ظریف
    step = 34 * S
    for x in range(step, W, step):
        for y in range(step, H, step):
            d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(255, 255, 255, 26))

    # خط گرادیانی بالای تصویر
    for i in range(W):
        t = i / W
        c = (int(C_ACC1[0] * (1 - t) + C_ACC2[0] * t),
             int(C_ACC1[1] * (1 - t) + C_ACC2[1] * t),
             int(C_ACC1[2] * (1 - t) + C_ACC2[2] * t))
        d.line([(i, 0), (i, 5 * S)], fill=c)
    return base


# ─────────────── طیف دایره‌ای ───────────────
def radial_spectrum(img, vals, cx, cy, r_in, r_out):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    n = len(vals)
    for i, v in enumerate(vals):
        a0 = -90 + i * (360 / n) - (360 / n) * 0.28
        a1 = -90 + i * (360 / n) + (360 / n) * 0.28
        rr = r_in + (r_out - r_in) * (0.10 + 0.90 * v)
        t = i / n
        col = (int(C_ACC1[0] * (1 - t) + C_ACC2[0] * t),
               int(C_ACC1[1] * (1 - t) + C_ACC2[1] * t),
               int(C_ACC1[2] * (1 - t) + C_ACC2[2] * t))
        d.pieslice([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1, fill=col + (235,))
    glow = layer.filter(ImageFilter.GaussianBlur(16 * S))
    img.alpha_composite(glow)
    img.alpha_composite(layer)

    d2 = ImageDraw.Draw(img)
    # حلقه‌های راهنما
    for rr, al in [(r_in, 90), (r_in - 26 * S, 40)]:
        d2.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(255, 255, 255, al), width=2 * S)
    # دیسک مرکزی
    d2.ellipse([cx - r_in + 34 * S, cy - r_in + 34 * S, cx + r_in - 34 * S, cy + r_in - 34 * S],
               fill=(13, 18, 38, 235), outline=(129, 140, 248, 120), width=2 * S)
    return d2


# ─────────────── اجزای متنی ───────────────
def pill(img, d, x, y, text, fg=(205, 214, 244), bg=C_PILL, border=C_LINE, size=13, pad=15, hgt=34):
    f = font("Inter.ttf", size, 600)
    tw = d.textlength(text, font=f)
    w = tw + pad * 2 * S
    h = hgt * S
    d.rounded_rectangle([x, y, x + w, y + h], radius=h / 2, fill=bg, outline=border, width=2 * S)
    d.text((x + pad * S, y + h / 2), text, font=f, fill=fg, anchor="lm")
    return x + w + 12 * S


def main():
    vals = spectrum(AUDIO, bands=80)
    img = background().convert("RGBA")
    d = ImageDraw.Draw(img)

    # ── طیف دایره‌ای سمت راست
    cx, cy = int(W * 0.787), int(H * 0.455)
    r_in, r_out = int(110 * S), int(206 * S)
    d = radial_spectrum(img, vals, cx, cy, r_in, r_out)

    fc = font("JetBrainsMono.ttf", 12.5, None)
    d.text((cx, cy - 12 * S), f"{N_SFX} SFX", font=font("Inter.ttf", 25, 800), fill=C_TX, anchor="mm")
    d.text((cx, cy + 16 * S), f"{N_BGM} BGM", font=font("Inter.ttf", 25, 800), fill=C_ACC2, anchor="mm")
    d.text((cx, cy + 46 * S), "TRACKS", font=fc, fill=C_MUT, anchor="mm")

    # ── متن سمت راستِ طیف (چپِ تصویر)
    x0 = int(76 * S)
    y = int(74 * S)

    d.text((x0, y), "OPEN SOURCE  ·  PYTHON + NUMPY + SCIPY", font=fc, fill=C_ACC2)
    y += int(46 * S)

    f_big = font("Inter.ttf", 55, 900)
    f_big2 = font("Inter.ttf", 40, 800)
    d.text((x0, y), TITLE1, font=f_big, fill=C_TX)
    y += int(70 * S)
    d.text((x0, y), TITLE2, font=f_big2, fill=C_ACC1)
    y += int(66 * S)

    f_sub = font("Inter.ttf", 17.5, 400)
    for line in ["Everything generated from raw DSP — no samples, no scraped",
                 "libraries. Zero copyright claims on your monetized videos."]:
        d.text((x0, y), line, font=f_sub, fill=C_MUT)
        y += int(29 * S)

    # ── بلوک‌های آماری
    y += int(26 * S)
    stats = [(str(N_SFX), "SOUND EFFECTS"), (str(N_BGM), "MUSIC TRACKS"), ("0", "COPYRIGHT CLAIMS"), ("0", "ATTRIBUTION")]
    sx = x0
    f_num = font("Inter.ttf", 37, 900)
    f_lab = font("JetBrainsMono.ttf", 10.5)
    for i, (num, lab) in enumerate(stats):
        col = C_TX if i < 2 else (110, 231, 183)
        d.text((sx, y), num, font=f_num, fill=col)
        d.text((sx + 2 * S, y + int(48 * S)), lab, font=f_lab, fill=C_MUT)
        wnum = d.textlength(num, font=f_num)
        wlab = d.textlength(lab, font=f_lab)
        sx += int(max(wnum, wlab) + 46 * S)
        if i < 3:
            d.line([(sx - 24 * S, y + 4 * S), (sx - 24 * S, y + 46 * S)], fill=C_LINE, width=2 * S)

    # ── روبان موج واقعی (از hook loop) بین آمار و بج‌ها
    try:
        r = subprocess.run([FF, "-v", "error", "-i", AUDIO2, "-f", "f32le", "-ac", "1", "-ar", "22050", "-"],
                           capture_output=True)
        a = np.frombuffer(r.stdout, dtype=np.float32)
        win = int(0.006 * 22050)
        nb = 240
        step = max(1, len(a) // nb)
        env = np.array([np.abs(a[i:i + step]).max() if i + step <= len(a) else 0 for i in range(0, len(a) - step, step)])
        env = env / (env.max() + 1e-9)
        ry = int(H - 152 * S)
        rh = int(22 * S)
        x_start, x_end = int(76 * S), int(W - 76 * S)
        npts = min(len(env), 240)
        for i in range(npts):
            t = i / npts
            xx_ = int(x_start + (x_end - x_start) * t)
            hh = max(2 * S, int(env[i] ** 1.4 * rh))
            col = (int(C_ACC1[0] * (1 - t) + C_ACC2[0] * t),
                   int(C_ACC1[1] * (1 - t) + C_ACC2[1] * t),
                   int(C_ACC1[2] * (1 - t) + C_ACC2[2] * t))
            alpha = int(70 + 130 * env[i])
            d.line([(xx_, ry - hh), (xx_, ry + hh)], fill=col + (alpha,), width=max(2, 3 * S // 2))
    except Exception:
        pass

    # ── بج‌ها
    by = int(H - 96 * S)
    bx = x0
    bx = pill(img, d, bx, by, "CC0 / PUBLIC DOMAIN", fg=(134, 239, 172), bg=(16, 46, 36), border=(30, 90, 66))
    bx = pill(img, d, bx, by, "FREE COMMERCIAL USE", fg=(186, 230, 253), bg=(14, 38, 56), border=(28, 76, 108))
    bx = pill(img, d, bx, by, "WAV + MP3", fg=(221, 214, 254), bg=(38, 30, 66), border=(78, 62, 128))
    bx = pill(img, d, bx, by, "REPRODUCIBLE FROM CODE", fg=(203, 213, 225), bg=C_PILL, border=C_LINE)

    # ── امضای پایین-راست
    if HANDLE:
        f_mono = font("JetBrainsMono.ttf", 12)
        d.text((W - 76 * S, H - 74 * S), HANDLE, font=f_mono, fill=(120, 130, 168), anchor="rm")

    out = img.convert("RGB").resize((1280, 640), Image.LANCZOS)
    p = os.path.join(OUTDIR, "social-preview.png")
    out.save(p, optimize=True)
    print("saved", p, os.path.getsize(p) // 1024, "KB")
    return p


if __name__ == "__main__":
    main()
