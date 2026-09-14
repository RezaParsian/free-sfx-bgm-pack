"""
build_sfx.py — ساخت کتابخانه‌ی افکت صوتی اورجینال
خروجی: /home/user/sfx-lab/out/sfx/*.wav
"""
import os, numpy as np
from audio_engine import *

OUT = os.environ.get("OUTDIR", "audio-pack")
os.makedirs(OUT, exist_ok=True)
REG = {}


def add(name, mono, pan=None, peak=0.89, width=0.0):
    x = normalize(np.asarray(mono, dtype=float), peak)
    x = fade(x)
    st = to_stereo(x, pan)
    if width:
        st = stereo_width(st, width)
    m = float(np.max(np.abs(st)))
    if m > 1e-9:
        st = st * (peak / m)
    REG[name] = st


def combine(a, b):
    """جمع دو سیگنال با طول متفاوت (بدون خطا)"""
    n = max(len(a), len(b))
    out = np.zeros(n)
    out[:len(a)] += a
    out[:len(b)] += b
    return out


def mix_at(base, sig, at_sec):
    i = int(at_sec * SR)
    if i + len(sig) > len(base):
        base = np.concatenate([base, np.zeros(i + len(sig) - len(base))])
    base[i:i + len(sig)] += sig
    return base


def reverb(x, decay=1.4, mix=0.22, seed=7):
    """ریورب مصنوعی (IR نویزی با پوش نمایی) — بدون هیچ فایل خارجی"""
    n = int(SR * decay)
    ir = noise(n / SR, seed) * np.exp(-np.linspace(0, 6.5, n))
    ir = biquad(ir, 6500, 0.7, "lp")
    ir[0] = 1.0
    ir = ir / np.max(np.abs(ir))
    wet = fft_convolve(x, ir)[: len(x)]
    return (1 - mix) * x + mix * normalize(wet, np.max(np.abs(x)) + 1e-9)


# ───────────────── ۱) ترنزیشن و کات ─────────────────
def whoosh_transition():
    d = 0.95
    n = pink(d, 11)
    half = int(0.62 * len(n))
    lp = np.concatenate([
        lp_sweep(n[:half], 200, 6000, 0.9, 40),
        lp_sweep(n[half:], 6000, 260, 0.9, 30)])
    e = np.concatenate([
        np.linspace(0, 1, half) ** 1.6,
        np.exp(-np.linspace(0, 3.2, len(n) - half))])
    body = lp * e * 1.15
    air = biquad(noise(d, 3), 5000, 0.6, "hp") * e * 0.16
    t = np.linspace(0, d, len(n))
    pan = np.sin(np.pi * np.clip((t - 0.05) / 0.8, 0, 1)) * 0.85
    add("whoosh_transition", body + air, pan, 0.9, width=0.5)


def whoosh_short():
    d = 0.42
    n = pink(d, 21)
    lp = lp_sweep(n, 700, 5200, 1.1, 24)
    e = np.exp(-np.linspace(0, 1, len(n)) * 4.5) * np.minimum(1, np.linspace(0, 1, len(n)) * 12)
    t = np.linspace(0, d, len(n))
    pan = 0.8 - 1.6 * t / d
    add("whoosh_short", lp * e * 1.2 + biquad(n, 6000, .6, "hp") * e * .2, pan, 0.88, width=0.4)


def cut_tick():
    d = 0.09
    x = biquad(noise(d, 5), 3000, 1.4, "bp") * env_perc(d, 0.012)
    x += sine(1900, d) * env_perc(d, 0.008) * 0.25
    add("cut_tick", x, None, 0.8, width=0.2)


def riser_tension():
    d = 2.6
    n = pink(d, 31)
    e = np.linspace(0, 1, len(n)) ** 2.2
    bp = lp_sweep(n, 220, 9000, 1.2, 60) * e
    tone = sweep(110, 1500, d) * e * 0.5
    tone += sweep(110.7, 1512, d) * e * 0.35
    sh = (noise(d, 9) * e ** 3) * 0.08
    out = bp * 1.1 + tone + sh
    add("riser_tension", reverb(out, 1.8, 0.18), None, 0.85, width=0.7)


