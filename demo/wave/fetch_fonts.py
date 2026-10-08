"""从 Google Fonts 下载《巨浪》用到的字的子集（woff2），存到 demo/wave/fonts/，供网站自托管。
字体均为 SIL 开放字体许可（OFL）。用法：python3 demo/wave/fetch_fonts.py"""
import re, pathlib, urllib.parse, urllib.request
here = pathlib.Path(__file__).parent
src = (here / "src.html").read_text(encoding="utf-8")
# 只取字符串里的字（注释里的字不会画到画面上）
strings = "".join(re.findall(r'"([^"\n]*)"', src) + re.findall(r"`([^`]*)`", src))
cjk = "".join(sorted(set(ch for ch in strings if ord(ch) > 127)))
ascii_ = "".join(chr(c) for c in range(32, 127))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
def fetch(family, weights, text, prefix):
    url = f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}:wght@{';'.join(map(str, weights))}&text={urllib.parse.quote(text)}&display=swap"
    css = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA})).read().decode()
    out = []
    for block in re.findall(r"@font-face\s*{[^}]*}", css):
        w = re.search(r"font-weight:\s*(\d+)", block).group(1)
        u = re.search(r"url\((https://[^)]+)\)", block).group(1)
        name = f"{prefix}-{w}.woff2"
        (here / "fonts" / name).write_bytes(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA})).read())
        out.append((family, w, name))
    return out
faces = []
faces += fetch("Noto Sans SC", [300, 400, 500, 700], cjk + ascii_, "sans")
faces += fetch("Noto Serif SC", [900], "反方", "serif")
faces += fetch("Caveat", [500, 700], ascii_ + "−×", "caveat")
# Google 返回的是可变字体，各字重是同一个文件：每个字体只留一个，用字重范围声明
import hashlib
seen, rules = {}, []
for f, w, n in faces:
    h = hashlib.md5((here / "fonts" / n).read_bytes()).hexdigest()
    if (f, h) in seen: (here / "fonts" / n).unlink(); seen[(f, h)][1].append(int(w)); continue
    seen[(f, h)] = (n, [int(w)])
for (f, _), (n, ws) in seen.items():
    rng = f"{min(ws)} {max(ws)}" if len(ws) > 1 else str(ws[0])
    rules.append(f'@font-face{{font-family:"{f}";font-weight:{rng};font-display:swap;src:url(fonts/{n}) format("woff2")}}')
    print(f, rng, n, (here / "fonts" / n).stat().st_size, "bytes")
(here / "fonts" / "fonts.css").write_text("\n".join(rules) + "\n", encoding="utf-8")
