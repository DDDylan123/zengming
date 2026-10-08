"""把两半切好的英文旁白合成 vo-en/01..20.mp3，并把真实时长写进 index.html 的 VO_META_EN，再生成 en/index.html。
用法（在 two-percent-v2/ 下）：python3 en/assemble.py en/s1 en/s2"""
import json, os, re, shutil, subprocess, sys
a, b = sys.argv[1:3]
os.makedirs('vo-en', exist_ok=True)
meta = {}
for half, off in ((a, 0), (b, 10)):
    m = json.load(open(f'{half}/meta.json'))
    for k, v in m.items():
        n = f'{int(k) + off:02d}'
        shutil.copy(f'{half}/{k}.mp3', f'vo-en/{n}.mp3'); meta[n] = v
s = open('index.html', encoding='utf-8').read()
s = re.sub(r'const VO_META_EN = .*?; /\*VO_META_EN\*/', 'const VO_META_EN = ' + json.dumps(dict(sorted(meta.items()))) + '; /*VO_META_EN*/', s)
open('index.html', 'w', encoding='utf-8').write(s)
subprocess.run([sys.executable, 'build_en.py'], check=True)
print(len(meta), 'lines, total', round(sum(v['dur'] for v in meta.values()), 1), 's')
