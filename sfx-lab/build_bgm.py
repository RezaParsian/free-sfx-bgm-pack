"""
build_bgm.py — ساخت موسیقی پس‌زمینه‌ی اورجینال و ۱۰۰٪ رایگان (بدون کپی‌رایت)
همه با سنتز ساخته می‌شن → هیچ ادعای Content ID روی ویدیوهات نمی‌شینه.
خروجی: /home/user/sfx-lab/out/bgm/*.wav
"""
import os, numpy as np
from audio_engine import *

OUT = os.environ.get("OUTDIR", "audio-pack")
os.makedirs(OUT, exist_ok=True)


def hz(name):
    N = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5,
         'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
    if name[-1].isdigit():
        octv = int(name[-1]); nm = name[:-1]
    else:
        octv = 4; nm = name
    return 440.0 * 2 ** ((N[nm] + (octv - 4) * 12 - 9) / 12)


# ─────────────── سازها ───────────────
def pluck(f, dur, bright=0.75, damp=0.995, seed=1):
    y = karplus(f, dur, damp, seed, bright)
    e = env_asr(len(y) / SR, 0.003, min(0.08, dur * .3), 1.0)
    return y * np.resize(e, len(y))


def bellnote(f, dur, vib=0.3):
    y = bell(f, dur, 1.0, vib)
    e = env_ad(dur, 0.004, curve=max(1.6, 5.0 * dur))
    return y * np.resize(e, len(y))


def bass_note(f, dur):
    t = t_axis(dur)
    y = np.sin(2 * np.pi * f * t) * 0.8 + np.sin(2 * np.pi * 2 * f * t) * 0.18
    y = y + biquad(saw(f, dur), 320, 0.8, "lp") * 0.10
    e = env_asr(dur, 0.008, min(0.07, dur * .35), 1.0) * np.exp(-np.linspace(0, 1, len(t)) * 0.9)
    return y * e


