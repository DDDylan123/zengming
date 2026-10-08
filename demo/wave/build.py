"""把《巨浪》用到的汉字笔画数据注入 src.html，生成单文件 demo/wave.html。
笔画数据取自 Make Me a Hanzi 的 graphics.txt（Arphic 公共许可）：
  python3 demo/wave/build.py path/to/makemeahanzi/graphics.txt"""
import json, re, sys, pathlib
here = pathlib.Path(__file__).parent
src = (here / "src.html").read_text(encoding="utf-8")
need = set(re.findall(r"[一-鿿]", src)) | {"王", "君"}
han = {}
for line in open(sys.argv[1], encoding="utf-8"):
    d = json.loads(line)
    if d["character"] in need:
        han[d["character"]] = {"s": d["strokes"], "m": d["medians"]}
missing = sorted(need - set(han) - {"珺"})
if missing:
    print("missing:", "".join(missing))
out = here.parent / "wave.html"
html = src.replace("/*__HANZI__*/", "const HANZI = " + json.dumps(han, ensure_ascii=False, separators=(",", ":")) + ";", 1)
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html) // 1024} KB, {len(han)} glyphs)")
