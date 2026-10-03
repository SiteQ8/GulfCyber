#!/usr/bin/env python3
"""يجمع جداول المصطلحات الأساسية من كل الفصول في ملحق المسرد مرتباً أبجدياً."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
rows = {}
for f in sorted(MAN.glob("*.md")):
    mm = re.match(r"\d\d-ch(\d\d)\.md$", f.name)
    if not mm:
        continue
    num = int(mm.group(1))
    text = f.read_text(encoding="utf-8")
    m = re.search(r"### المصطلحات الأساسية(?: \{[^}]*\})?\n\n\| المصطلح \| بالإنجليزية \|\n\|[-|]+\|\n((?:\|.*\|\n)+)", text)
    if not m:
        continue
    for line in m.group(1).strip().splitlines():
        ar, en = [c.strip() for c in line.strip("|").split("|")]
        rows.setdefault(ar, [en, set()])[1].add(num)
def key(s):
    return s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ال", "", 1) if s.startswith("ال") else s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
if len(rows) < 150:
    raise SystemExit(f"المسرد ناقص: {len(rows)} مصطلحاً فقط")
out = ["## مسرد المصطلحات {.unnumbered}", "",
       f"يجمع هذا المسرد {len(rows)} مصطلحاً أساسياً وردت في فصول الكتاب بالعربية وما يقابلها بالإنجليزية مع رقم الفصل الذي شُرح فيه كل مصطلح، ورُتبت أبجدياً بإهمال أداة التعريف.", "",
       "| المصطلح | بالإنجليزية | الفصل |", "|------------------------------|------------------------------|----------|"]
for ar in sorted(rows, key=key):
    en, nums = rows[ar]
    out.append(f"| {ar} | {en} | {'، '.join(str(n) for n in sorted(nums))} |")
out.append("")
(MAN / "82-appendix-glossary.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("terms:", len(rows))
