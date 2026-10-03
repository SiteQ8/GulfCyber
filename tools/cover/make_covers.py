#!/usr/bin/env python3
"""يولد ثلاثة تصاميم غلاف أصلية بصيغة SVG ثم يحولها إلى PNG وJPEG بمقاس غلاف الكيندل 1600 في 2560.

الاستخدام:
  python3 cover/make_covers.py                 يولد الخيارات الثلاثة بعناوين مقترحة
  python3 cover/make_covers.py --title "..." --subtitle "..." --design sadu|star|dial
"""
import argparse
import math
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "options"
W, H = 1600, 2560
AUTHOR = "علي العنزي"
SANS = "IBM Plex Sans Arabic"
SERIF = "Amiri"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size, family, fill, weight="bold", anchor="middle", opacity=1.0, spacing=0):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" direction="rtl" opacity="{opacity}" '
            f'letter-spacing="{spacing}">{esc(s)}</text>')


def title_block(title, subtitle, y, color, family, size=150, sub_size=56, sub_color="#D8DEE9"):
    out = []
    lines = split_title(title, max_len=18)
    yy = y
    for line in lines:
        out.append(text(W / 2, yy, line, size, family, color))
        yy += size * 1.15
    if subtitle:
        out.append(text(W / 2, yy + 20, subtitle, sub_size, SANS, sub_color, weight="normal"))
    return "\n".join(out), yy


def split_title(title, max_len=18):
    """يقسم العنوان الطويل على سطرين عند النقطتين أو عند منتصفه."""
    if ":" in title:
        a, b = title.split(":", 1)
        return [a.strip(), b.strip()]
    words = title.split()
    if len(title) <= max_len or len(words) < 3:
        return [title]
    mid = len(words) // 2
    return [" ".join(words[:mid]), " ".join(words[mid:])]


def design_sadu(title, subtitle):
    """سدو رقمي: مثلثات السدو تتحول إلى مسارات دوائر إلكترونية حول درع سداسي."""
    rnd = random.Random(7)
    navy, gold, red, cream = "#0B1F3A", "#C9A227", "#A23B2F", "#F3E9D2"
    p = [f'<rect width="{W}" height="{H}" fill="{navy}"/>']
    p.append(f'<defs><radialGradient id="g" cx="50%" cy="42%" r="55%"><stop offset="0" stop-color="#16345E"/>'
             f'<stop offset="1" stop-color="{navy}"/></radialGradient></defs>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#g)"/>')
    # شبكة مسارات خافتة
    for i in range(0, W, 80):
        p.append(f'<line x1="{i}" y1="0" x2="{i}" y2="{H}" stroke="{gold}" stroke-opacity="0.05"/>')
    for j in range(0, H, 80):
        p.append(f'<line x1="0" y1="{j}" x2="{W}" y2="{j}" stroke="{gold}" stroke-opacity="0.05"/>')
    # نطاق السدو: صفوف مثلثات ومعينات
    def band(y0, h, color, op):
        row = []
        step = 100
        for x in range(0, W + step, step):
            row.append(f'<polygon points="{x},{y0+h} {x+step/2},{y0} {x+step},{y0+h}" fill="{color}" fill-opacity="{op}"/>')
        return "\n".join(row)
    base = 1660
    p.append(f'<rect x="0" y="{base-30}" width="{W}" height="14" fill="{gold}" fill-opacity="0.8"/>')
    p.append(band(base, 90, gold, 0.85))
    p.append(band(base + 110, 70, red, 0.85))
    p.append(band(base + 200, 90, cream, 0.75))
    p.append(f'<rect x="0" y="{base+310}" width="{W}" height="14" fill="{gold}" fill-opacity="0.8"/>')
    # مسارات دوائر تخرج من النطاق إلى الأعلى مع عقد
    for k in range(18):
        x = 60 + k * 85 + rnd.randint(-20, 20)
        y1 = base - 40
        y2 = y1 - rnd.randint(100, 190)
        xo = x + rnd.choice([-60, 0, 60])
        p.append(f'<polyline points="{x},{y1} {x},{y2+60} {xo},{y2}" fill="none" stroke="{gold}" stroke-opacity="0.45" stroke-width="3"/>')
        p.append(f'<circle cx="{xo}" cy="{y2}" r="7" fill="{gold}" fill-opacity="0.9"/>')
    # الدرع السداسي في المنتصف الأعلى
    cx, cy, r = W / 2, 760, 330
    hexpts = " ".join(f"{cx + r*math.cos(math.radians(60*i-30))},{cy + r*math.sin(math.radians(60*i-30))}" for i in range(6))
    p.append(f'<polygon points="{hexpts}" fill="none" stroke="{gold}" stroke-width="10"/>')
    r2 = 250
    hex2 = " ".join(f"{cx + r2*math.cos(math.radians(60*i-30))},{cy + r2*math.sin(math.radians(60*i-30))}" for i in range(6))
    p.append(f'<polygon points="{hex2}" fill="#16345E" fill-opacity="0.6" stroke="{cream}" stroke-width="3" stroke-opacity="0.6"/>')
    # قفل مبسط داخل الدرع
    p.append(f'<rect x="{cx-110}" y="{cy-20}" width="220" height="170" rx="22" fill="{gold}"/>')
    p.append(f'<path d="M {cx-70} {cy-20} v -70 a 70 70 0 0 1 140 0 v 70" fill="none" stroke="{gold}" stroke-width="26"/>')
    p.append(f'<circle cx="{cx}" cy="{cy+55}" r="26" fill="{navy}"/>')
    p.append(f'<rect x="{cx-10}" y="{cy+55}" width="20" height="55" fill="{navy}"/>')
    # العنوان
    tb, yy = title_block(title, subtitle, 1200, cream, SANS, size=170, sub_size=60)
    p.append(tb)
    p.append(text(W / 2, H - 170, AUTHOR, 70, SANS, cream, weight="normal"))
    return "\n".join(p)