# ───────────────── ۲) UI و کلیک ─────────────────
def ui_click():
    d = 0.07
    x = biquad(noise(d, 1), 2400, 2.2, "bp") * env_perc(d, 0.008) * 1.0
    x += sine(1450, d) * env_perc(d, 0.006) * 0.35
    x += sine(220, d) * env_perc(d, 0.01) * 0.15
    add("ui_click", x * 1.6, None, 0.88, width=0.15)


def ui_double():
    d = 0.2
    x = np.zeros(int(SR * d))
    a = biquad(noise(0.05, 2), 2600, 2.0, "bp") * env_perc(0.05, 0.007)
    b = biquad(noise(0.05, 4), 1900, 2.0, "bp") * env_perc(0.05, 0.009)
    x = mix_at(x, a, 0.0)
    x = mix_at(x, b, 0.075)
    add("ui_double_click", x, None, 0.85)


def typing_burst():
    d = 1.5
    x = np.zeros(int(SR * d))
    rng = np.random.default_rng(17)
    t = 0.0
    while t < 1.25:
        seg = 0.022
        c = biquad(noise(seg, rng.integers(1, 999)), rng.uniform(1700, 3200), 3.0, "bp")
        c *= env_perc(seg, 0.005) * rng.uniform(0.5, 1.0)
        x = mix_at(x, c, t)
        x = mix_at(x, c * 0.25, t + 0.004)
        t += rng.uniform(0.055, 0.115)
    add("typing_keyboard", x * 0.85, None, 0.8, width=0.35)


def mouse_hover():
    d = 0.05
    x = biquad(noise(d, 8), 4200, 3.0, "bp") * env_perc(d, 0.004) * 0.7
    add("ui_hover_soft", x, None, 0.6)


# ───────────────── ۳) اعلان، موفقیت، خطا ─────────────────
def notification():
    d = 0.85
    x = np.zeros(int(SR * d))
    a = bell(1318.5, 0.55, 1.0) * env_ad(0.55, 0.003, curve=4.2)
    b = bell(1760.0, 0.62, 0.95) * env_ad(0.62, 0.003, curve=4.0)
    x = mix_at(x, a, 0.0)
    x = mix_at(x, b, 0.115)
    add("notification_ding", reverb(x, 1.1, 0.16), None, 0.85, width=0.3)


def success_chime():
    d = 1.5
    x = np.zeros(int(SR * d))
    for i, f in enumerate([783.99, 1046.5, 1318.5]):
        dd = 0.95 - i * 0.05
        s = bell(f, dd, 1.0, vib=0.4) * env_ad(dd, 0.004, curve=3.4)
        k = karplus(f * 2, 0.35, 0.994, seed=40 + i, brightness=0.8) * 0.18
        s = mix_at(s, k, 0.0)
        x = mix_at(x, s * (0.95 - i * 0.06), i * 0.105)
    x = mix_at(x, bell(1567.98, 0.7, 1.0) * env_ad(0.7, 0.004, curve=3.8) * 0.35, 0.315)
    add("success_chime", reverb(x, 1.6, 0.2), None, 0.85, width=0.45)


def error_buzz():
    d = 0.42
    t = t_axis(d)
    x = square(103, d) * 0.6 + square(107.3, d) * 0.5
    x = biquad(x, 950, 0.9, "lp")
    x *= (0.75 + 0.25 * np.sin(2 * np.pi * 42 * t))
    x = x * env_ad(d, 0.004, curve=6.5)
    click = biquad(noise(0.02, 6), 1200, 1.0, "hp") * env_perc(0.02, 0.004) * 0.5
    x = mix_at(x, click, 0.0)
    add("error_buzz", x, None, 0.82)


def coin_ping():
    d = 0.7
    x = bell(1864, 0.42, 1.0) * env_ad(0.42, 0.002, curve=5.0)  # noqa
    x = mix_at(x, bell(2489, 0.5, 0.95) * env_ad(0.5, 0.002, curve=4.2) * 0.8, 0.055)
    add("coin_ping", reverb(x, 0.9, 0.14), None, 0.8)


