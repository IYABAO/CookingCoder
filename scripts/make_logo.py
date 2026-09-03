# -*- coding: utf-8 -*-
"""生成 CookingCoder 的 logo.png 与 favicon.ico（程序猿厨师帽 + 代码尖括号）"""
from PIL import Image, ImageDraw, ImageFont
import os

SIZE = 512
bg1 = (255, 112, 67)   # #FF7043 深橙
bg2 = (230, 74, 25)    # #E64A19

# 1) 渐变背景 + 圆角遮罩
base = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
px = base.load()
for y in range(SIZE):
    t = y / SIZE
    r = int(bg1[0]*(1-t) + bg2[0]*t)
    g = int(bg1[1]*(1-t) + bg2[1]*t)
    b = int(bg1[2]*(1-t) + bg2[2]*t)
    for x in range(SIZE):
        px[x, y] = (r, g, b, 255)

mask = Image.new('L', (SIZE, SIZE), 0)
md = ImageDraw.Draw(mask)
md.rounded_rectangle([0, 0, SIZE, SIZE], radius=100, fill=255)
base.putalpha(mask)

d = ImageDraw.Draw(base)
white = (255, 255, 255, 255)
cap_w = 250
cap_h = 150
cap_cx = 256
cap_bottom = 380
cap_top = cap_bottom - cap_h  # 230

# 帽身（矩形）
d.rounded_rectangle([cap_cx - cap_w//2, cap_top, cap_cx + cap_w//2, cap_bottom],
                    radius=18, fill=white)

# 帽顶三个鼓包
bump_y = cap_top + 10
d.ellipse([cap_cx-125, bump_y-58, cap_cx-125+116, bump_y+58], fill=white)
d.ellipse([cap_cx-58,  bump_y-58, cap_cx+58,  bump_y+58], fill=white)
d.ellipse([cap_cx+9,   bump_y-58, cap_cx+125, bump_y+58], fill=white)

# 帽檐横带
d.rounded_rectangle([cap_cx - cap_w//2 - 8, cap_bottom-52, cap_cx + cap_w//2 + 8, cap_bottom-22],
                    radius=10, fill=white)

# 帽檐橙点装饰
orange_dot = (255, 112, 67, 255)
dot_r = 9
for dx in (-80, 0, 80):
    d.ellipse([cap_cx+dx-dot_r, cap_bottom-37-dot_r, cap_cx+dx+dot_r, cap_bottom-37+dot_r],
              fill=orange_dot)

# 帽身内代码符号 </> 深棕色
code_color = (62, 39, 35, 255)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 46)
except Exception:
    font = ImageFont.load_default()

code_text = "</>"
bbox = d.textbbox((0, 0), code_text, font=font)
tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
tx = cap_cx - tw/2 - bbox[0]
ty = (cap_top+cap_bottom)/2 - th/2 - bbox[1] - 6
d.text((tx, ty), code_text, fill=code_color, font=font)

out_dir = r'E:\github\CookingCoder\docs\assets'
os.makedirs(out_dir, exist_ok=True)
logo_path = os.path.join(out_dir, 'logo.png')
base.save(logo_path)
print('logo.png saved', base.size)

# favicon.ico
fav_sizes = [(16, 16), (32, 32), (48, 48)]
imgs = [base.resize(s, Image.LANCZOS) for s in fav_sizes]
fav_path = os.path.join(out_dir, 'favicon.ico')
imgs[-1].save(fav_path, format='ICO', sizes=fav_sizes)
print('favicon.ico saved')
