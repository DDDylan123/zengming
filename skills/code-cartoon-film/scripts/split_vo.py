"""把一口气念完的整篇旁白按停顿切成 N 句：候选停顿 + 按字数推算时长的动态规划，再逐句做老电视处理。
用法：python3 split_vo.py take.mp3 vo-lines.json out_dir"""
import json, re, subprocess, sys, os
take, lines_json, out = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
lines = [l['tts'] for l in json.load(open(lines_json))]
w = [len(re.sub(r'\s', '', l)) for l in lines]; N = len(lines)
total = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', take]))
log = subprocess.run(['ffmpeg', '-i', take, '-af', 'silencedetect=noise=-32dB:d=0.22', '-f', 'null', '-'], capture_output=True, text=True).stderr
gaps, s = [], None
for k, v in re.findall(r'silence_(start|end): ([\d.]+)', log):
    if k == 'start': s = float(v)
    elif s is not None: gaps.append((s, float(v))); s = None
head = gaps[0][1] if gaps and gaps[0][0] < .05 else 0.0
gaps = [g for g in gaps if g[0] > .05 and g[1] < total - .05]
pts = [(head, head)] + gaps + [(total, total)]
rate = sum(w) / (total - head - sum(b - a for a, b in gaps) * .5)
INF = 1e18; dp = [[INF] * len(pts) for _ in range(N + 1)]; par = [[-1] * len(pts) for _ in range(N + 1)]; dp[0][0] = 0
for k in range(1, N + 1):
    for j in range(1, len(pts)):
        if k == N and j != len(pts) - 1: continue
        for i in range(j):
            if dp[k - 1][i] >= INF: continue
            dur = pts[j][0] - pts[i][1]; exp = w[k - 1] / rate
            bonus = -(pts[j][1] - pts[j][0]) * .8 if j < len(pts) - 1 else 0
            c = dp[k - 1][i] + ((dur - exp) / exp) ** 2 + bonus
            if c < dp[k][j]: dp[k][j] = c; par[k][j] = i
j = len(pts) - 1; seq = []
for k in range(N, 0, -1): i = par[k][j]; seq.append((pts[i][1], pts[j][0])); j = i
seq = seq[::-1]
CHAIN = ("[0]aformat=channel_layouts=mono,highpass=f=300,highpass=f=300,lowpass=f=3600,lowpass=f=3600,"
 "acompressor=threshold=-20dB:ratio=4:attack=5:release=80,aeval='tanh(2.2*val(0))/tanh(2.2)',"
 "vibrato=f=0.7:d=0.06,vibrato=f=7:d=0.015,aecho=0.8:0.5:22:0.25,volume=1.4,afade=t=in:d=0.04,areverse,afade=t=in:d=0.08,areverse[v];"
 "[1]highpass=f=1500,lowpass=f=6000,volume=0.5[n];[2]volume=0.012[h];[v][n][h]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.9[o]")
meta = {}
for i, (a, b) in enumerate(seq):
    k = f'{i + 1:02d}'; a = max(0, a - .06); b = b + .12; d = b - a
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', str(d), '-i', take, '-f', 'lavfi', '-i', f'anoisesrc=color=pink:amplitude=0.02:d={d}',
                    '-f', 'lavfi', '-i', f'sine=f=50:d={d}', '-filter_complex', CHAIN, '-map', '[o]', '-ar', '44100', '-b:a', '128k', f'{out}/{k}.mp3'], check=True)
    dd = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{out}/{k}.mp3']))
    meta[k] = {'dur': round(dd, 3)}
    print(k, f'{a:6.2f}-{b:6.2f}', f'{b - a:5.2f}s', f'exp {w[i] / rate:5.2f}', lines[i][:14])
json.dump(meta, open(f'{out}/meta.json', 'w'))
