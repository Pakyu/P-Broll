#!/bin/bash
# 单条成片 QA:模型原片 -> contact sheet + 首/尾帧 + 模式对应帧对照 + 客观分
# 普通 B-roll 不改音轨；完整讲解片追加 --strip-audio 才生成 -noaudio.mp4。
# 用法: qa_video.sh <video.mp4> <confirmed-still.png> [out-dir] [bg-hex]
#       [--mode first-last|single-first] [--strip-audio]
set -euo pipefail

V="${1:?用法: qa_video.sh <video.mp4> <confirmed-still.png> [out-dir] [bg-hex]}"
STILL="${2:?缺少确认静帧参数}"
shift 2

OUT="$(dirname "$V")"
BGHEX=""
MODE="first-last"
STRIP_AUDIO=0
POSITIONAL=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --strip-audio)
      STRIP_AUDIO=1
      shift
      ;;
    --mode)
      [ "$#" -ge 2 ] || { echo "--mode 缺少取值" >&2; exit 2; }
      MODE="$2"
      shift 2
      ;;
    --mode=*)
      MODE="${1#--mode=}"
      shift
      ;;
    *)
      if [ "$POSITIONAL" -eq 0 ]; then
        OUT="$1"; POSITIONAL=1
      elif [ "$POSITIONAL" -eq 1 ]; then
        BGHEX="$1"; POSITIONAL=2
      else
        echo "未知参数: $1" >&2; exit 2
      fi
      shift
      ;;
  esac
done

case "$MODE" in
  first-last|single-first) ;;
  *) echo "--mode 必须是 first-last 或 single-first" >&2; exit 2 ;;
esac

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

if [ "$STRIP_AUDIO" -eq 1 ]; then
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

if [ "$MODE" = "single-first" ]; then
  COMPARE_FRAME="$OUT/video-first-frame.jpg"
  COMPARE_OUT="$OUT/start-frame-comparison.jpg"
  rm -f "$OUT/end-frame-comparison.jpg"
else
  COMPARE_FRAME="$OUT/video-last-frame.jpg"
  COMPARE_OUT="$OUT/end-frame-comparison.jpg"
  rm -f "$OUT/start-frame-comparison.jpg"
fi
ffmpeg -y -v error -i "$STILL" -i "$COMPARE_FRAME" \
  -filter_complex "[0:v]scale=270:480[a];[1:v]scale=270:480[b];[a][b]hstack" \
  "$COMPARE_OUT"

HERE="$(cd "$(dirname "$0")" && pwd)"
ARGS=(--video "$V" --still "$STILL" --mode "$MODE")
[ "$MODE" = "first-last" ] && [ -n "$BGHEX" ] && ARGS+=(--bg-hex "$BGHEX")
"$VENV_PY" "$HERE/qa_score.py" "${ARGS[@]}" || echo "  (qa_score 需要 Pillow，分数缺省不阻塞)"
echo "QA assets -> $OUT"
