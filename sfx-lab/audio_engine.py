"""
audio_engine.py — موتور سنتز صدا (بدون هیچ نمونه‌ی کپی‌رایت‌دار)
همه‌ی افکت‌ها و موزیک‌ها از صفر با DSP ساخته می‌شن → ۱۰۰٪ اورجینال و قابل استفاده‌ی تجاری.
"""
import numpy as np
from scipy.signal import lfilter, fftconvolve

SR = 44100


# ───────────────────────────── پایه ─────────────────────────────
def t_axis(dur):
    return np.linspace(0, dur, int(SR * dur), endpoint=False)


def sine(freq, dur, phase=0.0):
    return np.sin(2 * np.pi * freq * t_axis(dur) + phase)


def square(freq, dur, duty=0.5):
    ph = (t_axis(dur) * freq) % 1.0
    return np.where(ph < duty, 1.0, -1.0)


def saw(freq, dur):
    return 2.0 * ((t_axis(dur) * freq) % 1.0) - 1.0


def tri(freq, dur):
    return 2.0 * np.abs(saw(freq, dur)) - 1.0


def noise(dur, seed=None):
    rng = np.random.default_rng(seed)
    return rng.standard_normal(int(SR * dur))


def pink(dur, seed=None):
    """نویز صورتی با طیف 1/f (طبیعی‌تر از سفید برای whoosh / ambience)"""
    w = noise(dur, seed)
    n = len(w)
    X = np.fft.rfft(w)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1] if len(f) > 1 else 1.0
    X = X / np.sqrt(f)
    y = np.fft.irfft(X, n)
    m = np.max(np.abs(y))
    return y / m if m > 1e-9 else y


def sweep(f0, f1, dur, curve="exp"):
    """سویپ فرکانس (up = riser / down = impact)"""
    t = t_axis(dur)
    if curve == "exp":
        f = f0 * (f1 / f0) ** (t / dur)
    else:
        f = f0 + (f1 - f0) * (t / dur)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(phase)


def fft_convolve(x, ir):
    n = len(x) + len(ir) - 1
    nfft = int(2 ** np.ceil(np.log2(n)))
    return np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]


def biquad(x, f0, Q=1.0, kind="lp", sr=SR):
    """فیلتر (lp / hp / bp) با scipy — سریع و دقیق"""
    w0 = 2 * np.pi * min(f0, sr * 0.49) / sr
    alpha = np.sin(w0) / (2 * max(Q, 0.01))
    cw = np.cos(w0)
    if kind == "lp":
        b = np.array([(1 - cw) / 2, 1 - cw, (1 - cw) / 2])
    elif kind == "hp":
        b = np.array([(1 + cw) / 2, -(1 + cw), (1 + cw) / 2])
    else:
        b = np.array([alpha, 0.0, -alpha])
    a0 = 1 + alpha
    b = b / a0
    a = np.array([1.0, -2 * cw / a0, (1 - alpha) / a0])
    return lfilter(b, a, np.asarray(x, dtype=float))


def lp_sweep(x, f0, f1, Q=1.0, steps=64):
    """low-pass با فرکانس متغیر (برای whoosh طبیعی)"""
    n = len(x)
    out = np.zeros(n)
    edges = np.linspace(0, n, steps + 1).astype(int)
    for i in range(steps):
        fr = f0 * (f1 / f0) ** (i / max(steps - 1, 1))
        seg = x[edges[i]:edges[i + 1]]
        if len(seg) == 0:
            continue
        y = biquad(seg, max(fr, 40), Q, "lp")
        w = np.hanning(2 * len(seg))[: len(seg)]
        out[edges[i]:edges[i + 1]] += y * w
    return out


def env_ad(dur, attack=0.002, decay=None, curve=6.0):
    """پوش exponential attack/decay"""
    n = int(SR * dur)
    e = np.zeros(n)
    a = max(1, int(SR * attack))
    e[:a] = np.linspace(0, 1, a)
    d = n - a
    if d > 0:
        tt = np.linspace(0, 1, d)
        e[a:] = np.exp(-curve * tt)
    return e