def pad_chord(freqs, dur, seed=0):
    t = t_axis(dur)
    out = np.zeros_like(t)
    for i, f in enumerate(freqs):
        for det in (-6, 0, 6):
            ff = f * 2 ** (det / 1200)
            ph = 2 * np.pi * ff * t + np.random.default_rng(seed * 7 + i).uniform(0, 6.28)
            out += np.sin(ph) * 0.5 + (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.22
    out = biquad(out, 1500, 0.6, "lp")
    lfo = 0.86 + 0.14 * np.sin(2 * np.pi * 0.23 * t)
    return out * env_asr(dur, dur * 0.30, dur * 0.34, 1.0) * lfo / max(len(freqs), 1)


def click_noise(dur=0.012, freq=2500, seed=3, kind="hp", Q=.8):
    x = biquad(noise(dur, seed), freq, Q, kind)
    return x * env_perc(dur, dur * .35)


def mix_at(base, sig, at_sec=0.0):
    i = int(at_sec * SR)
    n = max(len(base), i + len(sig))
    out = np.zeros(n)
    out[:len(base)] += base
    out[i:i + len(sig)] += sig
    return out


def kick(soft=False):
    d = 0.28 if soft else 0.34
    n = int(SR * d)
    y = sweep(150 if soft else 165, 44, d) * np.exp(-np.linspace(0, 1, n) * (5.0 if soft else 4.2))
    y = mix_at(y, click_noise(.012, 2500, 3) * (.25 if soft else .5), 0.0)
    return y


def snare(dur=0.20, tone=190):
    n = int(SR * dur)
    y = biquad(noise(dur, 5), 1800, .8, "bp") * np.exp(-np.linspace(0, 1, n) * 11)
    y = y + sine(tone, dur) * np.exp(-np.linspace(0, 1, n) * 16) * .35
    y = y + biquad(noise(dur, 6), 7000, .7, "hp") * np.exp(-np.linspace(0, 1, n) * 20) * .25
    return y


def hat(dur=0.06, open_=False):
    d = 0.28 if open_ else dur
    y = biquad(noise(d, 11), 9000, .8, "hp")
    y *= np.exp(-np.linspace(0, 1, len(y)) * (10 if open_ else 45))
    return y


def shaker(dur=0.11):
    y = biquad(noise(dur, 13), 6500, .9, "hp")
    e = np.concatenate([np.linspace(0, 1, int(len(y) * .3)), np.exp(-np.linspace(0, 3, len(y) - int(len(y) * .3)))])
    return y * e * .8


def reverb_bus(x, decay=2.2, mix=0.25, seed=77, damp=6000):
    n = int(SR * decay)
    ir = noise(n / SR, seed) * np.exp(-np.linspace(0, 6.0, n))
    ir = biquad(ir, damp, .7, "lp")
    ir[0] = 1.0
    ir /= np.max(np.abs(ir))
    wet = fft_convolve(x, ir)[: len(x)]
    peak = np.max(np.abs(x)) + 1e-9
    return (1 - mix) * x + mix * wet * (peak / (np.max(np.abs(wet)) + 1e-9)) * .55


def sidechain(total_len, bpm, depth=0.42, attack=0.02):
    """پمپ ریتمیک روی بیت (حس حرفه‌ای موزیک یوتیوب)"""
    spb = 60 / bpm
    n = total_len
    e = np.ones(n)
    k = 0
    while k * spb < n / SR:
        i0 = int(k * spb * SR)
        i1 = min(n, i0 + int(attack * SR))
        if i1 > i0:
            e[i0:i1] = np.minimum(e[i0:i1], depth)
        i2 = min(n, i0 + int(spb * 0.85 * SR))
        if i2 > i1:
            ramp = depth + (1 - depth) * (np.linspace(0, 1, i2 - i1) ** 0.7)
            e[i1:i2] = np.minimum(e[i1:i2], ramp)
        k += 1
    return e


def place(buf, sig, at_sec, gain=1.0):
    i = int(at_sec * SR)
    need = i + len(sig)
    if need > len(buf):
        buf = np.concatenate([buf, np.zeros(need - len(buf))])
    buf[i:need] += sig * gain
    return buf


def render(name, tracks, total, fade_in=0.6, fade_out=2.0, peak=0.78, master_lp=None):
    x = np.zeros(int(SR * (total + 1)))
    for sig, at, g in tracks:
        x = place(x, sig, at, g)
    if master_lp:
        x = biquad(x, master_lp, .7, "lp")
    x = x[: int(SR * total)]
    fi = int(SR * fade_in); fo = int(SR * fade_out)
    x[:fi] *= np.linspace(0, 1, fi) ** 1.5
    x[-fo:] *= np.linspace(1, 0, fo) ** 1.3
    x = normalize(x, peak)
    st = to_stereo(x)
    path = os.path.join(OUT, name + ".wav")
    data = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data.tobytes())
    print(f"{name:28s} {total:6.1f}s")
    return name, total