def design_star(title, subtitle):
    """نجمة ثمانية: تكرار هندسي إسلامي بخطوط رفيعة يتحول في المركز إلى شبكة عقد مضيئة."""
    bg, line, glow, cream = "#0F2A33", "#2EC4B6", "#9BF1E6", "#F4EBD0"
    p = [f'<rect width="{W}" height="{H}" fill="{bg}"/>']
    p.append('<defs><linearGradient id="v" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0F2A33"/>'
             '<stop offset="1" stop-color="#071A20"/></linearGradient>'
             '<filter id="blur"><feGaussianBlur stdDeviation="14"/></filter></defs>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#v)"/>')

    def octagram(cx, cy, r, stroke, width, op):
        a = " ".join(f"{cx + r*math.cos(math.radians(90*i))},{cy + r*math.sin(math.radians(90*i))}" for i in range(4))
        b = " ".join(f"{cx + r*math.cos(math.radians(90*i+45))},{cy + r*math.sin(math.radians(90*i+45))}" for i in range(4))
        return (f'<polygon points="{a}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-opacity="{op}"/>'
                f'<polygon points="{b}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-opacity="{op}"/>')
    # التكرار الخافت
    step = 220
    for y in range(-100, H + step, step):
        for x in range(-100, W + step, step):
            d = math.hypot(x - W / 2, y - 820)
            op = max(0.04, min(0.22, 0.26 - d / 4200))
            p.append(octagram(x, y, 95, line, 1.5, op))
    # الشبكة المضيئة في المركز
    cx, cy = W / 2, 820
    p.append(f'<circle cx="{cx}" cy="{cy}" r="300" fill="{line}" fill-opacity="0.12" filter="url(#blur)"/>')
    for r, wdt, op in ((330, 6, 0.9), (230, 4, 0.8), (130, 3, 0.7)):
        p.append(octagram(cx, cy, r, glow, wdt, op))
    nodes = [(cx + 330 * math.cos(math.radians(45 * i)), cy + 330 * math.sin(math.radians(45 * i))) for i in range(8)]
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if j > i and (j - i) in (3, 5):
                p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{glow}" stroke-width="2" stroke-opacity="0.35"/>')
        p.append(f'<circle cx="{x1}" cy="{y1}" r="16" fill="{glow}"/>')
        p.append(f'<circle cx="{x1}" cy="{y1}" r="30" fill="none" stroke="{glow}" stroke-opacity="0.5" stroke-width="2"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="34" fill="{cream}"/>')
    # شريط العنوان
    p.append(f'<rect x="0" y="1330" width="{W}" height="620" fill="#071A20" fill-opacity="0.72"/>')
    p.append(f'<line x1="200" y1="1330" x2="{W-200}" y2="1330" stroke="{line}" stroke-width="3"/>')
    p.append(f'<line x1="200" y1="1950" x2="{W-200}" y2="1950" stroke="{line}" stroke-width="3"/>')
    tb, yy = title_block(title, subtitle, 1560, cream, SERIF, size=190, sub_size=62, sub_color="#BFE9E3")
    p.append(tb)
    p.append(text(W / 2, H - 170, AUTHOR, 72, SERIF, cream, weight="normal"))
    return "\n".join(p)


def design_dial(title, subtitle):
    """قرص القفل: تصميم طباعي صارم مع قرص قفل ذهبي رفيع يحمل أرقاماً وعلامات."""
    bg1, bg2, gold, white = "#0A1628", "#02070F", "#D4AF37", "#FFFFFF"
    p = ['<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient></defs>']
    p.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    cx, cy, R = W / 2, 740, 420
    for r, wdt, op in ((R, 5, 1), (R - 60, 2, 0.6), (R - 200, 2, 0.5), (R - 330, 3, 0.9)):
        p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{gold}" stroke-width="{wdt}" stroke-opacity="{op}"/>')
    for i in range(72):
        ang = math.radians(i * 5)
        long = i % 6 == 0
        r1 = R - 12
        r2 = R - (48 if long else 28)
        x1, y1 = cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)
        x2, y2 = cx + r2 * math.cos(ang), cy + r2 * math.sin(ang)
        p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{gold}" stroke-width="{4 if long else 2}"/>')
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        x, y = cx + (R - 120) * math.cos(ang), cy + (R - 120) * math.sin(ang)
        p.append(f'<text x="{x}" y="{y+16}" font-family="{SANS}" font-size="44" fill="{gold}" text-anchor="middle" '
                 f'opacity="0.9">{i * 5:02d}</text>')
    # مؤشر وقلب القفل
    p.append(f'<polygon points="{cx},{cy-R-40} {cx-26},{cy-R+12} {cx+26},{cy-R+12}" fill="{gold}"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="40" fill="{gold}"/>')
    p.append(f'<rect x="{cx-9}" y="{cy}" width="18" height="60" fill="{bg2}"/>')
    p.append(f'<circle cx="{cx}" cy="{cy-6}" r="12" fill="{bg2}"/>')
    # خطوط اتصال رفيعة من القرص إلى الحواف
    for ang in (20, 160, 200, 340):
        a = math.radians(ang)
        x1, y1 = cx + R * math.cos(a), cy + R * math.sin(a)
        x2, y2 = cx + (R + 420) * math.cos(a), cy + (R + 420) * math.sin(a)
        p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{gold}" stroke-width="2" stroke-opacity="0.35"/>')
        p.append(f'<circle cx="{x2}" cy="{y2}" r="8" fill="{gold}" fill-opacity="0.7"/>')
    p.append(f'<line x1="260" y1="1400" x2="{W-260}" y2="1400" stroke="{gold}" stroke-width="3"/>')
    tb, yy = title_block(title, subtitle, 1620, white, SANS, size=150, sub_size=58, sub_color="#C9D1E0")
    p.append(tb)
    p.append(f'<line x1="260" y1="{yy+90}" x2="{W-260}" y2="{yy+90}" stroke="{gold}" stroke-width="3"/>')
    p.append(text(W / 2, H - 170, AUTHOR, 68, SANS, gold, weight="normal"))
    return "\n".join(p)




