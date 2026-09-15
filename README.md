# 🔊 Code-Synthesized SFX & BGM Library for Content Creators

**40 sound effects + 9 background music tracks — generated entirely from code (DSP synthesis). Zero samples, zero copyright risk, zero Content ID claims.**

Built for tech & educational creators on YouTube and Instagram, and shipped with a full Persian guide on *exactly where to place every sound in your timeline*.

> 🇮🇷 راهنمای کامل فارسی: **[START-HERE.fa.md](START-HERE.fa.md)** · نسخه‌ی بصری: [`guides/guide.html`](guides/guide.html)

![license](https://img.shields.io/badge/license-CC0--1.0-blue) ![files](https://img.shields.io/badge/audio-49%20files-green) ![format](https://img.shields.io/badge/format-WAV%20%2B%20MP3-orange) ![claims](https://img.shields.io/badge/Content%20ID%20claims-0-brightgreen)

---

## Why this library is different

Almost every "free SFX pack" out there is a **re-collection** of sounds scraped from other libraries — which is exactly how copyright claims sneak into monetized videos.

This one contains **no recordings at all**. Every waveform is computed from scratch with Python/NumPy:

| Technique | Used for |
|---|---|
| Filtered pink noise + swept low-pass | whooshes, risers, swipes, ambience |
| Inharmonic bell synthesis | dings, chimes, sparkles, logo sting |
| Karplus–Strong | plucks, marimba, lo-fi piano |
| Detuned oscillator pads + sidechain pump | background music beds |
| FFT convolution with synthesized noise IR | reverb (no impulse responses from anywhere) |

**Result:** you can use it in monetized videos, client work, ads, even register `logo_sting` as your own sonic brand — no attribution, no license file to keep, no risk of a library changing its terms two years later.

---

## ▶ Listen

https://github.com/RezaParsian/free-sfx-bgm-pack/blob/master/audio-pack/mp3/sfx/whoosh_transition.mp3
https://github.com/RezaParsian/free-sfx-bgm-pack/blob/master/audio-pack/mp3/sfx/type_burst_mech.mp3
https://github.com/RezaParsian/free-sfx-bgm-pack/blob/master/audio-pack/mp3/sfx/impact_deep.mp3
https://github.com/RezaParsian/free-sfx-bgm-pack/blob/master/audio-pack/mp3/sfx/type_enter.mp3
https://github.com/RezaParsian/free-sfx-bgm-pack/blob/master/audio-pack/mp3/bgm/bgm_terminal_flow.mp3
https://github.com/RezaParsian/free-sfx-bgm-pack/blob/master/audio-pack/mp3/bgm/bgm_tech_explainer.mp3

*(GitHub renders any `.mp3` link in a README as an inline player.)*

---

## What's inside

```
audio-pack/
├── sfx/            40 sound effects — WAV (stereo, 44.1 kHz, master quality)
├── bgm/            9 music tracks — WAV
├── mp3/sfx/        same effects as MP3 (mobile / CapCut friendly)
├── mp3/bgm/        same tracks as MP3 (192 kbps)
└── measured.csv    measured duration + integrated loudness of every file

guides/
├── guide.html      visual, printable guide (Persian)
├── README.md       full text guide (Persian)
└── audio-library.xlsx  filterable table: effects, music, sources, timeline, checklist

sfx-lab/            the generator — every file is reproducible from source

social-preview.png  1280×640 GitHub social preview (upload via repo Settings → Social preview)
repo-icon.png       512×512 matching square icon (profile / org avatar, favicon)
```

### Sound effects (31)

| Category | Files |
|---|---|
| **Transitions & cuts** | `whoosh_transition` `whoosh_short` `cut_tick` `riser_tension` `rewind_sweep` |
| **UI & software** | `ui_click` `ui_double_click` `ui_hover_soft` `typing_keyboard` `text_reveal_soft` `swipe_paper` `camera_shutter` |
| **Alerts & feedback** | `notification_ding` `success_chime` `error_buzz` `coin_ping` `sparkle_magic` |
| **Impacts & emphasis** | `impact_deep` `impact_bright` `boom_cinematic` `pop_bubble` `gong_section` `heartbeat_tension` |
| **Creator tools** | `countdown_beeps` `countdown_tick_single` `air_horn_meme` `vinyl_stop` `laser_pew` `logo_sting` |
| **Typing & terminal** | `type_key_single` `type_burst_mech` `type_burst_soft` `type_key_roll` `type_enter` `type_backspace` `terminal_bell` `prompt_tick` `scroll_ratchet` |
| **Ambience (loopable)** | `room_tone_loop` `vinyl_crackle_loop` |

### Background music (8)

| Track | BPM | Best for |
|---|---|---|
| `bgm_hook_loop_8s` | 124 | First 3 seconds of a Reel / Short (seamless loop) |
| `bgm_tech_explainer` | 118 | Default bed for product reviews & tech explainers |
| `bgm_upbeat_vlog` | 112 | Intros, vlogs, unboxings |
| `bgm_playful_marimba` | 104 | Tips, bloopers, "common mistakes" |
| `bgm_cinematic_tension` | 80 | Durability tests, "here's the problem" |
| `bgm_lofi_focus` | 74 | Long tutorials, coding, study-with-me |
| `bgm_terminal_flow` | 92 | Live coding, typing timelapses, long Linux terminal sessions |
| `bgm_screen_bed` | 60 | Under screen recordings — nothing to fight your voice |
| `bgm_ambient_underscore` | 60 | Concepts, diagrams, slides |

---

## The 6 effects that do 80% of the work

| Effect | Where | Level |
|---|---|---|
| `whoosh_transition` | Every section change — place it **3–5 frames before** the cut | −8 dB |
| `cut_tick` | Every simple cut and slide change | −14 dB |
| `ui_click` | Every click in a screen recording, frame-exact | −12 dB |
| `notification_ding` | Every "important tip" | −12 dB |
| `impact_deep` | The frame where the benchmark number / headline lands | −8 dB |
| `riser_tension` | Start it **2.6 s before** the payoff moment | −10 dB |

### Loudness reference

| Element | Level |
|---|---|
| Your voice | 0 dB (reference) |
| Music under voice | −20 to −16 dB |
| Emphasis SFX | −8 to −6 dB |
| UI SFX | −14 to −10 dB |
| Room tone / ambience | −34 to −28 dB |
| **Final master** | **−14 LUFS**, true peak ≤ **−1 dBTP** |

All files ship pre-normalized (SFX → −18 LUFS, music → −20 LUFS), so dropping them on a timeline untouched already gives you correct **relative** balance.

---

## Rebuild everything from source

```bash
pip install -r requirements.txt

cd sfx-lab
OUTDIR=../audio-pack/sfx  python3 build_sfx_extra.py   # all 40 effects
OUTDIR=../audio-pack/bgm  python3 build_bgm.py         # all 9 tracks
PACKDIR=../audio-pack     python3 encode_mp3.py        # MP3 + loudnorm + LUFS report
OUTFILE=../guides/guide.html python3 build_html.py     # regenerate the HTML guide
OUTDIR=../guides/audio-library.xlsx python3 build_xlsx.py
```

**Branding:** `social-preview.png` and `repo-icon.png` are generated, not hand-drawn — the spectrum bars are the real FFT of `bgm_tech_explainer`, and the bottom ribbon is the real waveform envelope of `bgm_hook_loop_8s`. Regenerate with your own handle/title:

```bash
TITLE1="synthsfx" TITLE2="SFX & BGM Library" HANDLE="github.com/YOU/synthsfx" \
  python3 sfx-lab/make_social_preview.py
ASSETS=assets python3 sfx-lab/make_square_icon.py
```

Dependencies: `numpy`, `scipy`, `openpyxl`, `imageio-ffmpeg`. `ffmpeg` is used for MP3 encoding and loudness measurement — if you already have it on your PATH, edit `FF` in `encode_mp3.py`.

**Knobs worth turning:**

- `audio_engine.py` → oscillators, filters, Karplus–Strong, bell, reverb, sidechain
- `build_sfx.py` / `build_sfx_extra.py` → `peak` (loudness), `d` (length), `width` (stereo), `pan`
- `build_bgm.py` → `bpm`, `bars`, `prog` (chord progression), `master_lp`

> 💡 Set `master_lp=4500` in any music track to darken it — that carves out the 1–4 kHz band where the human voice lives.

---

## Note on repository size

The WAV masters are ~62 MB and are excluded by `.gitignore` by default; only the MP3s (~7 MB) are committed. They are fully reproducible with one command. If you'd rather ship the WAVs too, comment out those two lines in `.gitignore` — a single commit lands around 70 MB, which is fine for GitHub (the hard limit is 100 MB *per file*, largest here is 8 MB). Avoid committing regenerated WAVs repeatedly, since every rewrite adds another full copy to git history.

---

## License

Audio assets: **CC0 1.0** — public domain, use however you like, attribution not required.
Source code: **MIT**.

See [LICENSE](LICENSE).
