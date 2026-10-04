#!/usr/bin/env python3
"""Synthesises the 'galactic battle' score (numpy) and the deep voice-over (espeak-ng), mixed with ffmpeg."""
import numpy as np, wave, subprocess, math
SR, DUR = 44100, 19.0
N = int(SR * DUR); rng = np.random.default_rng(3)
t = np.arange(N) / SR
BPM = 150; beat = 60 / BPM
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def env(n, a=0.005, d=0.1):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.arange(n) / SR / d); return e
def saw(f, n, det=(0, )):
    tt = np.arange(n) / SR; o = np.zeros(n)
    for c in det: o += 2 * ((tt * f * 2 ** (c / 1200)) % 1) - 1
    return o / len(det)
def add(buf, x, t0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    x = x[:N - i]; l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    buf[0, i:i + len(x)] += x * l; buf[1, i:i + len(x)] += x * r
def lp(x, k):                      # simple one-pole low-pass
    a = 1 / k; y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s += a * (x[i] - s); y[i] = s
    return y
m = np.zeros((2, N))
D = 38  # D2
# bass ostinato: 8ths in D minor, 4 bars patterns
pat = [0, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, 0, 7, 5, 3, 0]
nb = int(DUR / (beat / 2))
for i in range(nb):
    tt = i * beat / 2
    if tt < 0.9: continue
    f = hz(D + 12 + pat[i % 16] ) ; n = int(beat / 2 * 0.9 * SR)
    add(m, 0.30 * lp(saw(f, n, (-6, 6)), 6) * env(n, 0.004, 0.16), tt)
# 16th string/arp pulse (D minor)
arp = [62, 69, 65, 69, 62, 69, 67, 69]
for i in range(int(DUR / (beat / 4))):
    tt = i * beat / 4
    if tt < 2.4 or (6.0 < tt < 6.2): continue
    n = int(beat / 4 * 0.8 * SR); g = 0.10 if tt < 14.2 else 0.13
    add(m, g * lp(saw(hz(arp[i % 8] + 12), n, (-8, 8)), 4) * env(n, 0.002, 0.09), tt, pan=0.5 * math.sin(i * 0.7))
# brass heroic motif (original), two statements
mot = [(62, 1), (69, 1), (74, .5), (72, .5), (69, 1), (65, 1), (67, .5), (69, .5), (70, 1), (69, 2)]
def play(mot, t0, g):
    tt = t0
    for p, d in mot:
        n = int(d * beat * SR * 1.02); vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * np.arange(n) / SR)
        ph = 2 * np.pi * np.cumsum(hz(p) * vib) / SR
        x = (np.sign(np.sin(ph)) * 0.5 + (2 * ((ph / 2 / np.pi) % 1) - 1)) * 0.5
        add(m, g * lp(x, 3) * env(n, 0.03, 0.9), tt); tt += d * beat
play(mot, T0 := 2.4, 0.5); play(mot, 6.2, 0.45)
play([(74, 1), (77, 1), (81, 1), (79, .5), (77, .5), (74, 2), (74, 1), (77, 1), (81, 2)], 10.2, 0.45)
play([(62, .5), (69, .5), (74, 1), (74, 2)], 14.2, 0.55)
# pads / drone
for f in (hz(26), hz(33), hz(38)):
    d = lp(saw(f, N, (-10, 0, 10)), 12) * 0.25
    d *= np.minimum(1, t / 1.0) * np.minimum(1, (DUR - t) / 1.2); m[0] += d; m[1] += d
# taiko / timpani
def hit(t0, g=1.0, f0=95):
    n = int(0.6 * SR); tt = np.arange(n) / SR
    k = np.sin(2 * np.pi * (f0 * 0.55 + f0 * 0.45 * np.exp(-tt * 18)) * tt) * np.exp(-tt * 6)
    k += 0.35 * rng.standard_normal(n) * np.exp(-tt * 40); add(m, g * 0.9 * k, t0)
for i in range(int(DUR / beat)):
    tt = i * beat
    hit(tt, 1.0 if i % 4 == 0 else 0.55 if i % 2 == 0 else 0.0) if tt > 0.3 else None
    if tt > 2.4 and i % 4 in (1, 3):                               # snare-like noise
        n = int(0.16 * SR); x = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / 0.05); add(m, 0.28 * (x - lp(x, 20)), tt)
    if tt > 2.4: hit(tt + beat * 0.75, 0.35, 120)