def shield_halfwidth(t):
    """نصف عرض الدرع عند ارتفاع نسبي t من القمة 0 إلى الرأس 1."""
    if t < 0:
        return 0
    return max(0.0, (1 - t ** 1.6) ** 0.7)


def design_shield(title, subtitle):
    """درع الفسيفساء: درع كبير مؤلف من مئات المربعات المضيئة بتدرج من الذهبي إلى الفيروزي."""
    rnd = random.Random(11)
    bg1, bg2 = "#0A1A33", "#03070F"
    p = ['<defs><radialGradient id="rg" cx="50%" cy="38%" r="60%">'
         f'<stop offset="0" stop-color="#143A66"/><stop offset="1" stop-color="{bg2}"/></radialGradient>'
         '<filter id="soft"><feGaussianBlur stdDeviation="22"/></filter></defs>']
    p.append(f'<rect width="{W}" height="{H}" fill="{bg1}"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#rg)"/>')
    # شبكة سداسية خافتة في الخلفية
    rr = 46
    for row in range(0, 60):
        for col in range(0, 24):
            cx = col * rr * 3 + (rr * 1.5 if row % 2 else 0)
            cy = row * rr * 0.866
            pts = " ".join(f"{cx + rr*math.cos(math.radians(60*i))},{cy + rr*math.sin(math.radians(60*i))}" for i in range(6))
            p.append(f'<polygon points="{pts}" fill="none" stroke="#5B7FB3" stroke-opacity="0.07" stroke-width="1"/>')
    # الدرع
    cx, top, height, halfw = W / 2, 330, 1120, 470
    p.append(f'<ellipse cx="{cx}" cy="{top + height*0.45}" rx="560" ry="640" fill="#1D5C8F" fill-opacity="0.35" filter="url(#soft)"/>')
    cell, gap = 34, 7
    for y in range(int(top), int(top + height), cell + gap):
        t = (y - top) / height
        hw = shield_halfwidth(t) * halfw
        for x in range(int(cx - halfw), int(cx + halfw), cell + gap):
            if abs(x + cell / 2 - cx) > hw:
                continue
            # تدرج اللون من الذهبي أعلى إلى الفيروزي أسفل
            g = (0xE2, 0xB9, 0x3B)
            tq = (0x2E, 0xC4, 0xB6)
            k = min(1.0, max(0.0, t * 1.15))
            r_, g_, b_ = (int(g[i] + (tq[i] - g[i]) * k) for i in range(3))
            op = rnd.uniform(0.35, 0.95)
            if rnd.random() < 0.06:
                r_, g_, b_, op = 255, 255, 255, 0.95
            p.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="rgb({r_},{g_},{b_})" fill-opacity="{op:.2f}"/>')
    # محيط الدرع بخط رفيع
    pts = []
    for i in range(0, 61):
        t = i / 60
        pts.append((cx - shield_halfwidth(t) * halfw, top + t * height))
    for i in range(60, -1, -1):
        t = i / 60
        pts.append((cx + shield_halfwidth(t) * halfw, top + t * height))
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    p.append(f'<path d="{d}" fill="none" stroke="#F3E9D2" stroke-width="4" stroke-opacity="0.9"/>')
    p.append(f'<path d="{d}" fill="none" stroke="#2EC4B6" stroke-width="14" stroke-opacity="0.25"/>')
    # ثقب المفتاح في وسط الدرع
    kx, ky = cx, top + height * 0.42
    p.append(f'<circle cx="{kx}" cy="{ky}" r="78" fill="{bg2}"/>')
    p.append(f'<polygon points="{kx-34},{ky+40} {kx+34},{ky+40} {kx+58},{ky+200} {kx-58},{ky+200}" fill="{bg2}"/>')
    p.append(f'<circle cx="{kx}" cy="{ky}" r="78" fill="none" stroke="#F3E9D2" stroke-width="5"/>')
    p.append(f'<polygon points="{kx-34},{ky+40} {kx+34},{ky+40} {kx+58},{ky+200} {kx-58},{ky+200}" fill="none" stroke="#F3E9D2" stroke-width="5"/>')
    # العنوان
    p.append(f'<line x1="300" y1="1570" x2="{W-300}" y2="1570" stroke="#E2B93B" stroke-width="3" stroke-opacity="0.9"/>')
    tb, yy = title_block(title, subtitle, 1790, "#FFFFFF", SANS, size=190, sub_size=62, sub_color="#E2B93B")
    p.append(tb)
    p.append(f'<line x1="300" y1="{yy+110}" x2="{W-300}" y2="{yy+110}" stroke="#E2B93B" stroke-width="3" stroke-opacity="0.9"/>')
    p.append(text(W / 2, H - 170, AUTHOR, 70, SANS, "#F3E9D2", weight="normal"))
    return "\n".join(p)