# ═══════════════ ۱) Tech Explainer (پرانرژی، پیش‌رونده) ═══════════════
def tech_explainer(bars=16, bpm=118, name="bgm_tech_explainer", reverb_mix=.20):
    spb = 60 / bpm; bar = 4 * spb
    total = bars * bar
    prog = [["C4", "E4", "G4"], ["G3", "B3", "D4"], ["A3", "C4", "E4"], ["F3", "A3", "C4"]]
    bass = ["C2", "G2", "A2", "F2"]
    arp = [["C5", "E5", "G5", "E5", "C5", "G5", "E5", "G5"],
           ["B4", "D5", "G5", "D5", "B4", "G5", "D5", "G5"],
           ["A4", "C5", "E5", "C5", "A4", "E5", "C5", "E5"],
           ["F4", "A4", "C5", "A4", "F4", "C5", "A4", "C5"]]
    tr = []
    for b in range(bars):
        t0 = b * bar
        ch = prog[b % 4]
        # پد
        tr.append((pad_chord([hz(f) for f in ch], bar * 1.06, seed=b), t0, 0.30))
        # بیس
        tr.append((bass_note(hz(bass[b % 4]), spb * 0.8), t0, 0.44))
        tr.append((bass_note(hz(bass[b % 4]) * 1.5, spb * 0.6), t0 + 2 * spb, 0.30))
        # آرپژ (از بار ۲)
        if b >= 1:
            step = spb / 2
            for i, nn in enumerate(arp[b % 4]):
                tr.append((pluck(hz(nn), step * 1.6, bright=.7, damp=.994, seed=b * 13 + i),
                           t0 + i * step, 0.26 if i % 2 == 0 else 0.18))
        # درامز (از بار ۱)
        for beat in range(4):
            tb = t0 + beat * spb
            tr.append((kick(), tb, 0.52))
            tr.append((hat(0.045), tb + spb / 2, 0.16))
            if beat in (1, 3):
                tr.append((snare(0.17), tb, 0.26))
            tr.append((shaker(0.09), tb + spb * .25, 0.09))
        # ملودی هوک (بارهای ۴، ۸، ۱۲، ۱۶)
        if b % 4 == 3:
            for i, (nn, off, ln) in enumerate([("E5", 0, .5), ("G5", .5, .5), ("A5", 1, 1.2)]):
                tr.append((bellnote(hz(nn), spb * ln * 1.1, vib=.25), t0 + off * spb + spb, 0.16))
    # میکس + ریورب + سایدچین
    buf = np.zeros(int(SR * total))
    for sig, at, g in tr:
        buf = place(buf, sig, at, g)
    sc = sidechain(len(buf), bpm, depth=.55)
    buf = buf * sc
    buf = reverb_bus(buf, 2.0, reverb_mix)
    return render(name, [(buf, 0, 1.0)], total, fade_in=1.2, fade_out=2.5, peak=.78)


# ═══════════════ ۲) هوک ۸ ثانیه‌ای (لوپ‌شونده برای ریلز) ═══════════════
def hook_loop():
    bpm = 124; spb = 60 / bpm; bars = 4; bar = 4 * spb
    total = bars * bar
    prog = [["A3", "C4", "E4"], ["F3", "A3", "C4"], ["C4", "E4", "G4"], ["G3", "B3", "D4"]]
    bass = ["A2", "F2", "C3", "G2"]
    tr = []
    for b in range(bars):
        t0 = b * bar
        tr.append((pad_chord([hz(f) for f in prog[b]], bar * 1.05, seed=b + 3), t0, .34))
        tr.append((bass_note(hz(bass[b]), spb * .85), t0, .5))
        tr.append((bass_note(hz(bass[b]), spb * .6), t0 + 2 * spb, .34))
        for beat in range(4):
            tb = t0 + beat * spb
            tr.append((kick(), tb, .6))
            tr.append((hat(.04), tb + spb / 2, .2))
            tr.append((shaker(.08), tb + spb * .75, .12))
            if beat in (1, 3):
                tr.append((snare(.15), tb, .3))
        notes = ["A4", "C5", "E5", "G5", "E5", "C5", "A4", "E5"]
        for i, nn in enumerate(notes):
            tr.append((pluck(hz(nn), spb * .9, bright=.85, damp=.993, seed=90 + i), t0 + i * spb / 2, .3))
    buf = np.zeros(int(SR * total))
    for sig, at, g in tr:
        buf = place(buf, sig, at, g)
    buf *= sidechain(len(buf), bpm, depth=.5)
    buf = reverb_bus(buf, 1.5, .18)
    return render("bgm_hook_loop_8s", [(buf, 0, 1.0)], total, fade_in=.05, fade_out=.05, peak=.8)


