#!/bin/sh
# 把片子用到的字从完整字体里截出来，生成 fonts/*.woff2（国内打不开 Google Fonts，所以字体跟片子放在一起）
# 用法：sh subset_fonts.sh index.html fonts/   （需要 pip install fonttools brotli）
# 改了旁白、字卡或换了字体后都要重跑，否则新字会掉回系统字体
HTML="$1"; OUT="$2"; TMP=$(mktemp -d); mkdir -p "$OUT"
python3 -c "import sys;s=open(sys.argv[1],encoding='utf-8').read();c=set(ch for ch in s if ord(ch)>32)|set(map(chr,range(32,127)));open(sys.argv[2],'w').write(''.join(sorted(c)))" "$HTML" "$TMP/chars.txt"
CSS=$(curl -sS -A "Mozilla/5.0" "https://fonts.googleapis.com/css2?family=Fredoka:wght@500;700&family=ZCOOL+KuaiLe&family=Noto+Serif+SC:wght@600;900")
i=0
for name in fredoka-500 fredoka-700 serif-600 serif-900 kuaile; do
  i=$((i+1)); url=$(echo "$CSS" | grep -o "https://[^)]*\.ttf" | sed -n "${i}p")
  curl -sS -o "$TMP/$name.ttf" "$url"
  pyftsubset "$TMP/$name.ttf" --text-file="$TMP/chars.txt" --flavor=woff2 --layout-features='*' --output-file="$OUT/$name.woff2"
done
ls -la "$OUT"; rm -rf "$TMP"
