#!/usr/bin/env bash
# فحص إتاحة النسخة الإلكترونية بأداة Ace من DAISY، يحتاج إلى تثبيت @daisy/ace ومتصفح كروميوم
set -e
OUT=${1:-/tmp/acereport}
rm -rf "$OUT"
PUPPETEER_EXECUTABLE_PATH=${PW_CHROME:-/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell} \
  ace-puppeteer -o "$OUT" "$(dirname "$0")/../dist/ebook.epub" > "$OUT.log" 2>&1
python3 - "$OUT" <<'PY'
import json, sys
r = json.load(open(sys.argv[1] + "/report.json"))
n = sum(len(d.get("assertions", [])) for d in r.get("assertions", []))
print("مخالفات الإتاحة:", n, "| النتيجة:", r.get("earl:result", {}).get("earl:outcome"))
sys.exit(1 if n else 0)
PY