# ═══════════════ ۳) Lo-fi Focus (آروم، برای توضیح طولانی) ═══════════════
def lofi_focus(bars=12, bpm=74):
    spb = 60 / bpm; bar = 4 * spb; total = bars * bar
    prog = [["D3", "F3", "A3", "C4"], ["G3", "B3", "D4", "F4"],
            ["C4", "E4", "G4", "B4"], ["A3", "C4", "E4", "G4"]]
    bass = ["D2", "G2", "C2", "A2"]
    tr = []
    for b in range(bars):
        t0 = b * bar
        ch = prog[b % 4]
        # پیانوی نرم (کارپلاس با damping زیاد)
        for i, nn in enumerate(ch):
            tr.append((pluck(hz(nn), spb * 3.4, bright=.32, damp=.9985, seed=200 + b * 5 + i), t0, .20 - i * .02))
        tr.append((pad_chord([hz(f) * 2 for f in ch[:3]], bar * 1.1, seed=b), t0, .12))
        # بیس
        tr.append((bass_note(hz(bass[b % 4]), spb * 1.6), t0, .40))
        tr.append((bass_note(hz(bass[b % 4]) * 1.5, spb * 1.0), t0 + spb * 2.5, .22))
        # درامز لوفای (سوئینگ‌دار)
        swing = 0.58
        for beat in range(4):
            tb = t0 + beat * spb
            if beat in (0, 2) or (beat == 3 and b % 4 == 3):
                tr.append((kick(soft=True), tb, .48))
            if beat in (1, 3):
                tr.append((snare(.16, tone=170), tb + (swing - .5) * spb * .4, .20))
            tr.append((hat(.05), tb + spb * swing, .13))
    buf = np.zeros(int(SR * total))
    for sig, at, g in tr:
        buf = place(buf, sig, at, g)
    buf = reverb_bus(buf, 2.6, .30, damp=4200)
    # کرکل وینیل + محدودکردن فرکانس بالا → حال‌وهوای لوفای
    n = len(buf)
    d = n / SR
    crack = pink(d, 41) * .018
    rng = np.random.default_rng(3)
    for _ in range(int(d * 6)):
        at = rng.integers(0, max(1, n - 300)); ln = rng.integers(80, 300)
        seg = np.sign(rng.standard_normal(ln)) * rng.uniform(.02, .25)
        buf[at:at + ln] += seg
    buf = combine_pad(buf, crack)
    return render("bgm_lofi_focus", [(buf, 0, 1.0)], total, fade_in=2.0, fade_out=3.0, peak=.75, master_lp=8200)


def combine_pad(a, b):
    n = min(len(a), len(b))
    out = a.copy()
    out[:n] += b[:n]
    return out


# ═══════════════ ۴) Ambient Underscore (خنثی، زیر اسکرین‌رکوردر) ═══════════════
def ambient_underscore(seconds=48):
    bpm = 60; spb = 1.0; total = seconds
    prog = [["F3", "A3", "C4"], ["D3", "F3", "A3"], ["Bb2", "D3", "F3"], ["C3", "E3", "G3"]]
    tr = []
    seg = 6.0
    k = int(total / seg)
    for i in range(k + 1):
        ch = prog[i % 4]
        tr.append((pad_chord([hz(f) for f in ch], seg * 1.35, seed=50 + i), i * seg, .34))
        tr.append((pad_chord([hz(f) * 2 for f in ch], seg * 1.2, seed=70 + i), i * seg + seg * .5, .12))
        if i % 2 == 0:
            tr.append((bass_note(hz(ch[0]) / 2, seg * .9), i * seg, .22))
        # نُت پیانوی پراکنده
        rng = np.random.default_rng(1000 + i)
        for _ in range(2):
            f = hz(rng.choice(["C5", "F5", "A5", "E5", "D5"]))
            tr.append((bellnote(f, 2.6, vib=.2), i * seg + rng.uniform(.4, seg - 1.6), .075))
    buf = np.zeros(int(SR * total))
    for sig, at, g in tr:
        buf = place(buf, sig, at, g)
    buf = reverb_bus(buf, 3.6, .42, damp=5200)
    return render("bgm_ambient_underscore", [(buf, 0, 1.0)], total, fade_in=3.0, fade_out=4.0, peak=.68, master_lp=9500)


