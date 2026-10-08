"""把 content.js 和所需汉字的笔画数据合进 template.html，生成单文件 demo/manuscript.html。
笔画数据取自 Make Me a Hanzi 的 graphics.txt（Arphic 公共许可），路径用第一个参数传入。"""
import json, re, subprocess, sys, pathlib
here = pathlib.Path(__file__).parent
graphics = sys.argv[1]
content = (here / "content.js").read_text(encoding="utf-8")
data = json.loads(subprocess.check_output(["node", "-e", f"process.stdout.write(JSON.stringify(require({json.dumps(str(here / 'content.js'))})))"]))
need = set(re.findall(r"[一-鿿]", json.dumps(data, ensure_ascii=False))) | {"王", "君"}
han = {}
for line in open(graphics, encoding="utf-8"):
    d = json.loads(line)
    if d["character"] in need:
        han[d["character"]] = {"s": d["strokes"], "m": d["medians"]}
missing = sorted(need - set(han) - {"珺"})
if missing:
    print("missing:", "".join(missing))
html = (here / "template.html").read_text(encoding="utf-8")
html = html.replace("/*__CONTENT__*/", content.replace("if (typeof module", "// if (typeof module"))
html = html.replace("/*__HANZI__*/", "const HANZI = " + json.dumps(han, ensure_ascii=False, separators=(",", ":")) + ";")
out = here.parent / "manuscript.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html) // 1024} KB, {len(han)} glyphs)")
