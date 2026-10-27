# Builds favicon.ico, favicon-32.png and apple-touch-icon.png in images/ from the D mark of images/logo.webp.
# Run by hand when the logo changes: python3 _source/favicon.py  (build.py copies the results to the site root)
import os, numpy as np
from collections import deque
from PIL import Image, ImageDraw, ImageFilter
BASE = os.path.dirname(os.path.abspath(__file__))
src, out = os.path.join(BASE, 'images', 'logo.webp'), os.path.join(BASE, 'images')
m = Image.open(src).convert('RGBA'); A = np.array(m).astype(float); H, W = A.shape[:2]
ink = A[:,:,3] > 60
lab = np.zeros((H, W), int); k = 0; info = {}
for y in range(H):
    for x in range(W):
        if ink[y,x] and not lab[y,x]:
            k += 1; q = deque([(y,x)]); lab[y,x] = k; n = 0; xs = []
            while q:
                cy, cx = q.popleft(); n += 1; xs.append(cx)
                for dy in (-1,0,1):
                    for dx in (-1,0,1):
                        ny, nx = cy+dy, cx+dx
                        if 0<=ny<H and 0<=nx<W and ink[ny,nx] and not lab[ny,nx]: lab[ny,nx] = k; q.append((ny,nx))
            info[k] = (n, min(xs), max(xs))
# the D of "Driven" is the big component starting at x~130; its arrow is the violet component inside it
D = max((c for c in info if 125 <= info[c][1] <= 135), key=lambda c: info[c][0])
arrow = [c for c in info if c != D and info[c][1] >= info[D][1] and info[c][2] <= info[D][2] and A[lab==c][:, :3].mean(axis=0)[2] > 150]
keep = np.isin(lab, [D] + arrow)
other = (lab > 0) & ~keep
def dil(mk, r):
    o = mk.copy()
    for _ in range(r): o = o | np.roll(o,1,0) | np.roll(o,-1,0) | np.roll(o,1,1) | np.roll(o,-1,1)
    return o
mask = dil(keep, 2) & ~dil(other, 1) | keep          # antialiased fringe of the mark, never the neighbour's
B = A.copy(); B[~mask, 3] = 0
ys, xs = np.where(B[:,:,3] > 0); B = B[ys.min():ys.max()+1, xs.min():xs.max()+1]
mark = Image.fromarray(B.astype(np.uint8), 'RGBA')
# upscale 6x, then re-sharpen the edge and snap colour to the two brand inks
S = 6; big = mark.resize((mark.width*S, mark.height*S), Image.LANCZOS)
Bb = np.array(big).astype(float); a = np.clip(Bb[:,:,3]/255, 0, 1)
a = np.clip((a - .5) * 3.2 + .5, 0, 1); a = a*a*(3-2*a)
navy, violet = np.array([16,25,65.]), np.array([66,51,255.])
rgb = Bb[:,:,:3]; isv = ((rgb-violet)**2).sum(2) < ((rgb-navy)**2).sum(2)
col = np.where(isv[...,None], violet, navy)
hi = Image.fromarray(np.dstack([col, a*255]).astype(np.uint8), 'RGBA').filter(ImageFilter.SMOOTH)

def tile(size, pad=.16, radius=.22, bg=(255,255,255,255)):
    big = size*4; t = Image.new('RGBA', (big, big), (0,0,0,0))
    ImageDraw.Draw(t).rounded_rectangle((0,0,big-1,big-1), radius=int(big*radius), fill=bg)
    inner = int(big*(1-2*pad)); s = min(inner/hi.width, inner/hi.height)
    mk = hi.resize((round(hi.width*s), round(hi.height*s)), Image.LANCZOS)
    t.alpha_composite(mk, ((big-mk.width)//2, (big-mk.height)//2))
    return t.resize((size, size), Image.LANCZOS)
ico = [tile(n, pad=.08) for n in (16, 32, 48)]
ico[2].save(f'{out}/favicon.ico', sizes=[(16,16),(32,32),(48,48)], append_images=ico[:2])
tile(32, pad=.08).save(f'{out}/favicon-32.png')
tile(180, pad=.18, radius=0).save(f'{out}/apple-touch-icon.png')   # iOS rounds the corners itself
print('mark', mark.size, '-> hi', hi.size)