# ═══════════════ ۵) Playful Marimba (بامزه، برای بخش‌های طنز) ═══════════════
def playful_marimba(bars=12, bpm=104):
    spb = 60 / bpm; bar = 4 * spb; total = bars * bar
    scale = ["C4", "D4", "E4", "G4", "A4", "C5", "D5", "E5"]
    prog = [["C4", "E4", "G4"], ["A3", "C4", "E4"], ["F3", "A3", "C4"], ["G3", "B3", "D4"]]
    bass = ["C2", "A2", "F2", "G2"]
    tr = []
    rng = np.random.default_rng(7)
    for b in range(bars):
        t0 = b * bar
        tr.append((pad_chord([hz(f) for f in prog[b % 4]], bar * 1.05, seed=b + 9), t0, .16))
        # ملودی ماریمبا (الگوی جهشی)
        for i in range(8):
            idx = int(rng.integers(0, len(scale))) if i % 3 else (i // 2) % len(scale)
            nn = scale[min(idx, len(scale) - 1)]
            tr.append((pluck(hz(nn), spb * .55, bright=.9, damp=.990, seed=300 + i + b), t0 + i * spb / 2,
                       .30 if i % 2 == 0 else .22))
        tr.append((bass_note(hz(bass[b % 4]), spb * .7), t0, .40))
        tr.append((bass_note(hz(bass[b % 4]) * 1.5, spb * .5), t0 + spb * 2, .22))
        for beat in range(4):
            tb = t0 + beat * spb
            tr.append((kick(soft=True), tb, .42))
            if beat in (1, 3):
                tr.append((snare(.13, tone=230), tb, .18))
            tr.append((hat(.035), tb + spb / 2, .12))
            tr.append((shaker(.07), tb + spb * .25, .08))
        if b % 4 == 3:
            tr.append((bellnote(hz("C6"), 1.1, vib=.4), t0 + bar - spb, .13))
    buf = np.zeros(int(SR * total))
    for sig, at, g in tr:
        buf = place(buf, sig, at, g)
    buf *= sidechain(len(buf), bpm, depth=.72)
    buf = reverb_bus(buf, 1.8, .22)
    return render("bgm_playful_marimba", [(buf, 0, 1.0)], total, fade_in=1.0, fade_out=2.0, peak=.76)


# ═══════════════ ۶) Cinematic Tension (برای مقایسه/هشدار/لحظه‌ی حساس) ═══════════════
def cinematic_tension(bars=10, bpm=80):
    spb = 60 / bpm; bar = 4 * spb; total = bars * bar
    prog = [["A2", "E3", "A3", "C4"], ["F2", "C3", "F3", "G#3"], ["G2", "D3", "G3", "Bb3"], ["E2", "B2", "E3", "G3"]]
    tr = []
    for b in range(bars):
        t0 = b * bar
        ch = prog[b % 4]
        tr.append((pad_chord([hz(f) for f in ch], bar * 1.25, seed=b + 21), t0, .40))
        tr.append((bass_note(hz(ch[0]), spb * 3.4), t0, .46))
        # ضربان قلب‌مانند
        for beat in range(4):
            tr.append((kick(soft=True), t0 + beat * spb, .30 if beat % 2 == 0 else .18))
        # ریزر تدریجی در نیمه‌ی دوم
        if b == bars - 3:
            n = pink(bar * 3, 61)
            e = np.linspace(0, 1, len(n)) ** 2.4
            tr.append((lp_sweep(n, 250, 8000, 1.1, 50) * e, t0, .18))
        if b == bars - 1:
            hit = sweep(150, 42, 1.6) * np.exp(-np.linspace(0, 1, int(SR * 1.6)) * 3.2)
            tr.append((hit, t0, .55))
            tr.append((bellnote(hz("A4"), 2.2, vib=.2), t0, .18))
    buf = np.zeros(int(SR * total))
    for sig, at, g in tr:
        buf = place(buf, sig, at, g)
    buf = reverb_bus(buf, 3.4, .38, damp=4800)
    return render("bgm_cinematic_tension", [(buf, 0, 1.0)], total, fade_in=2.0, fade_out=2.5, peak=.78)




# ═══════════════ ۷) Screen Bed (خیلی خلوت — زیر نریشن/اسکرین‌رکوردر) ═══════════════
def screen_bed(seconds=40):
    """دینامیک پایین، بدون درام، بدون ملودی مزاحم → صداش زیر حرف‌زدن گم نمی‌شه"""
    total = seconds
    seg = 8.0
    prog = [["C3", "E3", "G3"], ["A2", "C3", "E3"], ["F2", "A2", "C3"], ["G2", "B2", "D3"]]
    tr = []
    for i in range(int(total / seg) + 1):
        ch = prog[i % 4]
        tr.append((pad_chord([hz(f) for f in ch], seg * 1.4, seed=300 + i), i * seg, .26))
        tr.append((bass_note(hz(ch[0]), seg * .95), i * seg, .16))
        if i % 2 == 1:
            tr.append((pluck(hz(ch[2]) * 4, 1.4, bright=.35, damp=.9985, seed=400 + i), i * seg + seg * .5, .07))
    buf = np.zeros(int(SR * total))
    for sig, at, g in tr:
        buf = place(buf, sig, at, g)
    buf = reverb_bus(buf, 4.0, .45, damp=3800)
    return render("bgm_screen_bed", [(buf, 0, 1.0)], total, fade_in=3.0, fade_out=4.0, peak=.52, master_lp=7000)


# ═══════════════ ۸) Upbeat Vlog (روشن و مثبت — برای اینترو/بخش‌های پرانرژی) ═══════════════
def upbeat_vlog(bars=12, bpm=112):
    spb = 60 / bpm; bar = 4 * spb; total = bars * bar
    prog = [["G3", "B3", "D4"], ["E3", "G3", "B3"], ["C4", "E4", "G4"], ["D4", "F#4", "A4"]]
    bass = ["G2", "E2", "C3", "D3"]
    lead = [["D5", "G5", "B5", "G5"], ["B4", "E5", "G5", "E5"], ["E5", "G5", "C6", "G5"], ["F#5", "A5", "D6", "A5"]]
    tr = []
    for b in range(bars):
        t0 = b * bar
        tr.append((pad_chord([hz(f) for f in prog[b % 4]], bar * 1.06, seed=b + 40), t0, .22))
        tr.append((bass_note(hz(bass[b % 4]), spb * .8), t0, .44))
        tr.append((bass_note(hz(bass[b % 4]) * 1.5, spb * .55), t0 + spb * 1.5, .26))
        tr.append((bass_note(hz(bass[b % 4]), spb * .7), t0 + spb * 2, .36))
        tr.append((bass_note(hz(bass[b % 4]) * 2, spb * .5), t0 + spb * 3.5, .22))
        for i, nn in enumerate(lead[b % 4]):
            tr.append((pluck(hz(nn), spb * 1.1, bright=.8, damp=.9945, seed=500 + i + b * 4), t0 + i * spb, .24))
        for beat in range(4):
            tb = t0 + beat * spb
            tr.append((kick(), tb, .5))
            tr.append((hat(.05, open_=(beat == 3)), tb + spb / 2, .17 if beat == 3 else .14))
            if beat in (1, 3):
                tr.append((snare(.16), tb, .24))
            tr.append((shaker(.08), tb + spb * .25, .08))
    buf = np.zeros(int(SR * total))
    for sig, at, g in tr:
        buf = place(buf, sig, at, g)
    buf *= sidechain(len(buf), bpm, depth=.6)
    buf = reverb_bus(buf, 1.9, .2)
    return render("bgm_upbeat_vlog", [(buf, 0, 1.0)], total, fade_in=1.0, fade_out=2.5, peak=.78)


BUILD = [tech_explainer, hook_loop, lofi_focus, ambient_underscore, playful_marimba,
         cinematic_tension, screen_bed, upbeat_vlog]

if __name__ == "__main__":
    import time
    t0 = time.time()
    for fn in BUILD:
        fn()
    print(f"done in {time.time()-t0:.1f}s")
