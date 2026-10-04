import numpy as np
from PIL import Image, ImageDraw, ImageFilter
I='/tmp/claude-0/-home-user-skills-introduction-to-github/c09eafb4-e0f9-5725-8cf0-1a50e5566c30/images/'
im=Image.open(I+'1.png').convert('RGB').crop((325,175,725,430))
im=im.resize((im.width*3,im.height*3),Image.LANCZOS).filter(ImageFilter.UnsharpMask(2,80,2))
a=np.array(im).astype(np.int16)
a[:480,:410]=255                       # box art + its shadow (not part of the product)
a[:135,410:630]=255; a[:150,410:500]=255
im=Image.fromarray(a.astype(np.uint8))
minc=np.array(im).min(axis=2)
bg=Image.fromarray(((minc>218)*255).astype(np.uint8))   # near-white candidates
# flood fill from the borders so interior light parts of the product are kept
h,w=bg.size[1],bg.size[0]
mark=bg.copy()
for x in range(0,w,4):
    for y in (0,h-1):
        if mark.getpixel((x,y))==255: ImageDraw.floodfill(mark,(x,y),128)
for y in range(0,h,4):
    for x in (0,w-1):
        if mark.getpixel((x,y))==255: ImageDraw.floodfill(mark,(x,y),128)
m=np.array(mark)==128
alpha=np.where(m,0,255).astype(np.uint8)
alpha=Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
out=im.convert('RGBA'); out.putalpha(alpha)
bb=out.getchannel('A').point(lambda v:255 if v>20 else 0).getbbox(); print(bb)
out=out.crop(bb); out.save('hero.png'); print(out.size)
bgd=Image.new('RGBA',out.size,(20,25,60,255)); bgd.alpha_composite(out); bgd.save('hero_check.png')
