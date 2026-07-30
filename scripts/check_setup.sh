#!/usr/bin/env bash
# p-broll 通用环境自检（macOS/Linux）
# 检查通用依赖，并报告可选的视频与旁白生成路线。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"

FAIL=0
ok()   { printf 'PASS  %s\n' "$1"; }
warn() { printf 'WARN  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; FAIL=1; }

if command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
  ok "ffmpeg / ffprobe 可用"
else
  bad "ffmpeg / ffprobe 缺失"
fi

PY=""
command -v python3 >/dev/null 2>&1 && PY=python3
[ -z "$PY" ] && command -v python >/dev/null 2>&1 && PY=python
if [ -n "$PY" ] && "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
  ok "Python >= 3.10"
else
  bad "Python 缺失或版本低于 3.10"
fi

if [ -n "$PY" ] && "$PY" -c 'import sys; sys.path.insert(0, sys.argv[1]); import PIL; from font_utils import load_font; load_font(24); print(PIL.__version__)' "$HERE" >/dev/null 2>&1; then
  ok "Pillow / 中文字体可用"
else
  bad "Pillow 或中文字体缺失；安装 Pillow 和中文字体，或设置 P_BROLL_FONT"
fi

if command -v node >/dev/null 2>&1 && command -v npx >/dev/null 2>&1; then
  NODE_MAJOR="$(node -p "process.versions.node.split('.')[0]" 2>/dev/null || printf 0)"
  if [ "$NODE_MAJOR" -ge 22 ]; then
    ok "Node / npx 可用（Node >= 22，小云雀 CLI 与 HyperFrames 路线可用）"
  elif [ "$NODE_MAJOR" -ge 16 ]; then
    warn "Node $(node -v) 可用于小云雀 CLI，但 HyperFrames 当前需要 Node >= 22"
  else
    warn "Node $(node -v) 版本过低；小云雀 CLI 至少需要 Node 16，HyperFrames 至少需要 Node 22"
  fi
else
  warn "Node / npx 未检测到；仅在小云雀 CLI 或 HyperFrames 路线中需要"
fi

if command -v xxd >/dev/null 2>&1; then
  ok "xxd 可用（macOS/Linux 首尾帧取色）"
else
  bad "xxd 缺失；prepare_frames.sh 需要 xxd"
fi

DREAMINA=""
command -v dreamina >/dev/null 2>&1 && DREAMINA="$(command -v dreamina)"
[ -z "$DREAMINA" ] && [ -x "$HOME/bin/dreamina" ] && DREAMINA="$HOME/bin/dreamina"
if [ -n "$DREAMINA" ]; then
  DREAMINA_HELP="$("$DREAMINA" --help 2>&1 || true)"
  if printf '%s' "$DREAMINA_HELP" | grep -Eiq '(^|[^[:alnum:]_])(tts|text.?to.?speech|speech|voice|narration)([^[:alnum:]_]|$)|语音|配音'; then
    ok "即梦 CLI 检测到可能的语音命令；执行前仍需读取子命令 help"
  else
    warn "即梦 CLI 已安装，但当前 help 未列出独立语音/TTS 命令；旁白路由将转向其他平台"
  fi
else
  warn "未检测到即梦 CLI；Agent 无语音能力时将推荐其他语音平台"
fi

printf 'INFO  Gate 2 图片路由：Agent 图片能力 → 用户平台 CLI → 小云雀 → HyperFrames\n'
printf 'INFO  Gate 2 静帧必须展示并取得明确确认；改图只能重新纯文生图，禁止参考旧图\n'
printf 'INFO  Gate 3 将动态检测 Agent 视频能力或平台 CLI，不要求固定 API Key\n'
printf 'INFO  视频时长：按内容复杂度动态计算 4–15 秒，并匹配不短于目标的平台档位\n'
printf 'INFO  旁白路由：Agent 内置 TTS → 即梦 CLI（须真实支持 TTS）→ 其他语音平台/用户回传\n'
exit "$FAIL"
