#!/usr/bin/env python3
"""يولد أشكال الكتاب التوضيحية بصيغة SVG ثم PNG من أربعة أنماط: دورة وسلسلة وطبقات ومثلث.

الاستخدام:
  python3 tools/figures/make_figures.py            يولد كل الأشكال في figures/
  python3 tools/figures/make_figures.py f03        يولد شكلاً واحداً باسمه
"""
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "figures"
W, H = 1200, 700
BLUE, BLUE2, GOLD, TEAL, INK, LIGHT = "#0E2A47", "#1F4E79", "#D4A72C", "#2A9D8F", "#1A2330", "#EEF2F7"
FONT = "IBM Plex Sans Arabic"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(body, w=W, h=H):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>'
            f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>{body}</svg>')


def text(x, y, s, size=30, fill="#FFFFFF", weight="bold", anchor="middle"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" direction="rtl">{esc(s)}</text>')


def wrapped(x, y, s, size, fill, max_chars=16, weight="bold"):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    out = []
    y0 = y - (len(lines) - 1) * size * 0.65
    for i, line in enumerate(lines):
        out.append(text(x, y0 + i * size * 1.3, line, size, fill, weight))
    return "".join(out)


def box(x, y, w, h, label, fill=BLUE, size=28, max_chars=16, textfill="#FFFFFF"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}"/>'
            + wrapped(x + w / 2, y + h / 2 + size * 0.35, label, size, textfill, max_chars))


def arrow(x1, y1, x2, y2, width=4):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="{width}" marker-end="url(#arrow)"/>'


def chain(steps, numbered=True):
    """سلسلة من اليمين إلى اليسار."""
    n = len(steps)
    margin, gap = 40, 34
    bw = (W - 2 * margin - gap * (n - 1)) / n
    bh = 150
    y = (H - bh) / 2
    body = []
    for i, s in enumerate(steps):
        x = W - margin - bw - i * (bw + gap)
        label = f"{i + 1}. {s}" if numbered else s
        body.append(box(x, y, bw, bh, label, fill=BLUE if i % 2 == 0 else BLUE2, size=24, max_chars=12))
        if i < n - 1:
            body.append(arrow(x - 4, y + bh / 2, x - gap + 6, y + bh / 2))
    return "".join(body)


def cycle(steps):
    """دورة بعقارب الساعة حول مركز."""
    n = len(steps)
    cx, cy, r = W / 2, H / 2, 240
    body = []
    pts = []
    for i in range(n):
        ang = -math.pi / 2 - 2 * math.pi * i / n
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    for i, (x, y) in enumerate(pts):
        nx, ny = pts[(i + 1) % n]
        mx, my = (x + nx) / 2, (y + ny) / 2
        vx, vy = mx - cx, my - cy
        d = math.hypot(vx, vy)
        bx, by = cx + vx / d * (r + 40), cy + vy / d * (r + 40)
        body.append(f'<path d="M {x} {y} Q {bx} {by} {nx} {ny}" fill="none" stroke="{INK}" stroke-width="4" marker-end="url(#arrow)"/>')
    for i, (x, y) in enumerate(pts):
        bw, bh = 230, 96
        body.append(box(x - bw / 2, y - bh / 2, bw, bh, f"{i + 1}. {steps[i]}", fill=BLUE if i % 2 == 0 else TEAL, size=26, max_chars=14))
    body.append(f'<circle cx="{cx}" cy="{cy}" r="78" fill="{GOLD}"/>')
    return "".join(body)


def layers(rows, pyramid=False):
    """طبقات من الأعلى إلى الأسفل، وبخيار الهرم تتسع الطبقات نزولاً."""
    n = len(rows)
    top, bottom = 40, H - 40
    gap = 14
    rh = (bottom - top - gap * (n - 1)) / n
    body = []
    for i, (label, fill) in enumerate(rows):
        y = top + i * (rh + gap)
        if pyramid:
            w = 420 + (W - 520) * (i + 1) / n
        else:
            w = W - 120
        x = (W - w) / 2
        body.append(box(x, y, w, rh, label, fill=fill, size=28, max_chars=44))
    return "".join(body)


def triangle(labels, center):
    cx, cy = W / 2, H / 2 + 20
    r = 250
    pts = [(cx, cy - r), (cx + r * 0.95, cy + r * 0.55), (cx - r * 0.95, cy + r * 0.55)]
    body = [f'<polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="{LIGHT}" stroke="{BLUE}" stroke-width="6"/>']
    for (x, y), label in zip(pts, labels):
        body.append(f'<circle cx="{x}" cy="{y}" r="74" fill="{BLUE}"/>')
        body.append(text(x, y + 12, label, 30))
    body.append(f'<circle cx="{cx}" cy="{cy + 40}" r="70" fill="{GOLD}"/>')
    body.append(text(cx, cy + 52, center, 30, INK))
    return "".join(body)


