"""
build_sfx_extra.py — افکت‌های تکمیلی (به REG اضافه می‌شن و در کنار بقیه نوشته می‌شن)
"""
import os, numpy as np
from audio_engine import *
import build_sfx as B
from build_sfx import add, mix_at, reverb, combine


# ── ۱) سوییچ نرم برای نمایان‌شدن متن / زیرنویس / آیکون ──
def text_reveal():
    d = 0.34
    n = pink(d, 71)
    bp = biquad(n, 2600, 0.8, "bp")
    e = np.concatenate([np.linspace(0, 1, int(len(n) * .45)) ** 1.5,
                        np.exp(-np.linspace(0, 5, len(n) - int(len(n) * .45)))])
    x = bp * e * 1.15
    tone = sine(880, d) * np.exp(-np.linspace(0, 1, int(SR * d)) * 9) * 0.10
    x = combine(x, tone)
    t = np.linspace(0, d, len(x))
    add("text_reveal_soft", x, pan=-0.5 + t / d, peak=0.8, width=0.5)


# ── ۲) ایرهورن (برای لحظه‌ی میم/شوخی) ──
def air_horn():
    d = 1.25
    t = t_axis(d)
    x = np.zeros_like(t)
    for f in (233.0, 311.1, 466.2):
        s = saw(f, d) * 0.5 + saw(f * 1.005, d) * 0.4
        s += square(f / 2, d) * 0.18
        x += s
    x = biquad(x, 1900, 0.7, "lp")
    x *= (1 + 0.05 * np.sin(2 * np.pi * 6.2 * t))
    e = env_asr(d, 0.02, 0.35, 1.0) * (0.6 + 0.4 * np.minimum(1, t / 0.12))
    x = x * e
    x = mix_at(x, biquad(noise(0.05, 4), 3000, .7, "hp") * env_perc(.05, .012) * .25, 0.0)
    add("air_horn_meme", reverb(x, 1.6, 0.22), None, 0.9, width=0.35)


# ── ۳) وینیل‌استاپ (توقف ناگهانی برای تاکید/پانچ‌لاین) ──
def vinyl_stop():
    d = 1.6
    # یک آکورد ماریمبا
    src = np.zeros(int(SR * 0.7))
    for f in (523.25, 659.25, 783.99):
        src = mix_at(src, karplus(f, 0.7, 0.997, seed=5, brightness=0.75) * 0.3, 0.0)
    src = biquad(src, 4200, .7, "lp")
    # تایم‌وارپ با نسبت نزولی → هم پیچ و هم سرعت کم می‌شه
    n = len(src)
    ratio = np.linspace(1.0, 0.12, n) ** 1.35
    idx = np.cumsum(ratio)
    idx = idx / idx[-1] * (n - 1)
    warped = np.interp(np.linspace(0, n - 1, n), idx, src)
    x = warped * np.exp(-np.linspace(0, 1, n) * 2.2)
    x = biquad(x, 2600, .7, "lp")
    tail = pink(0.35, 8) * np.exp(-np.linspace(0, 1, int(SR * .35)) * 6) * 0.06
    add("vinyl_stop", combine(x, tail), None, 0.85, width=0.2)


# ── ۴) گنگ/زنگ عمیق (تغییر بخش، شروع فصل، لحظه‌ی مهم) ──
def gong():
    d = 4.2
    x = np.zeros(int(SR * d))
    rng = np.random.default_rng(12)
    for f, g in [(62, .55), (93, .4), (128, .34), (171, .26), (214, .2), (287, .14), (389, .1)]:
        fr = f * (1 + rng.uniform(-0.008, 0.008))
        s = sine(fr, d) * np.exp(-np.linspace(0, 1, int(SR * d)) * rng.uniform(1.2, 2.6))
        s += sine(fr * 1.004, d) * np.exp(-np.linspace(0, 1, int(SR * d)) * 2.0) * .5
        x = combine(x, s * g)
    strike = biquad(noise(0.12, 21), 1400, .6, "bp") * env_perc(.12, .03) * .5
    x = mix_at(x, strike, 0.0)
    x = mix_at(x, sweep(90, 48, 1.2) * np.exp(-np.linspace(0, 1, int(SR * 1.2)) * 3) * .35, 0.0)
    add("gong_section", reverb(x, 3.4, 0.38), None, 0.92, width=0.7)


# ── ۵) نویز اتاق (پُرکردن سکوت مطلق در ضبط‌های خانگی) ──
def room_tone():
    d = 30.0
    x = pink(d, 91) * 0.05
    x = biquad(x, 90, .7, "hp")
    x = biquad(x, 5200, .7, "lp")
    n = int(SR * d)
    # هوم برق/کامپیوتر
    x += (sine(50, d) * .010 + sine(100, d) * .005 + sine(150, d) * .0025)
    # فن: نویز باندباریک با مدولاسیون آرام
    fan = biquad(noise(d, 92), 320, .9, "bp") * (0.018 + 0.004 * np.sin(2 * np.pi * .37 * t_axis(d)))
    x += fan
    # رندوم‌کردن فاز تا لوپ‌شونده‌تر به نظر برسه
    x *= env_asr(d, 1.2, 1.2, 1.0)
    add("room_tone_loop", x, None, 0.09, width=0.25)


EXTRA = [text_reveal, air_horn, vinyl_stop, gong, room_tone]

if __name__ == "__main__":
    import wave
    OUT = os.environ.get("OUTDIR", "audio-pack/sfx")
    os.makedirs(OUT, exist_ok=True)
    for fn in list(B.BUILD) + EXTRA:
        fn()
    for name in B.REG:
        st = B.REG[name]
        data = (np.clip(st, -1, 1) * 32767).astype(np.int16)
        with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes(data.tobytes())
        print(f"{name:26s} {len(st)/SR:5.2f}s")
