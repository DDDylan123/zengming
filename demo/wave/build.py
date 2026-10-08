"""把《巨浪》用到的汉字笔画数据注入 src.html，生成单文件页面。
笔画数据取自 Make Me a Hanzi 的 graphics.txt（Arphic 公共许可）。

  python3 demo/wave/build.py <graphics.txt>                 → demo/wave.html（字体走 Google Fonts）
  python3 demo/wave/build.py <graphics.txt> --site <目录>    → <目录>/index.html + <目录>/fonts/（字体自托管，给个人网站用）
"""
import json, re, sys, shutil, pathlib
here = pathlib.Path(__file__).parent
src = (here / "src.html").read_text(encoding="utf-8")
# 只收录字符串里的字：注释里的字不会画到画面上
strings = "".join(re.findall(r'"([^"\n]*)"', src) + re.findall(r"`([^`]*)`", src))
need = set(re.findall(r"[一-鿿]", strings)) | {"王", "君"}
compact = lambda p: re.sub(r"\s*([MLQCZ])\s*", r"\1", p)   # "M 323 706 Q …" → "M323 706Q…"
han = {}
for line in open(sys.argv[1], encoding="utf-8"):
    d = json.loads(line)
    if d["character"] in need:
        han[d["character"]] = {"s": [compact(p) for p in d["strokes"]], "m": d["medians"]}
missing = sorted(need - set(han) - {"珺"})
if missing:
    print("missing:", "".join(missing))
html = src.replace("/*__HANZI__*/", "const HANZI = " + json.dumps(han, ensure_ascii=False, separators=(",", ":")) + ";", 1)

if "--site" in sys.argv:
    outdir = pathlib.Path(sys.argv[sys.argv.index("--site") + 1])
    (outdir / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (here / "fonts").glob("*.woff2"):
        shutil.copy(f, outdir / "fonts" / f.name)
    fonts_css = (here / "fonts" / "fonts.css").read_text(encoding="utf-8")
    html = re.sub(r'<link href="https://fonts.googleapis.com[^>]*>', "<style>\n" + fonts_css + "</style>", html, count=1)
    head = '''<title>巨浪 — Dylan He</title>
<meta name="description" content="用沙堡和海浪解读曾鸣的产业史观：为什么 OpenAI、Anthropic 大概率不是原生时代的大赢家。纯代码动画，每句字幕标明是原话、转述、补充还是反方。">
<meta property="og:type" content="video.other"><meta property="og:site_name" content="Dylan He"><meta property="og:title" content="巨浪 — Dylan He">
<meta property="og:description" content="用沙堡和海浪解读曾鸣的产业史观。纯代码动画，可交互。"><meta property="og:image" content="https://dylanhe.cn/assets/the-wave.jpg"><meta property="og:url" content="https://dylanhe.cn/explainers/wave/">
<meta name="twitter:card" content="summary_large_image"><link rel="canonical" href="https://dylanhe.cn/explainers/wave/">'''
    html = re.sub(r"<title>[^<]*</title>", head, html, count=1)
    assert "fonts.googleapis" not in html
    out = outdir / "index.html"
else:
    out = here.parent / "wave.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html.encode()) // 1024} KB, {len(han)} glyphs)")
