#!/usr/bin/env python3
"""Generate a black, modern OGP image (1200x630) for rotomx's Portfolio.
If avatar.jpg / avatar.png exists in the same dir, it is composited as the
circular avatar. Otherwise a designed monogram is used.
"""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 630
SS = 2  # supersample
w, h = W * SS, H * SS

BG = (10, 10, 10)
GRID = (29, 29, 29)
TEXT = (245, 245, 245)
MUTED = (150, 150, 150)
DIM = (107, 107, 107)
LINE = (38, 38, 38)

FB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

img = Image.new("RGB", (w, h), BG)
d = ImageDraw.Draw(img)

# ---- grid with vignette mask (fade from top center) ----
grid = Image.new("RGB", (w, h), BG)
gd = ImageDraw.Draw(grid)
step = 64 * SS
for x in range(0, w, step):
    gd.line([(x, 0), (x, h)], fill=GRID, width=SS)
for y in range(0, h, step):
    gd.line([(0, y), (w, y)], fill=GRID, width=SS)
# radial-ish mask: brightest near top-center, fading down/out
mask = Image.new("L", (w, h), 0)
mk = ImageDraw.Draw(mask)
cx, cy = w * 0.5, h * 0.12
maxd = math.hypot(w * 0.62, h * 0.78)
for yy in range(0, h, 2 * SS):
    for xx in range(0, w, 2 * SS):
        dist = math.hypot(xx - cx, yy - cy)
        v = max(0, 1 - (dist / maxd))
        mk.rectangle([xx, yy, xx + 2 * SS, yy + 2 * SS], fill=int(v * 150))
img = Image.composite(grid, img, mask)
d = ImageDraw.Draw(img)

# ---- inset frame ----
m = 36 * SS
d.rounded_rectangle([m, m, w - m, h - m], radius=24 * SS, outline=LINE, width=2 * SS)

# ---- avatar with conic-style ring ----
AV = 240 * SS          # outer ring diameter
RINGW = 8 * SS
acx = w // 2
atop = 96 * SS
acy = atop + AV // 2

# conic gradient ring (grays), drawn at high res then masked to annulus
stops = [(255,255,255),(90,90,90),(255,255,255),(55,55,55),(255,255,255),(255,255,255)]
def lerp(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i]) * t) for i in range(3))
def conic_color(deg):
    p = (deg % 360) / 360.0 * (len(stops) - 1)
    i = int(p); t = p - i
    return lerp(stops[i], stops[min(i+1, len(stops)-1)], t)

ring = Image.new("RGB", (AV, AV), BG)
rd = ImageDraw.Draw(ring)
start = 200  # matches site's "from 200deg"
for a in range(0, 360, 1):
    rd.pieslice([0, 0, AV-1, AV-1], start + a, start + a + 2, fill=conic_color(a))
# punch inner hole -> annulus
hole = Image.new("L", (AV, AV), 0)
hd = ImageDraw.Draw(hole)
hd.ellipse([0, 0, AV-1, AV-1], fill=255)
inner_pad = RINGW
hd.ellipse([inner_pad, inner_pad, AV-1-inner_pad, AV-1-inner_pad], fill=0)
ring_rgba = ring.convert("RGBA")
ring_rgba.putalpha(hole)
img.paste(ring_rgba, (acx - AV//2, acy - AV//2), ring_rgba)

# inner content circle
INN = AV - 2 * (RINGW + 4 * SS)
inner_xy = (acx - INN//2, acy - INN//2)
avatar_path = None
for cand in ("avatar.jpg", "avatar.jpeg", "avatar.png"):
    if os.path.exists(cand):
        avatar_path = cand; break

cmask = Image.new("L", (INN, INN), 0)
ImageDraw.Draw(cmask).ellipse([0, 0, INN-1, INN-1], fill=255)

if avatar_path:
    av = Image.open(avatar_path).convert("RGB")
    # cover-crop to square
    s = min(av.size)
    av = av.crop(((av.width-s)//2, (av.height-s)//2, (av.width-s)//2+s, (av.height-s)//2+s)).resize((INN, INN), Image.LANCZOS)
    img.paste(av, inner_xy, cmask)
    USED_PHOTO = True
else:
    # designed monogram on subtle radial dark fill
    disc = Image.new("RGB", (INN, INN), (20, 20, 20))
    dd = ImageDraw.Draw(disc)
    for r in range(INN//2, 0, -1):
        t = 1 - r/(INN/2)
        c = lerp((34,34,34), (15,15,15), t)
        dd.ellipse([INN//2-r, INN//2-r, INN//2+r, INN//2+r], fill=c)
    mf = font(FB, int(INN*0.5))
    tb = dd.textbbox((0,0), "R", font=mf)
    dd.text((INN/2-(tb[2]-tb[0])/2-tb[0], INN/2-(tb[3]-tb[1])/2-tb[1]), "R", font=mf, fill=(245,245,245))
    img.paste(disc, inner_xy, cmask)
    USED_PHOTO = False

d = ImageDraw.Draw(img)

def center_text(y, text, fnt, fill, tracking=0):
    if tracking == 0:
        bb = d.textbbox((0,0), text, font=fnt)
        d.text((w/2-(bb[2]-bb[0])/2-bb[0], y), text, font=fnt, fill=fill)
        return
    widths = [d.textbbox((0,0), ch, font=fnt)[2] for ch in text]
    total = sum(widths) + tracking*(len(text)-1)
    x = w/2 - total/2
    for ch, cw in zip(text, widths):
        d.text((x, y), ch, font=fnt, fill=fill)
        x += cw + tracking

# ---- title ----
title_f = font(FB, 92 * SS // 1)
center_text(acy + AV//2 + 36*SS, "rotomx's Portfolio", title_f, TEXT)

# ---- subtitle ----
sub_f = font(FR, 30 * SS)
center_text(acy + AV//2 + 152*SS, "CORPORATE ENGINEER", sub_f, MUTED, tracking=8*SS)

# ---- handle (small, with brand dot) ----
hf = font(FR, 27 * SS)
handle = "@rotomx"
hb = d.textbbox((0,0), handle, font=hf)
dot_r = 7 * SS
gap = 14 * SS
total = dot_r*2 + gap + (hb[2]-hb[0])
hx = w/2 - total/2
hy = acy + AV//2 + 205*SS
d.ellipse([hx, hy+10*SS, hx+dot_r*2, hy+10*SS+dot_r*2], fill=(255,255,255))
d.text((hx+dot_r*2+gap, hy), handle, font=hf, fill=DIM)

img = img.resize((W, H), Image.LANCZOS)
img.save("og-image.png")
print("saved og-image.png  photo=", USED_PHOTO)
