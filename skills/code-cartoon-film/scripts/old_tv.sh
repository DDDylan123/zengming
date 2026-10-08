#!/bin/sh
# 老电视/老新闻片声音处理：只留中频 + 压缩 + 饱和 + 磁带抖动 + 小房间 + 底噪和 50Hz 嗡声
# 用法：sh old_tv.sh in.mp3 out.mp3
IN="$1"; OUT="$2"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
ffmpeg -loglevel error -y -i "$IN" -f lavfi -i "anoisesrc=color=pink:amplitude=0.02:d=$D" -f lavfi -i "sine=f=50:d=$D" -filter_complex \
"[0]aformat=channel_layouts=mono,highpass=f=300,highpass=f=300,lowpass=f=3600,lowpass=f=3600,acompressor=threshold=-20dB:ratio=4:attack=5:release=80,aeval='tanh(2.2*val(0))/tanh(2.2)',vibrato=f=0.7:d=0.06,vibrato=f=7:d=0.015,aecho=0.8:0.5:22:0.25,volume=1.4[v];[1]highpass=f=1500,lowpass=f=6000,volume=0.5[n];[2]volume=0.012[h];[v][n][h]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.9[o]" \
-map "[o]" -ar 44100 -b:a 160k "$OUT"