def inside_triangle(pt, a, b, c):
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    d1, d2, d3 = sign(pt, a, b), sign(pt, b, c), sign(pt, c, a)
    has_neg = d1 < 0 or d2 < 0 or d3 < 0
    has_pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (has_neg and has_pos)


def design_dhow(title, subtitle):
    """شراع البوم: شراع مركب خليجي مرسوم بشبكة عقد مضيئة فوق بحر من الخطوط."""
    rnd = random.Random(23)
    bg1, bg2, gold, teal, cream = "#07262E", "#020D12", "#E2B93B", "#3FD6C8", "#F4EBD0"
    p = ['<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="#0B3340"/><stop offset="0.55" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient>'
         '<filter id="glow"><feGaussianBlur stdDeviation="18"/></filter></defs>']
    p.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    # نجوم خافتة
    for _ in range(140):
        x, y = rnd.uniform(0, W), rnd.uniform(0, 1300)
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(1,2.6):.1f}" fill="{cream}" fill-opacity="{rnd.uniform(0.15,0.6):.2f}"/>')
    # القمر الهلال
    p.append(f'<circle cx="1360" cy="240" r="90" fill="{gold}" fill-opacity="0.18" filter="url(#glow)"/>')
    p.append('<path d="M 1360 150 A 90 90 0 1 1 1360 330 A 70 70 0 1 0 1360 150 Z" fill="#E2B93B" fill-opacity="0.85"/>')
    # البحر
    for i in range(26):
        y = 1560 + i * 34
        amp = 10 + i * 0.6
        d = f"M 0 {y} "
        for x in range(0, W + 40, 40):
            d += f"L {x} {y + amp*math.sin((x/160) + i*0.7):.1f} "
        p.append(f'<path d="{d}" fill="none" stroke="{teal}" stroke-opacity="{max(0.08, 0.5 - i*0.016):.2f}" stroke-width="2.5"/>')
    # الهيكل
    p.append(f'<path d="M 330 1470 Q 800 1600 1290 1470 L 1330 1400 Q 800 1530 290 1400 Z" fill="{bg2}" stroke="{gold}" stroke-width="5"/>')
    p.append(f'<path d="M 290 1400 Q 800 1530 1330 1400" fill="none" stroke="{gold}" stroke-width="3" stroke-opacity="0.7"/>')
    p.append(f'<line x1="300" y1="1435" x2="1320" y2="1435" stroke="{gold}" stroke-width="2" stroke-opacity="0.5"/>')
    # الصاري والشراع المثلث
    a, b, c = (470, 1400), (1120, 440), (1210, 1400)
    p.append(f'<line x1="{b[0]}" y1="{b[1]}" x2="{b[0]}" y2="1440" stroke="{gold}" stroke-width="6"/>')
    p.append(f'<path d="M {a[0]} {a[1]} Q 700 880 {b[0]} {b[1]} L {c[0]} {c[1]} Z" fill="{teal}" fill-opacity="0.08" stroke="{gold}" stroke-width="5"/>')
    # شبكة العقد داخل الشراع
    pts = []
    step = 50
    for y in range(b[1] + 40, a[1], step):
        for x in range(a[0], c[0], step):
            jx, jy = x + rnd.uniform(-12, 12), y + rnd.uniform(-12, 12)
            if inside_triangle((jx, jy), a, b, c) and (jx - a[0]) > 0.0:
                # استبعاد ما يقع خارج الحافة المنحنية تقريبياً
                tt = (jy - b[1]) / (a[1] - b[1])
                xmin = b[0] + (a[0] - b[0]) * tt + (1 - abs(2*tt - 1)) * 60
                if jx >= xmin:
                    pts.append((jx, jy))
    for i, (x1, y1) in enumerate(pts):
        near = sorted(pts, key=lambda q: (q[0]-x1)**2 + (q[1]-y1)**2)[1:4]
        for (x2, y2) in near:
            p.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{teal}" stroke-width="1.8" stroke-opacity="0.6"/>')
    for (x1, y1) in pts:
        lit = rnd.random() < 0.12
        p.append(f'<circle cx="{x1:.0f}" cy="{y1:.0f}" r="{7 if lit else 4}" fill="{gold if lit else teal}" fill-opacity="{0.95 if lit else 0.7}"/>')
    # العنوان في الأعلى
    tb, yy = title_block(title, subtitle, 300, cream, SERIF, size=170, sub_size=60, sub_color="#BFE9E3")
    p.append(tb)
    p.append(f'<line x1="330" y1="{yy+100}" x2="{W-330}" y2="{yy+100}" stroke="{gold}" stroke-width="3"/>')
    p.append(text(W / 2, H - 170, AUTHOR, 70, SERIF, cream, weight="normal"))
    return "\n".join(p)