FIGURES = {
    "f01-cia": lambda: triangle(["السرية", "السلامة", "التوافر"], "المعلومات"),
    "f02-killchain": lambda: chain(["الاستطلاع", "التسليح", "التسليم", "الاستغلال", "التثبيت", "القيادة والتحكم", "تحقيق الأهداف"]),
    "f03-riskcycle": lambda: cycle(["السياق", "التحديد", "التحليل", "التقييم", "المعالجة", "المراقبة"]),
    "f04-pyramid": lambda: layers([("السياسات: إرادة الإدارة، قصيرة وتتغير نادراً", BLUE),
                                   ("المعايير: متطلبات قابلة للقياس تتغير مع التقنية", BLUE2),
                                   ("الإجراءات: خطوات التنفيذ تتغير مع الأنظمة والأشخاص", TEAL),
                                   ("الإرشادات: ممارسات مستحسنة غير ملزمة", "#5C6B7A")], pyramid=True),
    "f05-pki": lambda: chain(["جهة الجذر المثبتة في الأنظمة", "جهة إصدار وسيطة", "شهادة الموقع أو الشخص", "المتصفح يتحقق من السلسلة"]),
    "f06-iaaa": lambda: chain(["التعريف: من تدعي أنك هو", "المصادقة: أثبت ذلك", "التخويل: ماذا يحق لك", "المساءلة: ما الذي فعلته"]),
    "f07-zones": lambda: layers([("الإنترنت والشركاء: منطقة غير موثوقة", "#5C6B7A"),
                                 ("المنطقة منزوعة السلاح: الأنظمة المواجهة للإنترنت", BLUE2),
                                 ("الشبكة الداخلية: الموظفون والخوادم والإدارة في مناطق منفصلة", BLUE),
                                 ("الأنظمة الحرجة والصناعية: معزولة ولا يصلها إلا من يحتاج", TEAL)]),
    "f08-vulncycle": lambda: cycle(["الاكتشاف", "ترتيب الأولويات", "المعالجة", "التحقق"]),
    "f09-sdlc": lambda: chain(["المتطلبات الأمنية", "التصميم ونمذجة التهديدات", "الكتابة الآمنة والمراجعة", "الاختبار الآلي واليدوي", "الإطلاق ومراجعة الإعدادات", "التشغيل والمراقبة"]),
    "f10-shared": lambda: layers([("البيانات وتصنيفها وتشفيرها: العميل في كل النماذج", TEAL),
                                  ("الهويات والصلاحيات والإعدادات: العميل في كل النماذج", TEAL),
                                  ("التطبيق: العميل في البنية التحتية والمنصة، والمزود في البرمجيات كخدمة", BLUE2),
                                  ("نظام التشغيل والمحرك: العميل في البنية التحتية، والمزود فيما عداها", BLUE2),
                                  ("المباني والعتاد والشبكة الأساسية: المزود في كل النماذج", BLUE)]),
    "f11-datalifecycle": lambda: cycle(["الجمع", "التخزين", "الاستخدام", "المشاركة", "الأرشفة", "الإتلاف"]),
    "f13-socflow": lambda: chain(["السجلات من المصادر", "التجميع والتوحيد", "الربط والكشف", "التصنيف والتحقيق", "الاحتواء والاستجابة", "الضبط والتحسين"]),
    "f14-ircycle": lambda: cycle(["الاستعداد", "الكشف والتحليل", "الاحتواء والاستئصال والتعافي", "النشاط اللاحق والدروس"]),
    "f15-resilience": lambda: cycle(["الخدمات الحرجة والتحمل", "تحليل أثر الأعمال", "استراتيجيات التعافي", "الخطط الثلاث", "التمارين والاختبار", "التحسين"]),
    "f16-culture": lambda: layers([("التوعية: أن يعرف الموظف ما التهديد", "#5C6B7A"),
                                   ("السلوك: أن يتوقف قبل الضغط ويبلغ خلال دقائق", BLUE2),
                                   ("الثقافة: أن يكون الإبلاغ عن الخطأ أمراً طبيعياً يُشكر عليه", BLUE)], pyramid=True),
    "f12-purdue": lambda: layers([("المستويان الرابع والخامس: شبكة المؤسسة والإنترنت", "#5C6B7A"),
                                  ("المنطقة منزوعة السلاح الصناعية: لا اتصال مباشر يتجاوزها", GOLD),
                                  ("المستوى الثالث: إدارة العمليات في الموقع", BLUE2),
                                  ("المستوى الثاني: الإشراف والتحكم وواجهات المشغلين", BLUE),
                                  ("المستوى الأول: وحدات التحكم المنطقية المبرمجة", BLUE),
                                  ("المستوى صفر: المستشعرات والمشغلات والعملية الفيزيائية", TEAL)]),
}


def render(svg_path, png_path):
    script = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const browser = await chromium.launch({{ executablePath: process.env.PW_CHROME || undefined, args: ['--no-sandbox'] }});
  const page = await browser.newPage({{ viewport: {{ width: {W}, height: {H} }}, deviceScaleFactor: 2 }});
  await page.goto('file://{svg_path}');
  await page.waitForTimeout(300);
  await page.screenshot({{ path: '{png_path}', clip: {{ x: 0, y: 0, width: {W}, height: {H} }} }});
  await browser.close();
}})();
"""
    subprocess.run(["node", "-e", script], check=True)


def main(argv):
    OUT.mkdir(exist_ok=True)
    names = [n for n in FIGURES if not argv or any(n.startswith(a) for a in argv)]
    for name in names:
        body = FIGURES[name]()
        svg_path = OUT / f"{name}.svg"
        svg_path.write_text(svg(body), encoding="utf-8")
        render(svg_path, OUT / f"{name}.png")
        print("wrote", name)


if __name__ == "__main__":
    main(sys.argv[1:])
