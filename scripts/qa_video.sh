#!/bin/bash
# 单条成片 QA 全家桶:直接读取模型原片，生成逐秒 contact sheet + 首/尾帧 + 尾帧对照 + 客观分
# 普通 B-roll 不改音轨；完整讲解片追加 --strip-audio 才生成 -noaudio.mp4。
# 用法: qa_video.sh <video.mp4> <confirmed-still.png> [out-dir=视频所在目录] [bg-hex] [--strip-audio]
set -euo pipefail

V="${1:?用法: qa_video.sh <video.mp4> <confirmed-still.png> [out-dir] [bg-hex]}"
STILL="${2:?缺少确认静帧参数}"
OUT="$(dirname "$V")"
BGHEX=""
STRIP_AUDIO=""
POSITIONAL=0
for ARG in "${@:3}"; do
  if [ "$ARG" = "--strip-audio" ]; then
    STRIP_AUDIO="--strip-audio"
  elif [ "$POSITIONAL" -eq 0 ]; then
    OUT="$ARG"; POSITIONAL=1
  elif [ "$POSITIONAL" -eq 1 ]; then
    BGHEX="$ARG"; POSITIONAL=2
  else
    echo "未知参数: $ARG" >&2; exit 2
  fi
done
mkdir -p "$OUT"

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
VENV_PY=python3
command -v python3 >/dev/null 2>&1 || VENV_PY=python
TILES=$("$VENV_PY" -c "import math; print(min(15, max(4, math.ceil(float('$DUR')))))")

if ffprobe -v error -select_streams a -show_entries stream=codec_type -of csv=p=0 "$V" | grep -q audio; then
  HAS_AUDIO=1
  echo "INFO  检测到模型原始音轨；按原样保留"
else
  HAS_AUDIO=0
  echo "INFO  模型原始视频没有音轨；不补音"
fi

if [ "$STRIP_AUDIO" = "--strip-audio" ]; then
  STEM="$(basename "${V%.*}")"; STEM="${STEM%-noaudio}"
  NOAUDIO="$OUT/${STEM}-noaudio.mp4"
  if [ "$HAS_AUDIO" -eq 1 ]; then
    ffmpeg -y -v error -i "$V" -map 0:v:0 -c:v copy -an "$NOAUDIO"
  else
    cp -f "$V" "$NOAUDIO"
  fi
  echo "INFO  完整讲解片无音频素材 -> $NOAUDIO"
fi

ffmpeg -y -v error -i "$V" \
  -vf "fps=1,scale=203:360,tile=${TILES}x1" -frames:v 1 "$OUT/contact-sheet.jpg"
ffmpeg -y -v error -i "$V" -frames:v 1 "$OUT/video-first-frame.jpg"
ffmpeg -y -v error -sseof -0.1 -i "$V" -frames:v 1 "$OUT/video-last-frame.jpg"
ffmpeg -y -v error -i "$STILL" -i "$OUT/video-last-frame.jpg" \
  -filter_complex "[0:v]scale=270:480[a];[1:v]scale=270:480[b];[a][b]hstack" \
  "$OUT/end-frame-comparison.jpg"

HERE="$(cd "$(dirname "$0")" && pwd)"
ARGS=(--video "$V" --still "$STILL")
[ -n "$BGHEX" ] && ARGS+=(--bg-hex "$BGHEX")
"$VENV_PY" "$HERE/qa_score.py" "${ARGS[@]}" || echo "  (qa_score 需要 Pillow,分数缺省不阻塞)"
echo "QA assets -> $OUT"
