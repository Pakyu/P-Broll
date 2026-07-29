# p-broll 通用环境自检（Windows）
# 检查通用依赖，并报告可选的视频与旁白生成路线。
$ErrorActionPreference = "Continue"
$fail = 0

function ok($msg)   { Write-Host "PASS  $msg" -ForegroundColor Green }
function warn($msg) { Write-Host "WARN  $msg" -ForegroundColor Yellow }
function bad($msg)  { Write-Host "FAIL  $msg" -ForegroundColor Red; $script:fail = 1 }

$ff = Get-Command ffmpeg -ErrorAction SilentlyContinue
$fp = Get-Command ffprobe -ErrorAction SilentlyContinue
if ($ff -and $fp) { ok "ffmpeg / ffprobe 可用" } else { bad "ffmpeg / ffprobe 缺失" }

try {
    $ver = & python -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
    $parts = $ver -split "\."
    if ([int]$parts[0] -ge 3 -and [int]$parts[1] -ge 10) {
        ok "Python $ver (>= 3.10)"
    } else {
        bad "Python 版本过低: $ver（需要 >= 3.10）"
    }
} catch {
    bad "Python 未安装"
}

try {
    $fontCheck = & python -c "import sys; sys.path.insert(0, r'$PSScriptRoot'); import PIL; from font_utils import load_font; load_font(24); print(PIL.__version__)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        ok "Pillow $fontCheck / 中文字体可用"
    } else {
        bad "Pillow 或中文字体缺失；安装 Pillow 和中文字体，或设置 P_BROLL_FONT"
    }
} catch {
    bad "Pillow 或中文字体检查失败"
}

$node = Get-Command node -ErrorAction SilentlyContinue
$npx = Get-Command npx -ErrorAction SilentlyContinue
if ($node -and $npx) {
    $nodeMajor = [int]((& node -p "process.versions.node.split('.')[0]").Trim())
    if ($nodeMajor -ge 22) {
        ok "Node / npx 可用（Node >= 22，小云雀 CLI 与 HyperFrames 路线可用）"
    } elseif ($nodeMajor -ge 16) {
        warn "Node $(& node -v) 可用于小云雀 CLI，但 HyperFrames 当前需要 Node >= 22"
    } else {
        warn "Node $(& node -v) 版本过低；小云雀 CLI 至少需要 Node 16，HyperFrames 至少需要 Node 22"
    }
} else {
    warn "Node / npx 未检测到；仅在小云雀 CLI 或 HyperFrames 路线中需要"
}

$dreamina = Get-Command dreamina -ErrorAction SilentlyContinue
if (-not $dreamina) {
    $dreaminaFallback = Join-Path $HOME "bin\dreamina.exe"
    if (Test-Path -LiteralPath $dreaminaFallback) {
        $dreamina = Get-Item -LiteralPath $dreaminaFallback
    }
}
if ($dreamina) {
    $dreaminaPath = if ($dreamina.Path) { $dreamina.Path } else { $dreamina.FullName }
    $dreaminaHelp = (& $dreaminaPath --help 2>&1 | Out-String)
    if ($dreaminaHelp -match '(?im)\b(tts|text.?to.?speech|speech|voice|narration)\b|语音|配音') {
        ok "即梦 CLI 检测到可能的语音命令；执行前仍需读取子命令 help"
    } else {
        warn "即梦 CLI 已安装，但当前 help 未列出独立语音/TTS 命令；旁白路由将转向其他平台"
    }
} else {
    warn "未检测到即梦 CLI；Agent 无语音能力时将推荐其他语音平台"
}

Write-Host "INFO  Gate 2 图片路由：Agent 图片能力 → 用户平台 CLI → 小云雀 → HyperFrames"
Write-Host "INFO  Gate 3 将动态检测 Agent 视频能力或平台 CLI，不要求固定 API Key"
Write-Host "INFO  视频时长：按内容复杂度动态计算 4–15 秒，并匹配不短于目标的平台档位"
Write-Host "INFO  旁白路由：Agent 内置 TTS → 即梦 CLI（须真实支持 TTS）→ 其他语音平台/用户回传"
exit $fail
