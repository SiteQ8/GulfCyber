# GulfCyber

الموقع والتدريبات والأدوات المرافقة لكتاب «المرجع الخليجي الشامل في الأمن السيبراني»، كتاب عربي من الخليج إلى الخليج في أمن المعلومات والأمن السيبراني للجامعات والجهات الحكومية والممارسين.

الموقع: [gulfcyber.3li.info](https://gulfcyber.3li.info)

الكتاب على أمازون: [amazon.com/dp/B0H6R5RR39](https://www.amazon.com/dp/B0H6R5RR39)

## ما في هذا المستودع

| المجلد | المحتوى |
|---|---|
| `docs/` | موقع الكتاب، وفي `docs/samples/` قارئ يفتح الكتاب ويقلب صفحات العينة المجانية من اليمين إلى اليسار مع نسخة PDF |
| `labs/` | تمارين كل فصل مع قوالب وبيانات تجريبية |
| `figures/` | أشكال الكتاب التوضيحية بصيغتي SVG وPNG |
| `tools/figures/` | مولد الأشكال من أربعة أنماط (دورة وسلسلة وطبقات ومثلث) بنص عربي |
| `tools/cover/` | مولد تصاميم الغلاف ومنها خريطة الخليج النقطية من بيانات الحدود الجغرافية |

نص الكتاب نفسه ليس في هذا المستودع.

## التدريبات

تجد في `labs/README.md` فهرساً بتمارين الفصول، ولكل فصل مجلد فيه التمارين وأسئلة المراجعة، ومع بعض الفصول قوالب جاهزة كسجل المخاطر وعينة قواعد جدار الحماية وجدول ترتيب الثغرات وجرد البيانات وورقة عمل نموذج بيردو.

## الأدوات

```
python3 tools/figures/make_figures.py          يولد كل الأشكال في figures/
python3 tools/cover/make_covers.py --design final   يولد الغلاف المعتمد بمقاس الكيندل
```

تحتاج الأدوات إلى Python 3 وNode مع Playwright وخطي IBM Plex Sans Arabic وAmiri، وتقرأ خريطة الخليج من ملفات geoBoundaries في `tools/cover/geo/` المرخصة برخصة ODbL.

## الرخص

- الشفرة في `tools/` برخصة MIT
- التمارين والأشكال في `labs/` و`figures/` برخصة CC BY-NC-SA 4.0، أي يجوز استخدامها وتعديلها في التعليم غير التجاري مع نسبة العمل إلى مؤلفه ومشاركة المشتقات بالرخصة نفسها
- بيانات الحدود الجغرافية من geoBoundaries برخصة ODbL

## English

Companion site, labs and tools for the Arabic book "The Comprehensive Gulf Reference in Cybersecurity". The book is available on Amazon at https://www.amazon.com/dp/B0H6R5RR39 and the manuscript itself is not in this repository. Labs are per chapter with templates and sample data, figures are generated from a small Python tool, and the dotted Gulf map on the cover is built from geoBoundaries data.
