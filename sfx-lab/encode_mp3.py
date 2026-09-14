import os, subprocess, wave, sys, glob
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.environ["PACKDIR"]

def dur(p):
    w = wave.open(p); return w.getnframes() / w.getframerate()

def enc(src, dst, mode):
    if mode == "loud":
        af = ["-af", "loudnorm=I=-18:TP=-1.5:LRA=11"]
    elif mode == "loudmusic":
        af = ["-af", "loudnorm=I=-20:TP=-1.5:LRA=11"]
    else:
        af = ["-af", "alimiter=limit=0.95:level=false"]
    br = "192k" if "bgm" in src else "160k"
    cmd = [FF, "-hide_banner", "-loglevel", "error", "-y", "-i", src] + af + \
          ["-ar", "44100", "-codec:a", "libmp3lame", "-b:a", br, dst]
    subprocess.run(cmd, check=True)

def lufs(p):
    r = subprocess.run([FF, "-hide_banner", "-i", p, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    out = r.stderr
    idx = out.rfind("Integrated loudness")
    if idx < 0: return None
    for line in out[idx:].splitlines():
        if "I:" in line:
            return line.split("I:")[1].split("LUFS")[0].strip()
    return None

report = []
for kind, mode_long in [("sfx", "loud"), ("bgm", "loudmusic")]:
    for src in sorted(glob.glob(os.path.join(ROOT, kind, "*.wav"))):
        n = os.path.basename(src)[:-4]
        d = dur(src)
        mode = mode_long if d >= 0.8 else "peak"
        dst = os.path.join(ROOT, "mp3", kind, n + ".mp3")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        enc(src, dst, mode)
        L = lufs(dst)
        report.append((kind, n, round(d, 2), mode, L, os.path.getsize(dst)))
        print(f"{kind:4s} {n:28s} {d:6.2f}s  {mode:9s} {str(L):>7s} LUFS  {os.path.getsize(dst)//1024:5d} KB")

with open(os.path.join(ROOT, "measured.csv"), "w") as f:
    f.write("type,name,duration_sec,gain_mode,integrated_lufs,size_bytes\n")
    for r in report:
        f.write(",".join(str(x) for x in r) + "\n")
print("total:", len(report), "files")