# ───────────────── ۴) ضربه و تاکید ─────────────────
def impact_deep():
    d = 1.6
    n = int(SR * d)
    sub = sweep(150, 42, d) * np.exp(-np.linspace(0, 1, n) * 3.4)
    crack = biquad(noise(0.05, 12), 2500, 0.8, "hp") * env_perc(0.05, 0.012) * 0.75
    body = biquad(pink(d, 13), 320, 0.8, "lp") * np.exp(-np.linspace(0, 1, n) * 4.5) * 0.6
    x = combine(sub, body)
    x = mix_at(x, crack, 0.0)
    add("impact_deep", reverb(x, 2.0, 0.25), None, 0.92, width=0.3)


def impact_bright():
    d = 0.75
    x = bell(2600, 0.55, 1.0) * env_ad(0.55, 0.002, curve=4.5) * 0.75
    sw = sweep(900, 180, 0.35) * np.exp(-np.linspace(0, 1, int(SR * .35)) * 5) * 0.35
    x = combine(x, sw)
    x = mix_at(x, biquad(noise(0.03, 14), 3500, .7, "hp") * env_perc(.03, .008) * .6, 0)
    add("impact_bright", reverb(x, 1.1, 0.18), None, 0.85)


def boom_cinematic():
    d = 3.0
    n = int(SR * d)
    sub = sweep(72, 30, d) * np.exp(-np.linspace(0, 1, n) * 2.2)
    rum = biquad(pink(d, 19), 160, 0.7, "lp") * np.exp(-np.linspace(0, 1, n) * 2.0) * 0.5
    hit = biquad(noise(0.08, 20), 1800, .8, "hp") * env_perc(.08, .02) * .5
    x = sub + rum
    x = mix_at(x, hit, 0.0)
    add("boom_cinematic", reverb(x, 2.6, 0.3), None, 0.92, width=0.5)


def pop_bubble():
    d = 0.13
    t = t_axis(d)
    x = sine(380, d) * np.exp(-t * 55) * 0.9
    x += sine(760, d) * np.exp(-t * 70) * 0.25
    x = mix_at(x, biquad(noise(0.006, 22), 3000, 1.0, "hp") * env_perc(.006, .002) * .4, 0)
    add("pop_bubble", x, None, 0.85)


def swipe_paper():
    d = 0.3
    n = pink(d, 25)
    x = biquad(n, 2600, 0.9, "bp") * np.concatenate([
        np.linspace(0, 1, int(len(n) * .35)) ** 1.4,
        np.exp(-np.linspace(0, 4, len(n) - int(len(n) * .35)))])
    x = mix_at(x, sine(150, .09) * env_perc(.09, .02) * .18, 0.0)
    add("swipe_paper", x, None, 0.8, width=0.4)


# ───────────────── ۵) ابزارهای تولید محتوا ─────────────────
def camera_shutter():
    d = 0.32
    x = np.zeros(int(SR * d))
    for at, f, g in [(0.0, 3200, 1.0), (0.008, 2200, 0.55), (0.055, 1800, 0.9), (0.063, 1300, 0.5)]:
        s = 0.014 if g > 0.8 else 0.01
        burst = biquad(noise(s, int(f)), f, 1.6, "bp") * env_perc(s, s * .35)
        x = mix_at(x, burst * g, at)
    x = mix_at(x, biquad(noise(.05, 99), 420, .9, "lp") * env_perc(.05, .014) * .5, 0.05)
    add("camera_shutter", x, None, 0.85)


def countdown_beeps():
    d = 2.4
    x = np.zeros(int(SR * d))
    for i in range(4):
        last = (i == 3)
        f = 1320.0 if last else 880.0
        seg = 0.13 if last else 0.05
        b = square(f, seg, .5)
        b = biquad(b, 3200, .8, "lp") * env_ad(seg, .002, curve=5.0)
        x = mix_at(x, b * (1.0 if last else .8), i * 0.6)
    add("countdown_beeps", reverb(x, .6, .1), None, 0.8)


def countdown_tick():
    d = 0.09
    x = square(950, d)
    x = biquad(x, 2600, .8, "lp") * env_ad(d, .001, curve=7)
    add("countdown_tick_single", x, None, 0.75)


