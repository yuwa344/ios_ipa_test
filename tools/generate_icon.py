#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 JR_CompanyWork App 图标(1024x1024 PNG,纯标准库,无第三方依赖)。
主题:深色渐变背景 + 白色办公大楼(塔楼 + 窗格) + 蓝色顶冠,呼应「企业办公」。
注意:iOS App 图标不允许 alpha 通道,输出纯 RGB(颜色类型 2),圆角由系统自动裁剪。
用法: python tools/generate_icon.py
输出: JR_CompanyWork/Assets.xcassets/AppIcon.appiconset/AppIcon.png
"""
import os
import struct
import zlib

W = H = 1024
OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "JR_CompanyWork", "Assets.xcassets", "AppIcon.appiconset", "AppIcon.png",
)

# ---------- 画布 ----------
px = [[0, 0, 0] for _ in range(W * H)]


def set_px(x, y, rgb):
    if 0 <= x < W and 0 <= y < H:
        px[y * W + x] = rgb


def blend(dst, src, a):
    return [int(dst[i] * (1 - a) + src[i] * a) for i in range(3)]


# ---------- 背景:垂直渐变 #0B0F1A -> #151A2D ----------
TOP = (11, 15, 26)
BOT = (21, 26, 45)
for y in range(H):
    t = y / (H - 1)
    c = [int(TOP[i] * (1 - t) + BOT[i] * t) for i in range(3)]
    for x in range(W):
        px[y * W + x] = c

# ---------- 径向高光(中心偏上,增加质感) ----------
cx, cy, cr = W * 0.5, H * 0.36, W * 0.75
for y in range(H):
    for x in range(W):
        d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
        if d < cr:
            a = (1 - d / cr) ** 2 * 0.10
            px[y * W + x] = blend(px[y * W + x], (120, 150, 220), a)


# ---------- 工具函数 ----------
def rect(x0, y0, x1, y1, rgb):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            set_px(x, y, rgb)


def fill_triangle(p1, p2, p3, rgb):
    xs = [p1[0], p2[0], p3[0]]
    ys = [p1[1], p2[1], p3[1]]
    for y in range(min(ys), max(ys) + 1):
        for x in range(min(xs), max(xs) + 1):
            def sign(a, b, c):
                return (a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])
            d1 = sign((x, y), p1, p2)
            d2 = sign((x, y), p2, p3)
            d3 = sign((x, y), p3, p1)
            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            if not (has_neg and has_pos):
                set_px(x, y, rgb)


# ---------- 圆角裁剪(圆角外填充背景色,无 alpha) ----------
RAD = 230
for y in range(H):
    for x in range(W):
        if not ((RAD <= x < W - RAD) or (RAD <= y < H - RAD)):
            cx_ = RAD if x < W / 2 else W - 1 - RAD
            cy_ = RAD if y < H / 2 else H - 1 - RAD
            if (x - cx_) ** 2 + (y - cy_) ** 2 > RAD ** 2:
                px[y * W + x] = TOP

# ---------- 主体:白色办公大楼 ----------
WHITE = (245, 247, 250)
BLUE = (59, 130, 246)

# 主楼体(居中,从底部到 78% 高度)
bx0, bx1 = 300, 724
by0, by1 = 250, 940
rect(bx0, by0, bx1, by1, WHITE)

# 顶部蓝色冠(梯形收顶)
fill_triangle((bx0, by0), (bx1, by0), (512, 120), BLUE)

# 窗格(网格,用背景色挖出窗户)
WIN = (11, 15, 26)
cols = 5
rows = 9
margin_x = 70
margin_y = 60
win_w = 46
win_h = 52
gap_x = (bx1 - bx0 - 2 * margin_x - cols * win_w) / (cols - 1)
gap_y = (by1 - by0 - 2 * margin_y - rows * win_h) / (rows - 1)
for r in range(rows):
    for c in range(cols):
        wx0 = bx0 + margin_x + c * (win_w + gap_x)
        wy0 = by0 + margin_y + r * (win_h + gap_y)
        rect(wx0, wy0, wx0 + win_w, wy0 + win_h, WIN)

# 大门(底部中央,蓝色)
rect(462, 860, 562, 940, BLUE)

# ---------- 写入 PNG ----------
# iOS App 图标不允许 alpha 通道,输出纯 RGB(颜色类型 2)
raw = bytearray()
for y in range(H):
    raw.append(0)  # filter: None
    for x in range(W):
        r, g, b = px[y * W + x]
        raw += struct.pack("BBB", r, g, b)


def chunk(tag, data):
    c = struct.pack(">I", len(data)) + tag + data
    return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))  # color type 2 = RGB
png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
png += chunk(b"IEND", b"")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "wb") as f:
    f.write(png)
print("OK ->", OUT, os.path.getsize(OUT), "bytes")
