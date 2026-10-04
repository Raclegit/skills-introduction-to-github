#!/usr/bin/env python3
"""Renders the 9:16 promo frames (numpy/PIL) and pipes them to ffmpeg (H.264)."""
import math, subprocess, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H, FPS, DUR = 1080, 1920, 30, 19.0
OUT = sys.argv[1] if len(sys.argv) > 1 else 'video_noaudio.mp4'
ONLY = [float(x) for x in sys.argv[2:]]          # optional: render only these timestamps as PNG

HOOK = "LEGO MINDSET"                              # hook text (single place to edit)
FB = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
FR_ = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
YEL, CYAN, VIO, WHITE = (255, 232, 31), (110, 200, 255), (190, 130, 255), (255, 255, 255)
random.seed(7); rng = np.random.default_rng(7)

# scene boundaries
T_S2, T_C1, T_S4 = 2.4, 6.2, 14.2
CARD = 2.0

hero = Image.open('hero.png').convert('RGBA')
HW, HH = hero.size

# ---------- helpers
def comp(frame, im, x, y):
    x, y = int(x), int(y)
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(frame.width, x + im.width), min(frame.height, y + im.height)
    if x1 <= x0 or y1 <= y0: return
    frame.alpha_composite(im.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))

def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x):
    x = min(max(x, 0), 1); c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def ease_io(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)

_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

