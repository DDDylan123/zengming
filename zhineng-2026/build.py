"""把《智能》读书笔记用到的手写汉字笔画注入 src.html，生成可直接打开的单文件页面。
笔画数据取自 Make Me a Hanzi 的 graphics.txt（Arphic 公共许可）。

  python3 zhineng-2026/build.py <graphics.txt>                → zhineng-2026/index.html
  python3 zhineng-2026/build.py <graphics.txt> --artifact <文件> → 去掉 doctype/html/head/body 外壳的版本（发布成 Artifact 用）
"""
import json, re, sys, pathlib
here = pathlib.Path(__file__).parent
src = (here / "src.html").read_text(encoding="utf-8")
# 只有 data-t 里的字会手写
need = set(re.findall(r"[一-鿿]", "".join(re.findall(r'data-t="([^"]*)"', src))))
compact = lambda p: re.sub(r"\s*([MLQCZ])\s*", r"\1", p)
han = {}
for line in open(sys.argv[1], encoding="utf-8"):
    d = json.loads(line)
    if d["character"] in need:
        han[d["character"]] = {"s": [compact(p) for p in d["strokes"]], "m": d["medians"]}
missing = sorted(need - set(han))
if missing:
    print("missing:", "".join(missing))
html = src.replace("/*__HANZI__*/", "const HANZI = " + json.dumps(han, ensure_ascii=False, separators=(",", ":")) + ";", 1)
out = here / "index.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html.encode()) // 1024} KB, {len(han)} glyphs)")
if "--artifact" in sys.argv:
    a = re.sub(r"<!doctype html>\s*<html[^>]*>\s*<head>\s*<meta charset[^>]*>\s*<meta name=\"viewport\"[^>]*>\s*", "", html, count=1)
    a = a.replace("</head>\n<body>\n", "", 1).replace("</body>\n</html>\n", "", 1)
    assert "<body" not in a and "<html" not in a
    pathlib.Path(sys.argv[sys.argv.index("--artifact") + 1]).write_text(a, encoding="utf-8")
