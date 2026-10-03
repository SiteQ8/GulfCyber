#!/usr/bin/env python3
"""يولد غلاف النسخة الورقية الكامل (الوجه والكعب والخلف) بصيغة PDF بالمقاس الدقيق.

الكتاب من اليمين إلى اليسار، فالوجه على يسار اللوحة والخلف على يمينها والكعب بينهما.

الاستخدام:
  python3 cover/make_print_cover.py --pages 325 --per-page 0.0025
  --per-page عرض الورقة الواحدة بالبوصة من قالب المطبعة (0.0025 للورق الكريمي عادة و0.002252 للأبيض)
"""
import argparse
import base64
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TRIM_W, TRIM_H, BLEED = 6.0, 9.0, 0.125
TITLE = "المرجع الخليجي الشامل في الأمن السيبراني"
SUBTITLE = "الأسس والضوابط والعمليات والتنظيم"
AUTHOR = "علي العنزي"
BLURB = [
    "كتاب عربي شامل في أمن المعلومات والأمن السيبراني كُتب من الخليج إلى الخليج، يجمع الأساس النظري والممارسة العملية والسياق التنظيمي لدول مجلس التعاون في مرجع واحد يصلح للمقرر الجامعي ولبرامج التأهيل الحكومية وللممارس في الميدان.",
    "تسعة عشر فصلاً في أربعة أبواب تتدرج من الأسس إلى الآفاق، يبدأ كل فصل بأهداف تعلم ويُختم بأخطاء شائعة وقائمة تحقق وخلاصة وجدول مصطلحات وخريطة إلى الأطر الدولية والخليجية وأسئلة وتمارين ومصادر، مع ثلاثة وعشرين شكلاً ودراسات حالة من واقع المنطقة، وملاحق فيها قائمة تحقق للمؤسسة الصغيرة ومسرد يضم أكثر من مئتي مصطلح.",
    "يضع الكتاب إطار بنك الكويت المركزي الجديد والضوابط الأساسية السعودية ومعيار ضمان المعلومات في قطر وقوانين حماية البيانات في الدول الست في موضعها من كل فصل، ويرافقه موقع فيه فصل مجاني ومستودع مفتوح بالتدريبات والقوالب والأشكال.",
]
BIO = "علي العنزي مهندس وقيادي في أمن المعلومات، يقود أعمال هندسة الأمن في إحدى كبرى المؤسسات المالية في الكويت، ويرأس لجاناً لمخاطر الأمن السيبراني في القطاع المالي في الكويت والخليج، وهو عضو مجلس إدارة سابق في إحدى كبرى شركات تكنولوجيا المعلومات في الكويت."


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


ISBN = "9798178685440"
SITE = "https://gulfcyber.3li.info"

L_CODES = ["0001101", "0011001", "0010011", "0111101", "0100011", "0110001", "0101111", "0111011", "0110111", "0001011"]
G_CODES = ["0100111", "0110011", "0011011", "0100001", "0011101", "0111001", "0000101", "0010001", "0001001", "0010111"]
R_CODES = ["1110010", "1100110", "1101100", "1000010", "1011100", "1001110", "1010000", "1000100", "1001000", "1110100"]
PARITY = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG", "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]


def ean13_check(d12):
    total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(d12))
    return str((10 - total % 10) % 10)


def ean13_svg(code, width_in=1.9, height_in=0.95):
    """باركود EAN-13 كصورة SVG بالمقاس المطلوب مع الأرقام تحته."""
    assert len(code) == 13 and code[-1] == ean13_check(code[:12]), "رقم غير صحيح"
    pattern = PARITY[int(code[0])]
    bits = "101"
    for i, ch in enumerate(code[1:7]):
        bits += (L_CODES if pattern[i] == "L" else G_CODES)[int(ch)]
    bits += "01010"
    for ch in code[7:]:
        bits += R_CODES[int(ch)]
    bits += "101"
    module = width_in / 113.0
    bar_h = height_in - 0.18
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_in}in" height="{height_in}in" viewBox="0 0 {width_in} {height_in}">',
           f'<rect width="{width_in}" height="{height_in}" fill="#fff"/>']
    x = module * 9
    guard = set(range(0, 3)) | set(range(45, 50)) | set(range(92, 95))
    for i, b in enumerate(bits):
        if b == "1":
            h = bar_h + (0.06 if i in guard else 0)
            out.append(f'<rect x="{x:.4f}" y="0.04" width="{module:.4f}" height="{h:.4f}" fill="#000"/>')
        x += module
    f = 'font-family="Noto Sans, DejaVu Sans, sans-serif" font-size="0.085" fill="#000"'
    out.append(f'<text x="{module*4:.3f}" y="{height_in-0.03:.3f}" {f}>{code[0]}</text>')
    out.append(f'<text x="{module*(9+3+21):.3f}" y="{height_in-0.03:.3f}" text-anchor="middle" {f} letter-spacing="0.012">{code[1:7]}</text>')
    out.append(f'<text x="{module*(9+3+42+5+21):.3f}" y="{height_in-0.03:.3f}" text-anchor="middle" {f} letter-spacing="0.012">{code[7:]}</text>')
    out.append("</svg>")
    return "".join(out)