def sparkle_magic():
    d = 1.7
    x = np.zeros(int(SR * d))
    rng = np.random.default_rng(77)
    for i in range(9):
        f = float(rng.choice([1046.5, 1318.5, 1568.0, 2093.0, 2637.0, 3136.0]))
        dd = float(rng.uniform(.35, .7))
        s = bell(f, dd, 1.0, vib=.6) * env_ad(dd, .002, curve=5)
        x = mix_at(x, s * rng.uniform(.35, .8), i * rng.uniform(.08, .16))
    x = mix_at(x, biquad(noise(1.2, 5), 8000, .8, "hp") * np.linspace(0, 1, int(SR * 1.2)) ** 3 * .06, 0)
    add("sparkle_magic", reverb(x, 2.0, .3), None, 0.8, width=0.8)


def vinyl_ambience():
    d = 9.0
    x = pink(d, 41) * 0.06
    x = biquad(x, 900, .5, "hp")
    rng = np.random.default_rng(3)
    n = int(SR * d)
    for _ in range(int(d * 7)):
        at = rng.integers(0, n - 400)
        ln = rng.integers(120, 500)
        seg = np.sign(rng.standard_normal(ln)) * rng.uniform(.05, .5)
        e = env_perc(ln / SR, ln / SR * .5)
        seg = seg * np.resize(e, ln)
        x[at:at + ln] += seg * .5
    hum = sine(50, d) * .012 + sine(100, d) * .006
    add("vinyl_crackle_loop", x + hum, None, 0.35, width=0.6)


def rewind_sweep():
    d = 0.75
    n = pink(d, 51)
    e = np.exp(-np.linspace(0, 1, len(n)) * 3.5)[::-1]
    lp = lp_sweep(n[::-1], 5200, 500, 1.0, 30)
    add("rewind_sweep", lp * e * 1.1, None, 0.85, width=0.4)


def laser_pew():
    d = 0.3
    x = sweep(2400, 180, d) * env_ad(d, .001, curve=6)
    x += sweep(1200, 90, d) * env_ad(d, .001, curve=7) * .4
    add("laser_pew", x, None, 0.8)


def heartbeat():
    d = 4.6
    x = np.zeros(int(SR * d))
    for beat in range(4):
        base = beat * 1.05
        for off, amp in [(0.0, 1.0), (0.22, .55)]:
            s = sweep(78, 42, .18) * np.exp(-np.linspace(0, 1, int(SR * .18)) * 6)
            x = mix_at(x, s * amp, base + off)
    add("heartbeat_tension", x, None, 0.85)


def logo_sting():
    d = 1.8
    x = np.zeros(int(SR * d))
    for f, dd, g, at in [(523.25, 1.3, .9, 0.0), (784.0, 1.4, .55, .09), (1046.5, 1.5, .5, .18)]:
        x = mix_at(x, bell(f, dd, 1.0, vib=.3) * env_ad(dd, .005, curve=2.6) * g, at)
    sub = sweep(110, 55, .8) * np.exp(-np.linspace(0, 1, int(SR * .8)) * 3) * .5
    x = mix_at(x, sub, 0.0)
    add("logo_sting", reverb(x, 2.4, .32), None, 0.85, width=0.6)


BUILD = [whoosh_transition, whoosh_short, cut_tick, riser_tension,
         ui_click, ui_double, typing_burst, mouse_hover,
         notification, success_chime, error_buzz, coin_ping,
         impact_deep, impact_bright, boom_cinematic, pop_bubble, swipe_paper,
         camera_shutter, countdown_beeps, countdown_tick, sparkle_magic,
         vinyl_ambience, rewind_sweep, laser_pew, heartbeat, logo_sting]

if __name__ == "__main__":
    import wave, time
    t0 = time.time()
    for fn in BUILD:
        fn()
    for name, st in REG.items():
        path = os.path.join(OUT, name + ".wav")
        data = (np.clip(st, -1, 1) * 32767).astype(np.int16)
        with wave.open(path, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes(data.tobytes())
        print(f"{name:26s} {len(st)/SR:5.2f}s")
    print(f"total {len(REG)} files in {time.time()-t0:.1f}s")