_tc = {}
def text_img(txt, size, fill, bold=True, maxw=980, stroke=7, line_gap=1.08):
    k = (txt, size, fill, bold, maxw)
    if k in _tc: return _tc[k]
    f = font(FB if bold else FR_, size)
    d = ImageDraw.Draw(Image.new('L', (4, 4)))
    words, lines, cur = txt.split(' '), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=f) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w_
    lines.append(cur)
    lh = int(size * line_gap)
    wd = int(max(d.textlength(l, font=f) for l in lines)) + 2 * stroke + 8
    im = Image.new('RGBA', (wd, lh * len(lines) + 2 * stroke + 16), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        x = (wd - d.textlength(l, font=f)) / 2
        dd.text((x + 3, stroke + 3 + i * lh + 5), l, font=f, fill=(0, 0, 0, 170), stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
        dd.text((x, stroke + i * lh + 5), l, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=(5, 8, 25, 255))
    _tc[k] = im
    return im

def put(frame, im, cx, cy, scale=1.0, alpha=1.0, rot=0):
    if scale <= 0.01 or alpha <= 0.01: return
    if abs(scale - 1) > 0.005:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.99:
        a = im.getchannel('A').point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    comp(frame, im, cx - im.width / 2, cy - im.height / 2)

def pop(frame, im, cx, cy, t, t0, alpha=1.0, dur=0.28):
    x = (t - t0) / dur
    if x < 0: return
    put(frame, im, cx, cy, scale=0.4 + 0.6 * ease_back(x), alpha=alpha * min(1, x * 4))

def panel(frame, x0, y0, x1, y1, bar=YEL, a=165):
    lay = Image.new('RGBA', frame.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0, y0, x1, y1), 26, fill=(6, 10, 32, a), outline=bar + (200,), width=3)
    d.rounded_rectangle((x0, y0, x0 + 14, y1), 7, fill=bar + (255,))
    frame.alpha_composite(lay)

# ---------- nebula (blue + violet fields, scrolled and cross-faded)
def fbm(h, w, seed, octs=6):
    r = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp, tot = 1.0, 0
    for o in range(octs):
        n = 2 ** (o + 2)
        g = Image.fromarray((r.random((n, int(n * w / h) + 1)) * 255).astype(np.uint8))
        acc += np.asarray(g.resize((w, h), Image.BICUBIC), np.float32) / 255 * amp; tot += amp; amp *= 0.55
    acc /= tot; acc = (acc - acc.min()) / (acc.max() - acc.min())
    return acc
NW, NH = 1500, 3400
fa, fb_ = fbm(NH, NW, 11), fbm(NH, NW, 29)
fa = np.clip((fa - 0.42) * 2.4, 0, 1) ** 1.4
fb_ = np.clip((fb_ - 0.45) * 2.4, 0, 1) ** 1.4
BLUE = np.array([0.10, 0.35, 1.0], np.float32); VIOL = np.array([0.62, 0.18, 0.95], np.float32)

def background(t, boost=1.0):
    ox = int(200 + 120 * math.sin(t * 0.35)); oy = int(300 + t * 38)
    ox2 = int(260 - 100 * math.cos(t * 0.3)); oy2 = int(800 - t * 30)
    a = fa[oy:oy + H, ox:ox + W]; b = fb_[oy2:oy2 + H, ox2:ox2 + W]
    base = np.array([4, 6, 20], np.float32)
    img = base + 170 * boost * (a[..., None] * BLUE + b[..., None] * VIOL * 0.9)
    # vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 1 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2
    img *= v[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')

# ---------- stars (3D, hyperspace streaks)
NS = 520
sx_ = rng.uniform(-1.6, 1.6, NS); sy_ = rng.uniform(-2.4, 2.4, NS); sz_ = rng.uniform(0.05, 1, NS)
scol = rng.choice(3, NS)
def stars(frame, speed, dt):
    global sz_
    lay = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(lay)
    f = 620; cx, cy = W / 2, H / 2 - 60
    zn = sz_ - speed * dt
    zt = sz_ + speed * 0.045 * (1 if speed > 0.8 else 0.4)     # tail further away -> streak
    for i in range(NS):
        z0, z1 = max(zn[i], 0.015), zt[i]
        x1, y1 = cx + sx_[i] * f / z0, cy + sy_[i] * f / z0
        x0, y0 = cx + sx_[i] * f / z1, cy + sy_[i] * f / z1
        br = min(1, (1 - z0) * 1.3 + 0.15)
        c = [(255, 255, 255), (170, 205, 255), (215, 175, 255)][scol[i]]
        c = tuple(int(v * br) for v in c)
        wdt = 1 + int((1 - z0) * (3 if speed > 0.8 else 2))
        d.line((x0, y0, x1, y1), fill=c, width=wdt)
    sz_ = np.where(zn < 0.02, 1.0, zn)
    reset = zn < 0.02
    sx_[reset] = rng.uniform(-1.6, 1.6, reset.sum()); sy_[reset] = rng.uniform(-2.4, 2.4, reset.sum())
    frame_rgb = ImageChops.add(frame.convert('RGB'), lay)
    return frame_rgb.convert('RGBA')

def speed_at(t):
    s = 0.30
    if t < T_S2: s = 2.4
    elif t < T_S2 + 0.9: s = 0.30 + 2.1 * (1 - ease_io((t - T_S2) / 0.9))
    for k in range(4):                                  # jump between cards
        tc = T_C1 + k * CARD
        if tc <= t < tc + 0.35: s = max(s, 1.8 * (1 - (t - tc) / 0.35))
    if T_S4 <= t < T_S4 + 0.8: s = max(s, 2.4 * (1 - (t - T_S4) / 0.8))
    return s

# ---------- hero (product) rendering
def hero_draw(frame, scale, fx, fy, sxc, syc, angle=0.0, yaw=1.0, alpha=1.0):
    """Draw the cut-out so that normalised point (fx,fy) lands at screen (sxc,syc)."""
    w = max(8, int(HW * scale * yaw)); h = max(8, int(HH * scale))
    im = hero.resize((w, h), Image.BILINEAR)
    rx, ry = fx * w - w / 2, fy * h - h / 2
    th = math.radians(angle)
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
        vx, vy = rx * math.cos(th) + ry * math.sin(th), -rx * math.sin(th) + ry * math.cos(th)
    else: vx, vy = rx, ry
    if alpha < 0.99:
        a = im.getchannel('A').point(lambda v: int(v * alpha)); im.putalpha(a)
    comp(frame, im, sxc - im.width / 2 - vx, syc - im.height / 2 - vy)

_glow = None
def glow(frame, cx, cy, r, col, a):
    global _glow
    if _glow is None:
        yy, xx = np.mgrid[-256:256, -256:256].astype(np.float32)
        _glow = np.clip(1 - np.sqrt(xx ** 2 + yy ** 2) / 256, 0, 1) ** 2
    s = Image.fromarray((_glow * 255 * a).astype(np.uint8)).resize((int(2 * r), int(2 * r)), Image.BILINEAR)
    lay = Image.new('RGBA', s.size, col + (0,)); lay.putalpha(s)
    comp(frame, lay, cx - r, cy - r)

# focal points (normalised in the cut-out): (fx, fy)
F_ALL = (0.50, 0.50); F_BODY = (0.66, 0.42); F_FIG = (0.30, 0.86)
F_PANEL = (0.78, 0.50); F_TENT = (0.78, 0.12)

GB, GV = (40, 110, 255), (160, 60, 240)
AFFIL = "Amazon Affiliate link - no extra cost to you"
LINK1, LINK2 = "https://amzn.eu/d/0bT8Zuqv", "https://geni.us/20Ni4M"

CARDS = [
    ("Scenes from The Mandalorian Season 1", "Scènes de The Mandalorian saison 1",
     "5 minifigures + posable Mudhorn + Grogu with hoverpram", "5 minifigurines + Mudhorn articulé + Grogu avec hoverpram", (0.40, 0.72), 1.5),
    ("Open the side panels, play inside", "Ouvrez les panneaux latéraux et jouez à l'intérieur",
     "Turn dials to steer, open the hatch, fire 2 stud shooters", "Tournez les molettes, ouvrez la trappe, 2 lance-tenons", (0.74, 0.48), 1.6),
    ("Remove the tents: build a scrap market", "Retirez les tentes : créez un marché de ferraille",
     "Help Mando battle the Mudhorn for its egg", "Aidez Mando à affronter le Mudhorn pour son œuf", (0.72, 0.25), 1.6),
    ("The gift for Star Wars fans 14+", "Le cadeau des fans de Star Wars 14+",
     "LEGO Builder app: 3D instructions, zoom & rotate", "App LEGO Builder : instructions 3D, zoom et rotation", F_ALL, 1.15),
]

def flash(frame, a):
    if a > 0.01: frame.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * min(a, 1)))))

