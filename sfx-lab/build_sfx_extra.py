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

# ═══════════════ پک تایپ و ترمینال (مخصوص آموزش برنامه‌نویسی / لینوکس) ═══════════════
def _key(seed, pitch=1.0, gain=1.0, clicky=1.0, soft=0.0):
    """یک فشار کلید مکانیکی: کلیک سوییچ + بدنه‌ی کی‌کپ + تاک پایین‌آمدن"""
    c = biquad(noise(0.005, seed), 3800 * pitch, 1.1, "hp") * env_perc(0.005, 0.0016)
    b = biquad(noise(0.028, seed + 7), 1900 * pitch, 2.2, "bp") * env_perc(0.028, 0.009)
    dth = 0.05
    th = sine(150 * pitch, dth) * env_perc(dth, 0.014)
    th = combine(th, biquad(noise(0.02, seed + 13), 520 * pitch, 1.4, "bp") * env_perc(0.02, 0.006) * 0.6)
    x = c * (0.85 * clicky * (1 - 0.6 * soft))
    x = combine(x, b * (0.5 * (1 - 0.35 * soft)))
    x = combine(x, th * (0.55 * (1 - 0.5 * soft)))
    return x * gain


def _release(seed, pitch=1.0, gain=0.3):
    c = biquad(noise(0.004, seed + 31), 5200 * pitch, 1.0, "hp") * env_perc(0.004, 0.0013)
    b = biquad(noise(0.014, seed + 37), 2400 * pitch, 2.5, "bp") * env_perc(0.014, 0.005)
    return combine(c * 0.8, b * 0.5) * gain


def type_key_single():
    add("type_key_single", _key(501, 1.0, 1.0), None, 0.85, width=0.2)


def type_burst_mech():
    d = 2.8
    x = np.zeros(int(SR * d))
    rng = np.random.default_rng(601)
    t = 0.0
    while t < d - 0.15:
        p = float(rng.uniform(0.85, 1.22))
        x = mix_at(x, _key(int(rng.integers(1, 9999)), p, rng.uniform(0.7, 1.0), clicky=1.0), t)
        if rng.random() < 0.75:
            x = mix_at(x, _release(int(rng.integers(1, 9999)), p, rng.uniform(0.15, 0.32)), t + rng.uniform(0.05, 0.10))
        t += rng.uniform(0.075, 0.135)
        if rng.random() < 0.14:          # مکث بین کلمه‌ها
            t += rng.uniform(0.12, 0.3)
    add("type_burst_mech", x, None, 0.85, width=0.4)


def type_burst_soft():
    d = 3.2
    x = np.zeros(int(SR * d))
    rng = np.random.default_rng(701)
    t = 0.0
    while t < d - 0.15:
        p = float(rng.uniform(0.8, 1.1))
        x = mix_at(x, _key(int(rng.integers(1, 9999)), p, rng.uniform(0.5, 0.8), clicky=0.35, soft=1.0), t)
        t += rng.uniform(0.09, 0.16)
        if rng.random() < 0.12:
            t += rng.uniform(0.15, 0.35)
    add("type_burst_soft", x, None, 0.8, width=0.35)


def type_key_roll():
    x = np.zeros(int(SR * 0.5))
    rng = np.random.default_rng(801)
    t = 0.0
    for i in range(7):
        g = 1.0 - i * 0.09
        x = mix_at(x, _key(int(rng.integers(1, 9999)), float(rng.uniform(0.95, 1.3)), g), t)
        t += rng.uniform(0.032, 0.055)
    add("type_key_roll", x, None, 0.85, width=0.45)


def type_enter():
    x = _key(901, 0.62, 1.25, clicky=0.8)
    x = combine(x, sine(95, 0.09) * env_perc(0.09, 0.028) * 0.7)
    x = mix_at(x, _key(902, 0.7, 0.5, clicky=0.5), 0.055)   # برخورد دومِ کلید بزرگ
    add("type_enter", x, None, 0.88, width=0.25)


def type_backspace():
    x = _key(951, 1.18, 1.0, clicky=0.9)
    x = combine(x, biquad(noise(0.02, 952), 900, 1.2, "bp") * env_perc(0.02, 0.007) * 0.35)
    add("type_backspace", x, None, 0.85, width=0.2)


def terminal_bell():
    d = 1.0
    x = bell(2093.0, d, 1.0, vib=0.0) * env_ad(d, 0.002, curve=4.0)
    x = combine(x, bell(2093.0 * 2.76, 0.5, 1.0) * env_ad(0.5, 0.002, curve=5.0) * 0.25)
    x = mix_at(x, biquad(noise(0.006, 961), 5000, 1.0, "hp") * env_perc(0.006, 0.002) * 0.3, 0.0)
    add("terminal_bell", reverb(x, 1.2, 0.18), None, 0.8, width=0.3)


def prompt_tick():
    d = 0.05
    x = biquad(noise(d, 971), 3000, 2.4, "bp") * env_perc(d, 0.004)
    x = combine(x, sine(1650, d) * env_perc(d, 0.003) * 0.3)
    add("prompt_tick", x, None, 0.6)


def scroll_ratchet():
    d = 0.5
    x = np.zeros(int(SR * d))
    rng = np.random.default_rng(981)
    t = 0.0
    i = 0
    while t < d - 0.02:
        e = np.sin(np.pi * min(1.0, t / d)) ** 0.8
        tick = biquad(noise(0.004, 990 + i), 2800 * rng.uniform(0.9, 1.1), 2.0, "bp") * env_perc(0.004, 0.0015)
        x = mix_at(x, tick * (0.5 + 0.5 * e), t)
        t += rng.uniform(0.024, 0.034)
        i += 1
    add("scroll_ratchet", x, None, 0.7, width=0.3)


TYPING = [type_key_single, type_burst_mech, type_burst_soft, type_key_roll,
          type_enter, type_backspace, terminal_bell, prompt_tick, scroll_ratchet]
EXTRA = EXTRA + TYPING


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