# big impacts + risers
def boom(t0, g=1.2):
    n = int(2.0 * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * 42 * tt) * np.exp(-tt * 2.2) + 0.5 * lp(rng.standard_normal(n), 30) * np.exp(-tt * 3)
    add(m, g * 0.8 * x, t0)
for tb in (0.0, 2.4, 6.2, 14.2): boom(tb)
def riser(t0, t1):
    n = int((t1 - t0) * SR); ramp = np.linspace(0, 1, n) ** 2
    x = rng.standard_normal(n); x = x - lp(x, 6); add(m, 0.5 * x * ramp, t0)
    ph = 2 * np.pi * np.cumsum(200 + 1800 * np.linspace(0, 1, n) ** 2) / SR; add(m, 0.12 * np.sin(ph) * ramp, t0)
riser(0.8, 2.4); riser(12.6, 14.2)
# lasers
def laser(t0, pan):
    n = int(0.3 * SR); f = 2200 * np.exp(-np.linspace(0, 1, n) * 2.2)
    add(m, 0.14 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-np.arange(n) / SR / 0.15), t0, pan)
for k, tl in enumerate([3.6, 4.3, 4.5, 5.1, 7.4, 9.0, 9.2, 9.7, 11.1, 11.5, 12.1, 12.3, 15.8, 16.3, 17.0, 17.2, 18.0]):
    laser(tl, [-0.8, 0.8, -0.4, 0.5][k % 4])
m /= np.max(np.abs(m)); m *= 0.9
def wr(path, a):
    with wave.open(path, 'wb') as w:
        w.setnchannels(a.shape[0]); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(a.T, -1, 1) * 32767).astype('<i2').tobytes())
wr('music.wav', m)

# ---- voice-over (deep): (start time, text, espeak speed)
SLOT = [1.9, 3.2, 1.8, 1.9, 1.8, 1.9, 4.2]
VO = [(0.35, "Lego mindset.", 120), (2.9, "Build your own galactic adventure.", 135),
      (6.35, "Mandalorian scenes.", 125), (8.35, "Open it. Steer it. Fire it.", 135),
      (10.35, "Build a scrap market.", 130), (12.35, "A gift for fans, fourteen plus.", 135),
      (14.75, "Worth it? Link in description. Like and subscribe.", 140)]
inputs, fl, outs = [], [], []
for i, (t0, txt, sp) in enumerate(VO):
    subprocess.run(['espeak-ng', '-v', 'en-us+m3', '-p', '5', '-s', str(sp+30), '-g', '1', '-w', f'vo{i}.wav', txt], check=True)
    d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'vo{i}.wav']))
    print(i, txt, 'start', t0, 'end~', round(t0 + d*1.25/min(2.0, max(1.25, d*1.25/SLOT[i])), 2))
    inputs += ['-i', f'vo{i}.wav']
    # deepen: pitch down ~ -4 semitones keeping tempo, bass boost, little reverb
    fl.append(f"[{i+2}:a]aresample=44100,asetrate=44100*0.80,aresample=44100,atempo={min(2.0, max(1.25, d*1.25/SLOT[i])):.3f},"
              f"equalizer=f=120:t=q:w=1:g=8,lowpass=f=4500,aecho=0.8:0.6:45|90:0.3|0.2,volume=3.0,adelay={int(t0*1000)}|{int(t0*1000)}[v{i}]")
    outs.append(f"[v{i}]")
fg = ";".join(fl) + f";{''.join(outs)}amix=inputs={len(VO)}:normalize=0,apad=whole_dur=19[vo];" \
     "[vo]asplit[vo1][vo2];[0:a][vo1]sidechaincompress=threshold=0.02:ratio=8:attack=5:release=300[md];" \
     "[md][vo2]amix=inputs=2:normalize=0,alimiter=limit=0.92,atrim=0:19,afade=t=out:st=18.2:d=0.8[a]"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'music.wav', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', *inputs,
                '-filter_complex', fg, '-map', '[a]', '-ac', '2', '-c:a', 'pcm_s16le', 'audio_mix.wav'], check=True)
print('ok')