def caption(frame, en, fr, t_loc, y, en_size=62, fr_size=44, col=WHITE):
    ti, tf = text_img(en, en_size, col, maxw=900), text_img(fr, fr_size, CYAN, bold=False, maxw=900, stroke=5)
    h = ti.height + tf.height + 36
    panel(frame, 50, y, W - 50, y + h, bar=YEL)
    pop(frame, ti, W / 2 + 10, y + 18 + ti.height / 2, t_loc, 0.0)
    if t_loc > 0.12:
        put(frame, tf, W / 2 + 10, y + 22 + ti.height + tf.height / 2, alpha=min(1, (t_loc - 0.12) * 6))
    return y + h

def footer(frame, t):
    if t >= T_S2:
        put(frame, text_img(AFFIL, 28, (220, 225, 245), bold=False, maxw=1000, stroke=4), W / 2, 1690,
            alpha=min(1, (t - T_S2) / 0.4) * 0.95)

def scene(t):
    frame = background(t, boost=1.25 if t < T_S2 or t >= T_S4 else 1.0)
    return frame

def compose(t, dt):
    frame = background(t, 1.3 if (t < T_S2 or t >= T_S4) else 1.0)
    frame = stars(frame, speed_at(t), dt)
    shake = 0; fl = 0
    # ------------- S1 : hook
    if t < T_S2:
        x = t / T_S2
        sc = 0.05 + 0.80 * ease_out(x * 1.15) ; ang = 540 * (1 - ease_out(x * 1.1)) * -1
        glow(frame, W / 2, 1080, 640 * (0.3 + sc), GB, 0.9)
        hero_draw(frame, 0.88 * sc, 0.5, 0.5, W / 2, 1090, angle=ang, alpha=min(1, t * 5))
        # hook slams in
        k = ease_back((t - 0.15) / 0.3)
        txt = text_img(HOOK, 150, YEL, maxw=980)
        put(frame, txt, W / 2, 360, scale=0.4 + 0.75 * max(k, 0) if t > 0.15 else 0, alpha=min(1, (t - 0.15) * 8))
        if 0.15 < t < 0.45: shake = 14 * (1 - (t - 0.15) / 0.3)
        if t > 1.2:
            put(frame, text_img("LEGO STAR WARS", 56, CYAN, maxw=980), W / 2, 1560, alpha=min(1, (t - 1.2) * 4))
        if t > T_S2 - 0.25: fl = (t - (T_S2 - 0.25)) / 0.25
    # ------------- S2 : reveal + message
    elif t < T_C1:
        tl = t - T_S2
        fl = max(0, 1 - tl / 0.35)
        sway = math.sin(tl * 2.2) * 5
        sc = 0.88 + 0.06 * ease_out(tl / 1.2) + 0.03 * math.sin(tl * 1.5)
        yaw = 1 - 0.07 * (0.5 + 0.5 * math.sin(tl * 2.6))
        glow(frame, W / 2, 1010, 720, GB, 0.8); glow(frame, W / 2 + 140, 1010, 520, GV, 0.5)
        hero_draw(frame, sc, 0.5, 0.5, W / 2, 1010 + 6 * math.sin(tl * 3), angle=sway, yaw=yaw)
        if tl < 0.3: shake = 12 * (1 - tl / 0.3)
        pop(frame, text_img("Build your own galactic adventure", 82, YEL, maxw=960), W / 2, 250, t, T_S2 + 0.25)
        if tl > 0.7:
            put(frame, text_img("Construisez votre propre aventure galactique", 50, CYAN, bold=False, maxw=940, stroke=5), W / 2, 480,
                alpha=min(1, (tl - 0.7) * 5))
        # exact product name
        if tl > 1.2:
            a = min(1, (tl - 1.2) * 5)
            panel(frame, 60, 1330, W - 60, 1590, bar=VIO)
            put(frame, text_img("LEGO Star Wars", 50, YEL, maxw=900), W / 2 + 10, 1385, alpha=a)
            put(frame, text_img("Offworld Sandcrawler and Mudhorn", 46, WHITE, maxw=960), W / 2 + 10, 1465, alpha=a)
            put(frame, text_img("75453", 62, CYAN, maxw=900), W / 2 + 10, 1535, alpha=a)
    # ------------- S3 : feature cards
    elif t < T_S4:
        k = min(3, int((t - T_C1) / CARD)); tl = t - (T_C1 + k * CARD)
        en1, fr1, en2, fr2, foc, zoom = CARDS[k]
        fl = max(0, 0.9 - tl / 0.18) if tl < 0.18 else 0
        if tl < 0.3: shake = 16 * (1 - tl / 0.3)
        # rapid punch zoom then slow push, alternate tilts
        z = 0.50 + (zoom * 0.5 - 0.50) * ease_out(tl / 0.35) + 0.06 * (tl / CARD)
        ang = (-9 if k % 2 == 0 else 9) * (1 - ease_out(tl / 0.5)) + (3 if k % 2 == 0 else -3)
        glow(frame, W / 2, 800, 700, GB if k % 2 == 0 else GV, 0.8)
        hero_draw(frame, z, foc[0], foc[1], W / 2, 700, angle=ang, yaw=1 - 0.05 * math.sin(tl * 4))
        yb = caption(frame, en1, fr1, tl, 1170, en_size=58, fr_size=40)
        if tl > 0.45:
            al = min(1, (tl - 0.45) * 6)
            t1, t2 = text_img(en2, 38, WHITE, maxw=900, stroke=5), text_img(fr2, 32, CYAN, bold=False, maxw=900, stroke=4)
            h2 = t1.height + t2.height + 30
            panel(frame, 50, yb + 20, W - 50, yb + 20 + h2, bar=CYAN, a=150)
            put(frame, t1, W / 2 + 10, yb + 32 + t1.height / 2, alpha=al)
            put(frame, t2, W / 2 + 10, yb + 34 + t1.height + t2.height / 2, alpha=al)
        # progress ticks
        for j in range(4):
            d = ImageDraw.Draw(frame); c = YEL + (255,) if j <= k else (255, 255, 255, 70)
            d.rounded_rectangle((W / 2 - 150 + j * 78, 120, W / 2 - 150 + j * 78 + 64, 130), 5, fill=c)
    # ------------- S4 : CTA
    else:
        tl = t - T_S4
        fl = max(0, 1 - tl / 0.3)
        if tl < 0.3: shake = 14 * (1 - tl / 0.3)
        glow(frame, W / 2, 620, 560, GB, 0.7)
        hero_draw(frame, 0.62 + 0.03 * math.sin(tl * 3), 0.5, 0.5, W / 2, 560 + 5 * math.sin(tl * 2.4),
                  angle=math.sin(tl * 1.7) * 4)
        pulse = 1 + 0.05 * math.sin(tl * 9)
        k = ease_back(tl / 0.3)
        put(frame, text_img("WORTH IT?", 150, YEL, maxw=980), W / 2, 960, scale=(0.4 + 0.6 * k) * pulse, alpha=min(1, tl * 8))
        if tl > 0.35:
            a = min(1, (tl - 0.35) * 5)
            put(frame, text_img("Link in description, like & subscribe", 56, WHITE, maxw=940), W / 2, 1130, alpha=a)
            put(frame, text_img("Lien en description, likez et abonnez-vous", 40, CYAN, bold=False, maxw=940, stroke=5), W / 2, 1240, alpha=a)
        if tl > 0.9:
            a = min(1, (tl - 0.9) * 4)
            panel(frame, 80, 1330, W - 80, 1560, bar=YEL)
            put(frame, text_img(LINK1, 54, YEL, maxw=900), W / 2 + 10, 1405, alpha=a)
            put(frame, text_img(LINK2, 54, YEL, maxw=900), W / 2 + 10, 1500, alpha=a)
    # affiliate notice (obligatory) from the reveal on
    footer(frame, t)
    flash(frame, fl)
    if shake:
        dx, dy = int(random.uniform(-shake, shake)), int(random.uniform(-shake, shake))
        frame = ImageChops.offset(frame.convert('RGB'), dx, dy).convert('RGBA')
    return frame

# ---------- main
def main():
    N = int(DUR * FPS); dt = 1 / FPS
    if ONLY:
        t_prev = 0.0
        want = {int(round(x * FPS)) for x in ONLY}
        for i in range(N):
            f = compose(i * dt, dt)
            if i in want: f.convert('RGB').save(f'frame_{i * dt:05.2f}.png')
        return
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', str(FPS), OUT],
                         stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(compose(i * dt, dt).convert('RGB').tobytes())
        if i % 60 == 0: print(f'{i}/{N}', flush=True)
    p.stdin.close(); p.wait()

main()
