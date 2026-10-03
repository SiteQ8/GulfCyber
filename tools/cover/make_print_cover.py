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
BIO = "علي العنزي مهندس وقيادي في أمن المعلومات، يقود أعمال هندسة الأمن في أكبر مؤسسة مالية في الكويت ويرأس لجنة الأمن السيبراني في اتحاد مصارف الكويت."


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


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
.bio {{ position:absolute; left:{BLEED + 0.55}in; right:0.55in; bottom:1.85in; display:flex; gap:0.18in; align-items:center; color:#F4EBD0; font-size:0.125in; line-height:1.6; border-top:1px solid rgba(212,167,44,.6); padding-top:0.15in; }}
.bio img {{ width:0.85in; height:0.85in; border-radius:50%; object-fit:cover; border:2px solid #D4A72C; flex:none; }}
.backsite {{ position:absolute; left:0; right:0.55in; bottom:0.55in; text-align:right; color:#D4A72C; font-size:0.14in; }}
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
  <div class="bio">{'<img src="' + photo_uri + '">' if photo_uri else ''}<div>{BIO}<br><span style="color:#D4A72C">gulfcyber.3li.info</span></div></div>
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