def design_kufi(title, subtitle):
    """المتاهة الكوفية: متاهة من خطوط ذهبية سميكة تشبه الكوفي المربع ودوائر الطباعة معاً، ولوحة عنوان في المركز."""
    rnd = random.Random(5)
    bg, gold, panel, ink = "#0B2B26", "#D9B44A", "#F4EBD0", "#0B2B26"
    p = [f'<rect width="{W}" height="{H}" fill="{bg}"/>']
    p.append('<defs><radialGradient id="kg" cx="50%" cy="50%" r="70%"><stop offset="0" stop-color="#124038"/>'
             f'<stop offset="1" stop-color="{bg}"/></radialGradient></defs>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#kg)"/>')
    cell = 64
    cols, rows = W // cell, H // cell
    px0, py0, px1, py1 = 150, 980, W - 150, 1720
    def blocked(cx_, cy_):
        x, y = cx_ * cell + cell / 2, cy_ * cell + cell / 2
        return px0 - 40 < x < px1 + 40 and py0 - 40 < y < py1 + 40
    visited = [[blocked(x, y) for y in range(rows)] for x in range(cols)]
    segs = []
    def carve(x, y):
        visited[x][y] = True
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        rnd.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and not visited[nx][ny]:
                segs.append(((x, y), (nx, ny)))
                carve(nx, ny)
    sys.setrecursionlimit(20000)
    for sx in range(cols):
        for sy in range(rows):
            if not visited[sx][sy]:
                carve(sx, sy)
    for (x1, y1), (x2, y2) in segs:
        X1, Y1 = x1 * cell + cell / 2, y1 * cell + cell / 2
        X2, Y2 = x2 * cell + cell / 2, y2 * cell + cell / 2
        d = math.hypot((X1 + X2) / 2 - W / 2, (Y1 + Y2) / 2 - H / 2)
        op = max(0.18, min(0.75, 0.85 - d / 2600))
        p.append(f'<line x1="{X1}" y1="{Y1}" x2="{X2}" y2="{Y2}" stroke="{gold}" stroke-width="22" stroke-opacity="{op:.2f}" stroke-linecap="square"/>')
    # عقد مضيئة متفرقة على أطراف المسارات
    for _ in range(60):
        x = rnd.randrange(cols) * cell + cell / 2
        y = rnd.randrange(rows) * cell + cell / 2
        if px0 - 60 < x < px1 + 60 and py0 - 60 < y < py1 + 60:
            continue
        p.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{panel}" fill-opacity="0.9"/>')
    # لوحة العنوان
    p.append(f'<rect x="{px0}" y="{py0}" width="{px1-px0}" height="{py1-py0}" fill="{panel}"/>')
    p.append(f'<rect x="{px0+22}" y="{py0+22}" width="{px1-px0-44}" height="{py1-py0-44}" fill="none" stroke="{bg}" stroke-width="3"/>')
    tb, yy = title_block(title, subtitle, 1240, ink, SERIF, size=165, sub_size=54, sub_color="#2F5C53")
    p.append(tb)
    p.append(f'<rect x="{px0+40}" y="{H-260}" width="{px1-px0-80}" height="140" fill="{bg}" stroke="{gold}" stroke-width="3"/>')
    # قفل صغير فوق اللوحة
    kx, ky = W / 2, py0 - 130
    p.append(f'<rect x="{kx-70}" y="{ky}" width="140" height="110" rx="14" fill="{panel}"/>')
    p.append(f'<path d="M {kx-45} {ky} v -45 a 45 45 0 0 1 90 0 v 45" fill="none" stroke="{panel}" stroke-width="18"/>')
    p.append(f'<circle cx="{kx}" cy="{ky+48}" r="16" fill="{bg}"/>')
    p.append(text(W / 2, H - 165, AUTHOR, 70, SERIF, panel, weight="normal"))
    return "\n".join(p)




GEO = HERE / "geo"
GCC = ["KWT", "SAU", "ARE", "QAT", "BHR", "OMN"]
NEIGHBORS = ["IRN", "IRQ", "YEM", "JOR", "EGY", "SYR"]
CAPITALS = {"الكويت": (47.98, 29.37), "الرياض": (46.72, 24.69), "أبوظبي": (54.37, 24.45),
            "الدوحة": (51.53, 25.29), "المنامة": (50.59, 26.23), "مسقط": (58.59, 23.59)}


def country_masks(project, size):
    """يرسم كل دولة في قناع صورة ليُفحص موقع كل نقطة بسرعة."""
    import json
    from PIL import Image, ImageDraw
    masks = {}
    for code in GCC + NEIGHBORS:
        path = GEO / f"{code}.geojson"
        if not path.exists():
            continue
        img = Image.new("1", size, 0)
        draw = ImageDraw.Draw(img)
        data = json.loads(path.read_text(encoding="utf-8"))
        for feat in data["features"]:
            geom = feat["geometry"]
            polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
            for poly in polys:
                ring = poly[0]
                pts = [project(lon, lat) for lon, lat in ring]
                if len(pts) > 2:
                    draw.polygon(pts, fill=1)
        masks[code] = img.load()
    return masks