def env_perc(dur, decay=0.05):
    n = int(SR * dur)
    e = np.exp(-np.linspace(0, 1, n) * (dur / decay) * 4)
    e[: max(1, int(SR * 0.0008))] *= np.linspace(0, 1, max(1, int(SR * 0.0008)))
    return e


def env_asr(dur, a=0.05, r=0.15, sustain=1.0):
    n = int(SR * dur)
    e = np.ones(n) * sustain
    ai = min(int(SR * a), n // 2)
    ri = min(int(SR * r), n // 2)
    if ai > 0:
        e[:ai] = np.linspace(0, sustain, ai)
    if ri > 0:
        e[-ri:] = np.linspace(sustain, 0, ri)
    return e


def karplus(freq, dur, damp=0.996, seed=0, brightness=1.0):
    """سنتز Karplus-Strong (زه/مالِت) — برای BGM، سکه و pluck"""
    N = max(2, int(SR / freq))
    rng = np.random.default_rng(seed)
    buf = rng.standard_normal(N)
    if brightness < 1.0:
        for _ in range(max(1, int((1 - brightness) * 8))):
            buf = 0.5 * (buf + np.roll(buf, 1))
    total = int(SR * dur)
    reps = int(np.ceil(total / N))
    x = np.tile(buf, reps)[:total]
    # فیلتر comb با بازخورد → همان حلقه‌ی Karplus ولی برداری
    b = np.zeros(N + 1); b[0] = 1.0; b[N] = damp * 0.5; b[N - 1] = damp * 0.5
    a = np.zeros(N + 1); a[0] = 1.0
    y = lfilter(b, a, x)
    y = y / (np.max(np.abs(y)) + 1e-9)
    return y * np.exp(-np.linspace(0, 1, total) * (1.2 * dur / (dur + 0.6)))


def bell(freq, dur, bright=1.0, vib=0.0):
    """زنگ/دینگ با هارمونیک‌های غیرصحیح (حس فلزی-شیشه‌ای)"""
    t = t_axis(dur)
    parts = [(1.0, 1.0, 4.0), (2.0, 0.55, 3.2), (2.76, 0.32, 2.6),
             (5.4, 0.14, 2.0), (8.9, 0.06, 1.6)]
    out = np.zeros_like(t)
    for ratio, amp, dec in parts:
        f = freq * ratio * bright
        if f > SR * 0.45:
            continue
        ph = 2 * np.pi * f * t
        if vib:
            ph += vib * np.sin(2 * np.pi * 5.5 * t)
        out += amp * np.sin(ph) * np.exp(-dec * t / dur)
    return out / 2.1


def normalize(x, peak=0.89):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 1e-9 else x


def fade(x, fi=0.003, fo=0.015):
    n = len(x)
    a = min(int(SR * fi), n // 2)
    b = min(int(SR * fo), n // 2)
    if a > 0:
        x[:a] *= np.linspace(0, 1, a)
    if b > 0:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def to_stereo(x, pan_curve=None):
    """pan_curve: آرایه‌ی -1..1 هم‌اندازه‌ی x"""
    x = np.asarray(x, dtype=float)
    if x.ndim == 2:
        return x
    if pan_curve is None:
        return np.stack([x, x], axis=1)
    g = np.sqrt(2) / 2
    l = x * g * (1 - np.clip(pan_curve, -1, 1)) ** 0.5 * np.sqrt(2)
    r = x * g * (1 + np.clip(pan_curve, -1, 1)) ** 0.5 * np.sqrt(2)
    return np.stack([l, r], axis=1)


def stereo_width(xst, amount=0.3):
    """پهن‌کردن استریو با سیگنال side"""
    l, r = xst[:, 0], xst[:, 1]
    mid = (l + r) / 2
    side = (l - r) / 2
    side *= (1 + amount)
    return np.stack([mid + side, mid - side], axis=1)
