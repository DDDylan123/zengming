"""下载 20 句旁白 → 老电视处理 → 量时长和音高。用法：python3 process_vo.py urls.json out_dir
urls.json: {"01": "https://...mp3", ...}"""
import json, subprocess, sys, os, urllib.request
import numpy as np

urls = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
CHAIN = ("[0]aformat=channel_layouts=mono,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
         "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
         "highpass=f=300,highpass=f=300,lowpass=f=3600,lowpass=f=3600,"
         "acompressor=threshold=-20dB:ratio=4:attack=5:release=80,aeval='tanh(2.2*val(0))/tanh(2.2)',"
         "vibrato=f=0.7:d=0.06,vibrato=f=7:d=0.015,aecho=0.8:0.5:22:0.25,volume=1.4[v];"
         "[1]highpass=f=1500,lowpass=f=6000,volume=0.5[n];[2]volume=0.012[h];"
         "[v][n][h]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.9[o]")
def f0(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32); fs = 16000; hop = 320; win = 1024; vals = []
    for i in range(0, len(x) - win, hop):
        w = x[i:i + win]
        if np.sqrt(np.mean(w * w)) < .02: continue
        w = w - w.mean(); ac = np.correlate(w, w, 'full')[win - 1:]
        lo, hi = fs // 300, fs // 70
        k = lo + np.argmax(ac[lo:hi])
        if ac[k] > .35 * ac[0]: vals.append(fs / k)
    return float(np.median(vals)) if vals else 0.0
res = {}
for k, u in sorted(urls.items()):
    raw = f'{out}/{k}_raw.mp3'; dst = f'{out}/{k}.mp3'
    urllib.request.urlretrieve(u, raw)
    d0 = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', raw]))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-f', 'lavfi', '-i', f'anoisesrc=color=pink:amplitude=0.02:d={d0}',
                    '-f', 'lavfi', '-i', f'sine=f=50:d={d0}', '-filter_complex', CHAIN, '-map', '[o]', '-ar', '44100', '-b:a', '128k', dst], check=True)
    d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', dst]))
    res[k] = {'dur': round(d, 3), 'f0': round(f0(raw), 1)}
    print(k, res[k], flush=True)
json.dump(res, open(f'{out}/meta.json', 'w'), indent=1)