def qr_svg(text, size_in=1.16):
    import qrcode
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=1)
    q.add_data(text)
    q.make(fit=True)
    m = q.get_matrix()
    n = len(m)
    cell = size_in / n
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size_in}in" height="{size_in}in" viewBox="0 0 {size_in} {size_in}">',
           f'<rect width="{size_in}" height="{size_in}" fill="#fff"/>']
    for r, row in enumerate(m):
        for c, v in enumerate(row):
            if v:
                out.append(f'<rect x="{c*cell:.4f}" y="{r*cell:.4f}" width="{cell:.4f}" height="{cell:.4f}" fill="#000"/>')
    out.append("</svg>")
    return "".join(out)


def svg_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def build_html(spine):
    total_w = TRIM_W * 2 + spine + BLEED * 2
    total_h = TRIM_H + BLEED * 2
    map_svg = data_uri(ROOT / "cover" / "gulf-map.svg", "image/svg+xml")
    photo = ROOT / "cover" / "author.jpg"
    photo_uri = data_uri(photo, "image/jpeg") if photo.exists() else ""
    blurb = "".join(f"<p>{p}</p>" for p in BLURB)
    return f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<style>
@page {{ size: {total_w}in {total_h}in; margin: 0; }}
html, body {{ margin:0; padding:0; width:{total_w}in; height:{total_h}in; font-family:"IBM Plex Sans Arabic", sans-serif; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
.wrap {{ position:relative; width:{total_w}in; height:{total_h}in; background:#0E2A47; overflow:hidden; }}
.panel {{ position:absolute; top:0; height:{total_h}in; }}
.front {{ left:0; width:{TRIM_W + BLEED}in; background:#0E2A47; }}
.spine {{ left:{TRIM_W + BLEED}in; width:{spine}in; background:#0A2039; }}
.back {{ left:{TRIM_W + BLEED + spine}in; width:{TRIM_W + BLEED}in; background:#0E2A47; }}
.map {{ position:absolute; left:0; top:0.9in; width:{TRIM_W + BLEED}in; height:4.6in; object-fit:contain; }}
.gold {{ position:absolute; left:0; width:100%; height:0.06in; background:#D4A72C; }}
.cream {{ position:absolute; left:0; right:0; bottom:0; height:3.55in; background:#F6F1E7; }}
.title {{ position:absolute; left:0.45in; right:0.45in; top:0.42in; text-align:center; font-size:0.42in; font-weight:700; line-height:1.35; color:#111826; }}
.subtitle {{ position:absolute; left:0; right:0; top:1.55in; text-align:center; font-size:0.17in; color:#3B4A63; }}
.rule {{ position:absolute; left:50%; margin-left:-0.35in; width:0.7in; height:0.03in; background:#D4A72C; top:1.95in; }}
.author {{ position:absolute; left:0; right:0; top:2.25in; text-align:center; font-size:0.24in; color:#111826; }}
.site {{ position:absolute; left:0; right:0; top:2.68in; text-align:center; font-size:0.14in; color:#9A7A1E; }}
.spine-text {{ position:absolute; left:50%; top:50%; transform:translate(-50%,-50%) rotate(-90deg); transform-origin:center; white-space:nowrap; color:#F4EBD0; font-size:{min(0.19, spine * 0.42):.3f}in; font-weight:700; }}
.spine-text span {{ color:#D4A72C; font-weight:500; margin-right:0.5in; }}
.back .inner {{ position:absolute; left:{BLEED + 0.55}in; right:0.55in; top:0.75in; bottom:1.7in; color:#F4EBD0; }}
.back h2 {{ font-size:0.26in; margin:0 0 0.18in; color:#D4A72C; font-weight:700; }}
.back p {{ font-size:0.146in; line-height:1.75; margin:0 0 0.12in; }}
.bio {{ position:absolute; left:{BLEED + 0.55}in; right:0.55in; bottom:2.05in; display:flex; gap:0.18in; align-items:center; color:#F4EBD0; font-size:0.125in; line-height:1.6; border-top:1px solid rgba(212,167,44,.6); padding-top:0.15in; }}
.bio img {{ width:0.85in; height:0.85in; border-radius:50%; object-fit:cover; border:2px solid #D4A72C; flex:none; }}
.barcode {{ position:absolute; right:0.45in; bottom:0.45in; width:2.05in; height:1.32in; background:#fff; border-radius:0.04in; display:flex; flex-direction:column; align-items:center; justify-content:center; }}
.barcode .isbn {{ font-family:"Noto Sans", sans-serif; font-size:0.1in; color:#000; direction:ltr; margin-bottom:0.02in; }}
.qr {{ position:absolute; left:{BLEED + 0.55}in; right:2.75in; bottom:0.45in; display:flex; direction:ltr; align-items:center; gap:0.18in; color:#F4EBD0; font-size:0.125in; line-height:1.6; }}
.qr div {{ direction:rtl; text-align:right; }}
.qr img {{ width:1.32in; height:1.32in; background:#fff; padding:0.08in; box-sizing:border-box; border-radius:0.04in; }}
.backmap {{ position:absolute; right:-1.2in; bottom:0.6in; width:4.2in; opacity:.14; }}
</style></head><body><div class="wrap">
<div class="panel front">
  <img class="map" src="{map_svg}">
  <div class="gold" style="top:{total_h - 3.55 - 0.06}in"></div>
  <div class="cream">
    <div class="title">{TITLE}</div>
    <div class="subtitle">{SUBTITLE}</div>
    <div class="rule"></div>
    <div class="author">{AUTHOR}</div>
    <div class="site">3li.info</div>
  </div>
</div>
<div class="panel spine"><div class="spine-text">{TITLE} <span>{AUTHOR}</span></div></div>
<div class="panel back">
  <img class="backmap" src="{map_svg}">
  <div class="inner"><h2>من الخليج إلى الخليج</h2>{blurb}</div>
  <div class="bio">{'<img src="' + photo_uri + '">' if photo_uri else ''}<div>{BIO}</div></div>
  <div class="qr"><img src="{svg_uri(qr_svg(SITE))}"><div>الفصل الأول مجاناً والتدريبات والقوالب<br><span style="color:#D4A72C">gulfcyber.3li.info</span></div></div>
  <div class="barcode"><div class="isbn">ISBN {ISBN}</div><img src="{svg_uri(ean13_svg(ISBN))}" style="width:1.9in;height:0.95in"></div>
</div>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, required=True)
    ap.add_argument("--per-page", type=float, default=0.0025, help="عرض الورقة بالبوصة من قالب المطبعة")
    ap.add_argument("--out", default=str(ROOT / "cover" / "print-cover.pdf"))
    a = ap.parse_args()
    spine = round(a.pages * a.per_page, 4)
    html = HERE / ".print-cover.html"
    html.write_text(build_html(spine), encoding="utf-8")
    total_w = TRIM_W * 2 + spine + BLEED * 2
    total_h = TRIM_H + BLEED * 2
    script = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const browser = await chromium.launch({{ executablePath: process.env.PW_CHROME || undefined, args: ['--no-sandbox'] }});
  const page = await browser.newPage();
  await page.goto('file://{html}');
  await page.waitForTimeout(500);
  await page.pdf({{ path: '{a.out}', width: '{total_w}in', height: '{total_h}in', printBackground: true, preferCSSPageSize: true, margin: {{top:'0',bottom:'0',left:'0',right:'0'}} }});
  await page.screenshot({{ path: '{str(a.out).replace('.pdf', '.png')}', fullPage: true }});
  await browser.close();
}})();
"""
    subprocess.run(["node", "-e", script], check=True)
    print(f"wrote {a.out} (spine {spine} in, sheet {total_w:.3f} x {total_h:.3f} in)")


if __name__ == "__main__":
    main()