def design_gulfmap(title, subtitle):
    """خريطة الخليج النقطية: دول المجلس من نقاط ذهبية مضيئة وعواصمها عقد مترابطة بأقواس."""
    rnd = random.Random(31)
    bg1, bg2, gold, teal, cream, faint = "#071226", "#02050C", "#E2B93B", "#3FD6C8", "#F4EBD0", "#2A3A5C"
    k = 56.0
    lon0, lat0 = 33.5, 35.0
    cosl = math.cos(math.radians(24))
    def project(lon, lat):
        return ((lon - lon0) * cosl * k, (lat0 - lat) * k + 120)
    masks = country_masks(project, (W, H))
    p = ['<defs><radialGradient id="mg" cx="55%" cy="35%" r="65%">'
         f'<stop offset="0" stop-color="#12264A"/><stop offset="1" stop-color="{bg2}"/></radialGradient>'
         '<filter id="mglow"><feGaussianBlur stdDeviation="16"/></filter></defs>']
    p.append(f'<rect width="{W}" height="{H}" fill="{bg1}"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#mg)"/>')
    step = 19
    for y in range(140, 1560, step):
        for x in range(0, W, step):
            jx, jy = x + (step / 2 if (y // step) % 2 else 0), y
            if jx >= W:
                continue
            code = None
            for c in GCC:
                if masks.get(c) and masks[c][int(jx), int(jy)]:
                    code = c
                    break
            if code:
                t = (jy - 140) / 1400
                r_, g_, b_ = (int(0xE2 + (0x3F - 0xE2) * t), int(0xB9 + (0xD6 - 0xB9) * t), int(0x3B + (0xC8 - 0x3B) * t))
                p.append(f'<circle cx="{jx:.0f}" cy="{jy:.0f}" r="{rnd.uniform(4.2, 6.2):.1f}" fill="rgb({r_},{g_},{b_})" fill-opacity="{rnd.uniform(0.55, 1.0):.2f}"/>')
            else:
                for c in NEIGHBORS:
                    if masks.get(c) and masks[c][int(jx), int(jy)]:
                        p.append(f'<circle cx="{jx:.0f}" cy="{jy:.0f}" r="3" fill="{faint}" fill-opacity="0.55"/>')
                        break
    caps = {name: project(lon, lat) for name, (lon, lat) in CAPITALS.items()}
    names = list(caps)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            (x1, y1), (x2, y2) = caps[names[i]], caps[names[j]]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - abs(x2 - x1) * 0.25 - 40
            p.append(f'<path d="M {x1:.0f} {y1:.0f} Q {mx:.0f} {my:.0f} {x2:.0f} {y2:.0f}" fill="none" stroke="{teal}" stroke-width="2.2" stroke-opacity="0.55"/>')
    for name, (x, y) in caps.items():
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="34" fill="{teal}" fill-opacity="0.35" filter="url(#mglow)"/>')
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="13" fill="{cream}"/>')
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="24" fill="none" stroke="{cream}" stroke-width="2" stroke-opacity="0.7"/>')
    p.append(f'<line x1="260" y1="1640" x2="{W-260}" y2="1640" stroke="{gold}" stroke-width="3"/>')
    tb, yy = title_block(title, subtitle, 1860, "#FFFFFF", SANS, size=185, sub_size=60, sub_color=gold)
    p.append(tb)
    p.append(f'<line x1="260" y1="{yy+110}" x2="{W-260}" y2="{yy+110}" stroke="{gold}" stroke-width="3"/>')
    p.append(text(W / 2, H - 170, AUTHOR, 70, SANS, cream, weight="normal"))
    return "\n".join(p)


def design_textbook(title, subtitle):
    """المرجع الجامعي: خلفية فاتحة ولوح أزرق عميق ورمز أقواس متحدة المركز، على طراز الكتب الجامعية."""
    cream, blue, gold, ink = "#F6F1E7", "#0E2A47", "#D4A72C", "#111826"
    p = [f'<rect width="{W}" height="{H}" fill="{cream}"/>']
    p.append(f'<rect x="0" y="0" width="{W}" height="1380" fill="{blue}"/>')
    # أقواس ربع دائرية من الزاوية اليمنى العليا ترمز إلى موجات الرصد
    for i, r in enumerate(range(160, 1500, 150)):
        p.append(f'<path d="M {W} {r} A {r} {r} 0 0 0 {W - r} 0" fill="none" stroke="{gold}" stroke-width="{3 if i % 2 else 7}" stroke-opacity="{0.9 - i*0.08:.2f}"/>')
    # شبكة نقاط خافتة أسفل اللوح
    for y in range(60, 1340, 46):
        for x in range(60, 700, 46):
            p.append(f'<circle cx="{x}" cy="{y}" r="2.2" fill="{cream}" fill-opacity="0.16"/>')
    # قفل تخطيطي
    kx, ky = 330, 560
    p.append(f'<rect x="{kx-170}" y="{ky}" width="340" height="270" rx="26" fill="none" stroke="{gold}" stroke-width="12"/>')
    p.append(f'<path d="M {kx-105} {ky} v -120 a 105 105 0 0 1 210 0 v 120" fill="none" stroke="{gold}" stroke-width="12"/>')
    p.append(f'<circle cx="{kx}" cy="{ky+118}" r="36" fill="{gold}"/>')
    p.append(f'<rect x="{kx-14}" y="{ky+118}" width="28" height="80" fill="{gold}"/>')
    # شريط ذهبي رفيع يفصل اللوح
    p.append(f'<rect x="0" y="1380" width="{W}" height="16" fill="{gold}"/>')
    tb, yy = title_block(title, subtitle, 1680, ink, SANS, size=150, sub_size=58, sub_color="#3B4A63")
    p.append(tb)
    p.append(f'<rect x="{W/2-120}" y="{yy+70}" width="240" height="8" fill="{gold}"/>')
    p.append(text(W / 2, H - 170, AUTHOR, 70, SANS, ink, weight="normal"))
    return "\n".join(p)


def design_fingerprint(title, subtitle):
    """البصمة: بصمة ذهبية من خطوط متحدة المركز تتحول أطرافها إلى مسارات دوائر إلكترونية."""
    rnd = random.Random(17)
    bg1, bg2, gold, white = "#060A12", "#000000", "#D9B44A", "#FFFFFF"
    p = ['<defs><radialGradient id="fg" cx="50%" cy="34%" r="60%"><stop offset="0" stop-color="#14192B"/>'
         f'<stop offset="1" stop-color="{bg2}"/></radialGradient></defs>']
    p.append(f'<rect width="{W}" height="{H}" fill="url(#fg)"/>')
    cx, cy = W / 2, 820
    for i, r in enumerate(range(40, 560, 26)):
        ry = r * 1.28
        start = rnd.uniform(0, 360)
        arcs = rnd.randint(2, 4)
        gaps = sorted(rnd.uniform(0, 360) for _ in range(arcs))
        for gi in range(arcs):
            a0 = gaps[gi] + 8
            a1 = (gaps[(gi + 1) % arcs] if gi + 1 < arcs else gaps[0] + 360) - 8
            if a1 - a0 < 20:
                continue
            x0, y0 = cx + r * math.cos(math.radians(a0)), cy + ry * math.sin(math.radians(a0))
            x1, y1 = cx + r * math.cos(math.radians(a1)), cy + ry * math.sin(math.radians(a1))
            large = 1 if a1 - a0 > 180 else 0
            op = 0.95 - i * 0.025
            p.append(f'<path d="M {x0:.1f} {y0:.1f} A {r} {ry} 0 {large} 1 {x1:.1f} {y1:.1f}" fill="none" stroke="{gold}" stroke-width="11" stroke-opacity="{op:.2f}" stroke-linecap="round"/>')
    # مسارات تخرج من البصمة إلى الأطراف
    for ang in (15, 35, 155, 165, 200, 340):
        a = math.radians(ang)
        r0 = 560
        x0, y0 = cx + r0 * math.cos(a), cy + r0 * 1.28 * math.sin(a)
        x1 = x0 + (260 if math.cos(a) > 0 else -260)
        y1 = y0
        x2 = x1 + (90 if math.cos(a) > 0 else -90)
        y2 = y1 + rnd.choice([-90, 90])
        p.append(f'<polyline points="{x0:.0f},{y0:.0f} {x1:.0f},{y1:.0f} {x2:.0f},{y2:.0f}" fill="none" stroke="{gold}" stroke-width="5" stroke-opacity="0.7"/>')
        p.append(f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="11" fill="{gold}"/>')
    p.append(f'<line x1="260" y1="1640" x2="{W-260}" y2="1640" stroke="{gold}" stroke-width="3"/>')
    tb, yy = title_block(title, subtitle, 1860, white, SANS, size=185, sub_size=60, sub_color=gold)
    p.append(tb)
    p.append(f'<line x1="260" y1="{yy+110}" x2="{W-260}" y2="{yy+110}" stroke="{gold}" stroke-width="3"/>')
    p.append(text(W / 2, H - 170, AUTHOR, 70, SANS, "#F3E9D2", weight="normal"))
    return "\n".join(p)




SITE = "3li.info"
YEAR = "2026"


def gulf_dots(p, rnd, k, dx, dy, gcc_from, gcc_to, faint_color, faint_opacity, top, bottom, step=19, neighbors=None):
    """يرسم دول المجلس بنقاط متدرجة اللون ودول الجوار بنقاط خافتة، ويعيد مواقع العواصم."""
    cosl = math.cos(math.radians(24))
    lon0, lat0 = 33.5, 35.0
    def project(lon, lat):
        return ((lon - lon0) * cosl * k + dx, (lat0 - lat) * k + dy)
    masks = country_masks(project, (W, H))
    for y in range(top, bottom, step):
        for x in range(0, W, step):
            jx, jy = x + (step / 2 if (y // step) % 2 else 0), y
            if jx >= W or jy >= H:
                continue
            code = None
            for c in GCC:
                if masks.get(c) and masks[c][int(jx), int(jy)]:
                    code = c
                    break
            if code:
                t = min(1.0, max(0.0, (jy - top) / (bottom - top)))
                col = tuple(int(gcc_from[i] + (gcc_to[i] - gcc_from[i]) * t) for i in range(3))
                p.append(f'<circle cx="{jx:.0f}" cy="{jy:.0f}" r="{rnd.uniform(4.4, 6.4):.1f}" fill="rgb{col}" fill-opacity="{rnd.uniform(0.6, 1.0):.2f}"/>')
            else:
                for c in (neighbors or NEIGHBORS):
                    if masks.get(c) and masks[c][int(jx), int(jy)]:
                        p.append(f'<circle cx="{jx:.0f}" cy="{jy:.0f}" r="3" fill="{faint_color}" fill-opacity="{faint_opacity}"/>')
                        break
    return {name: project(lon, lat) for name, (lon, lat) in CAPITALS.items()}


def design_final(title, subtitle):
    """الغلاف المعتمد: الطراز الجامعي الفاتح مع خريطة الخليج النقطية داخل اللوح الأزرق."""
    rnd = random.Random(31)
    cream, blue, blue2, gold, ink, teal, white = "#F6F1E7", "#0E2A47", "#163B63", "#D4A72C", "#111826", "#3FD6C8", "#F4EBD0"
    panel_h = 1500
    p = ['<defs><radialGradient id="pg" cx="52%" cy="42%" r="70%">'
         f'<stop offset="0" stop-color="{blue2}"/><stop offset="1" stop-color="{blue}"/></radialGradient>'
         '<filter id="cglow"><feGaussianBlur stdDeviation="16"/></filter></defs>']
    p.append(f'<rect width="{W}" height="{H}" fill="{cream}"/>')
    p.append(f'<rect x="0" y="0" width="{W}" height="{panel_h}" fill="url(#pg)"/>')
    # أقواس خافتة في الزاوية اليمنى العليا
    for i, r in enumerate(range(220, 1500, 170)):
        p.append(f'<path d="M {W} {r} A {r} {r} 0 0 0 {W - r} 0" fill="none" stroke="{gold}" stroke-width="{2 if i % 2 else 4}" stroke-opacity="{max(0.08, 0.4 - i*0.05):.2f}"/>')
    # الخريطة
    caps = gulf_dots(p, rnd, k=54, dx=150, dy=210, gcc_from=(0xE8, 0xC2, 0x4A), gcc_to=(0x3F, 0xD6, 0xC8),
                     faint_color="#4F6E95", faint_opacity=0.38, top=120, bottom=panel_h - 40,
                     neighbors=("IRN", "IRQ", "JOR", "YEM"))
    names = list(caps)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            (x1, y1), (x2, y2) = caps[names[i]], caps[names[j]]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - abs(x2 - x1) * 0.25 - 40
            p.append(f'<path d="M {x1:.0f} {y1:.0f} Q {mx:.0f} {my:.0f} {x2:.0f} {y2:.0f}" fill="none" stroke="{teal}" stroke-width="2.4" stroke-opacity="0.6"/>')
    for name, (x, y) in caps.items():
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="36" fill="{teal}" fill-opacity="0.4" filter="url(#cglow)"/>')
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="13" fill="{white}"/>')
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="25" fill="none" stroke="{white}" stroke-width="2" stroke-opacity="0.75"/>')
    # الشريط الذهبي الفاصل
    p.append(f'<rect x="0" y="{panel_h}" width="{W}" height="16" fill="{gold}"/>')
    # العنوان
    tb, yy = title_block(title, subtitle, 1760, ink, SANS, size=150, sub_size=58, sub_color="#3B4A63")
    p.append(tb)
    p.append(f'<rect x="{W/2-120}" y="{yy+70}" width="240" height="8" fill="{gold}"/>')
    # المؤلف والموقع والحقوق
    p.append(text(W / 2, H - 250, AUTHOR, 72, SANS, ink, weight="normal"))
    p.append(f'<text x="{W/2}" y="{H-170}" font-family="{SANS}" font-size="46" fill="#9A7A1E" text-anchor="middle" '
             f'font-weight="normal">{SITE}</text>')
    p.append(f'<text x="{W/2}" y="{H-100}" font-family="{SANS}" font-size="34" fill="#6B7383" text-anchor="middle" '
             f'font-weight="normal">&#169; {YEAR}</text>')
    return "\n".join(p)


DESIGNS = {"sadu": design_sadu, "star": design_star, "dial": design_dial,
           "shield": design_shield, "dhow": design_dhow, "kufi": design_kufi,
           "gulfmap": design_gulfmap, "textbook": design_textbook, "fingerprint": design_fingerprint,
           "final": design_final}
DEFAULTS = {
    "sadu": ("مَعْقِل", "المرجع الشامل في أمن المعلومات والأمن السيبراني"),
    "star": ("قَلْعَة", "أمن المعلومات من الخليج إلى الخليج"),
    "dial": ("أمن المعلومات: المرجع الخليجي الشامل", "الأسس والضوابط والعمليات والتنظيم"),
    "shield": ("حِمى", "المرجع الشامل في أمن المعلومات والأمن السيبراني"),
    "dhow": ("العُمدة في أمن المعلومات", "من الخليج إلى الخليج"),
    "kufi": ("الجامع في أمن المعلومات", "الأسس والضوابط والعمليات والتنظيم في دول الخليج"),
    "gulfmap": ("دَرْوازَة", "المرجع الشامل في أمن المعلومات والأمن السيبراني"),
    "textbook": ("المرجع الخليجي الشامل في الأمن السيبراني", "الأسس والضوابط والعمليات والتنظيم"),
    "fingerprint": ("مَناعَة", "المرجع الخليجي في أمن المعلومات والأمن السيبراني"),
    "final": ("المرجع الخليجي الشامل في الأمن السيبراني", "الأسس والضوابط والعمليات والتنظيم"),
}


def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'{body}\n</svg>\n')


def render(svg_path, png_path):
    script = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const browser = await chromium.launch({{ executablePath: process.env.PW_CHROME || undefined, args: ['--no-sandbox'] }});
  const page = await browser.newPage({{ viewport: {{ width: {W}, height: {H} }}, deviceScaleFactor: 1 }});
  await page.goto('file://{svg_path}');
  await page.waitForTimeout(400);
  await page.screenshot({{ path: '{png_path}', clip: {{ x: 0, y: 0, width: {W}, height: {H} }} }});
  await browser.close();
}})();
"""
    subprocess.run(["node", "-e", script], check=True)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--title")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--design", choices=list(DESIGNS))
    args = ap.parse_args(argv)
    OUT.mkdir(exist_ok=True)
    jobs = [args.design] if args.design else list(DESIGNS)
    for name in jobs:
        title, subtitle = DEFAULTS[name]
        if args.title:
            title, subtitle = args.title, args.subtitle
        body = DESIGNS[name](title, subtitle)
        svg_path = OUT / f"{name}.svg"
        svg_path.write_text(svg(body), encoding="utf-8")
        png_path = OUT / f"{name}.png"
        render(svg_path, png_path)
        try:
            from PIL import Image
            Image.open(png_path).convert("RGB").save(OUT / f"{name}.jpg", quality=92)
            if name == "final":
                Image.open(png_path).convert("RGB").save(HERE / "ebook-cover.jpg", quality=94)
        except ImportError:
            pass
        print("wrote", png_path)


if __name__ == "__main__":
    main(sys.argv[1:])
