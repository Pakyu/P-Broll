# P-Broll

[![Validate P-Broll](https://github.com/Pakyu/P-Broll/actions/workflows/validate.yml/badge.svg)](https://github.com/Pakyu/P-Broll/actions/workflows/validate.yml)
[MIT License](LICENSE)

把口播文稿、观点句或完整选题，转成编辑隐喻式纸拼贴 B-roll。

P-Broll 是一个面向 AI Agent 的视频制作 Skill，不是独立的 GUI 软件。它会先理解内容、设计视觉隐喻，再生成静帧和动态视频，并通过首尾帧与画面质量检查交付结果。

## 能做什么

- 单条 B-roll：根据动作和信息复杂度，动态规划 **4–15 秒**时长。
- 批量 B-roll：为多句口播分别生成视觉隐喻、静帧和视频。
- 完整讲解片：使用 beat map 编排约 **45–60 秒**的成片。
- 统一视觉语言：黑白半调剪贴、平坦色场、卡纸点缀、奶油色描边与纸张阴影。
- 从空场开始组装：物件逐件进入，形成“概念被搭建出来”的视觉节奏。
- 多工具路由：优先使用 Agent 已有能力，也支持平台 CLI、手动生成包和 HyperFrames 兜底。
- 跨平台脚本：支持 Windows、macOS 和 Linux，并包含自动化检查与视频 QA。

## 工作流程

```mermaid
flowchart LR
    A[口播文稿 / 观点 / 选题] --> B[Gate 1<br/>隐喻方案与动态时长]
    B --> C[Gate 2<br/>生成、展示并确认最终静帧]
    C --> D[准备首帧与尾帧]
    D --> E[Gate 3<br/>确认模型与费用、生成视频并执行 QA]
    E --> F[单条或批量 B-roll]
    E --> G[45–60 秒完整讲解片]
```

### 三道确认门

1. **Gate 1：隐喻与时长**
   明确口播核心、物件关系、动作层级、画面构图和建议时长。

2. **Gate 2：最终静帧**
   生成后把实际尾帧展示给用户并完成图片 QA。只有用户明确确认当前版本没问题，才能以此建立首帧并进入视频阶段。

3. **Gate 3：视频与 QA**
   使用首尾帧生成视频，检查构图、首尾一致性、运动质量和技术参数。

Gate 2 不能预先跳过。即使用户在开始前说“直接跑完”或让 Agent 自主决定，也必须在静帧实际生成后暂停，等待用户针对当前图片版本明确确认。这样可以避免在错误静帧上继续消耗视频生成费用。批量项目可以一次确认多个明确编号，但未确认的条目不能进入视频生成。

## 安装

将仓库克隆到你的 Agent 能识别的 Skills 目录。不同客户端的目录可能不同，请以客户端当前配置为准。

macOS / Linux 示例：

```bash
git clone https://github.com/Pakyu/P-Broll.git ~/.agents/skills/p-broll
```

Windows PowerShell 示例：

```powershell
git clone https://github.com/Pakyu/P-Broll.git "$HOME\.agents\skills\p-broll"
```

如果你的客户端使用 `~/.codex/skills`、`~/.claude/skills` 或自定义 Skills 目录，把目标路径替换为对应目录即可。安装后重启或刷新 Agent 会话。

## 快速开始

单条 B-roll：

```text
使用 $p-broll，把这句话做成一条纸拼贴 B-roll：
“真正困难的不是找到答案，而是先问对问题。”
```

批量生成：

```text
使用 $p-broll，把下面 5 句口播分别做成 B-roll。
请先给出每句的隐喻方案和动态时长，再逐条生成。
```

完整讲解片：

```text
使用 $p-broll，把“创业早期如何判断产品市场匹配”做成一条约 50 秒的完整讲解片。
```

如果你愿意让 Agent 自主决定前期视觉方案：

```text
隐喻、构图和静帧方向按你的判断执行。静帧生成后发给我确认，确认通过后再选择视频模型并生成。
```

## 生成工具优先级

P-Broll 不绑定单一模型，也不要求固定的 `GEMINI_API_KEY`。Agent 应先检测当前环境实际可用的能力，再选择路线。

### 图片生成

| 优先级 | 路线 | 说明 |
|---|---|---|
| 1 | Agent 自带或已集成的图片生成能力 | 例如 Codex 内置图片生成；优先使用，无需重复配置平台 |
| 2 | 用户指定图片平台的官方 CLI | 仅使用用户已经选择或授权的平台 |
| 3 | 小云雀 CLI 或网页 | 适合希望使用国内平台的用户 |
| 4 | HyperFrames | 生成可控、确定性的静帧，作为最终兜底 |

外部 CLI 提供多个生图模型时，先询问用户是否指定模型，并展示当前可用型号、尺寸能力和单张积分/费用。用户没有偏好或不知道怎么选时，只在平台实时提供的型号中优先考察 **Seedream 5.0 Pro、NanoBanana、GPT Image 2**，再根据价格和画面需求给出建议；这些名称不是对所有平台可用性的承诺。

图片需要修改时必须重新纯文生图：把修改意见写进一份新的完整提示词，生成一个全新版本。禁止把旧图、截图、裁剪图、蒙版、控制图或其他派生图作为参考输入，也禁止使用 image-to-image、局部重绘或扩图来修改。新版本仍要重新展示并取得 Gate 2 确认。

### 视频生成

| 优先级 | 路线 | 说明 |
|---|---|---|
| 1 | Agent 自带或已集成的视频生成能力 | 必须实际支持首帧与尾帧约束 |
| 2 | 用户常用平台的官方 CLI | 根据 CLI 当前提供的参数调用，不猜测不存在的能力 |
| 3 | 小云雀 CLI | 当前可用且支持首尾帧时，优先考虑 Seedance 1.5 Pro，其次 Seedance 2.0；使用前需按平台当前规则开通可用会员档位 |
| 4 | 手动生成包 | 输出首帧、尾帧、中英文提示词、时长和操作说明，由用户上传到网页生成 |
| 5 | HyperFrames | 不依赖生成式视频账号的确定性动效兜底方案 |

小云雀入口：<https://xiaoyunque.jianying.com/s/z_Wf-ql547E/>
CLI 安装命令：

```bash
npx @pippit-dev/cli@latest install
```

使用 CLI 路线前，请先完成平台登录，并按平台当前页面确认会员、积分、模型权限和计费规则。CLI 有多个视频模型时，Agent 会先询问是否指定；没有偏好时，平台实际可用且满足首尾帧要求的前提下优先建议 **Seedance 1.5 Pro**，其次 **Seedance 2.0**。不同模型费用可能差异很大，提交前必须再次确认静帧版本、模型、时长和预计消耗。无法可靠查询费用时，只有用户明确接受未知消耗才会提交。新用户可能获得免费积分，但实际权益以平台显示为准。

如果没有任何视频平台 CLI，也不准备开通平台服务，P-Broll 会整理一个手动生成包。即使用户无法完成手动生成，也可以继续使用 HyperFrames 制作基础动效。

### 语音生成

语音只在制作完整讲解片、且确实需要旁白时使用：

1. Agent 自带或已集成的 TTS。
2. 当前即梦 CLI 确实提供 TTS 命令时，使用即梦 CLI。
3. 用户指定其他语音平台，或由用户上传已经生成的旁白。

普通 B-roll 默认保留视频模型生成的原始音频，不额外产出无音频副本。只有完整讲解片需要统一旁白和混音时，才会抽离或重建音频轨道。

## 动态时长

P-Broll 不把所有视频固定为 5 秒。它会根据以下因素在 **4–15 秒**范围内估算：

- 简单动作数量；
- 需要协同发生的动作数量；
- 物件之间的关系复杂度；
- 开头空场停留时间；
- 尾帧稳定展示时间；
- 目标平台实际支持的时长档位。

可以使用内置脚本预估时长：

```bash
python scripts/select_duration.py \
  --simple 2 \
  --coordinated 1 \
  --relation simple \
  --platform-durations 5,10,15
```

用户指定的时长会优先考虑；如果该时长不足以完成必要动作，脚本会明确提示，而不是强行压缩。

## 环境要求

核心流程：

- Python 3.10 或更高版本；
- Pillow；
- FFmpeg 与 FFprobe；
- 至少一款可用的中文字体。

按所选路线可能还需要：

- Node.js 与 `npx`；
- HyperFrames 当前工作流建议使用 Node.js 22 或更高版本；
- 小云雀 CLI 所需 Node.js 版本以其当前安装程序为准；
- macOS / Linux 的部分帧处理脚本需要 `xxd`。

Windows 自检：

```powershell
pwsh -NoProfile -File scripts/check_setup.ps1
```

macOS / Linux 自检：

```bash
bash scripts/check_setup.sh
```

如果自动识别到的中文字体不合适，可以通过脚本的 `--font` 参数指定，或设置 `P_BROLL_FONT` 环境变量。

## 常用脚本

准备首尾帧：

```powershell
# Windows
pwsh -NoProfile -File scripts/prepare_frames.ps1 <item-dir>
```

```bash
# macOS / Linux
bash scripts/prepare_frames.sh <item-dir>
```

创建手动视频生成包：

```bash
python scripts/create_manual_package.py \
  --item-dir <item-dir> \
  --prompt-cn "<中文提示词>" \
  --prompt-en "<English prompt>" \
  --title "<标题>" \
  --duration 8 \
  --duration-reason "<时长理由>"
```

视频 QA：

```powershell
# Windows
pwsh -NoProfile -File scripts/qa_video.ps1 <video.mp4> <confirmed-still.png>
```

```bash
# macOS / Linux
bash scripts/qa_video.sh <video.mp4> <confirmed-still.png>
```

组装完整讲解片：

```bash
python scripts/assemble.py --project <project-dir>
```

## 典型输出

```text
project/
├── beats.json
├── 01-beat/
│   ├── confirmed-still.png
│   ├── first-frame.png
│   ├── end-frame.png
│   ├── prompt-cn.txt
│   ├── prompt-en.txt
│   ├── video.mp4
│   └── qa/
│       ├── contact-sheet.png
│       ├── first-frame.png
│       ├── last-frame.png
│       └── qa-report.json
├── 02-beat/
│   └── ...
└── final.mp4
```

文件名会随单条、批量和完整讲解片模式略有变化。详细字段和目录约定见 [`references/beats-manifest.md`](references/beats-manifest.md)。

## 费用与权限

- P-Broll 本身采用 MIT License，可免费使用和修改。
- 图片、视频和语音模型可能由第三方收费，费用取决于用户选择的平台和账号。
- Skill 不会把某个平台描述为永久免费，也不会承诺固定赠送额度。
- 生图前确认模型、张数和预计费用；静帧生成后必须由用户确认图片版本；生视频前再次确认模型、时长和预计费用。
- 涉及会员开通或外部发布前，应先向用户说明并获得确认。
- API Key、登录凭证和 Cookie 不应写进项目文件或提交到 GitHub。

## 设计边界

- HyperFrames 是确定性动画兜底，不能等同于生成式真人视频模型。
- 自动视频路线必须确认平台真实支持首尾帧；只有首帧图生视频时，应明确说明能力差异。
- 画面中的品牌、人物肖像、字体和素材仍需使用者自行确认授权。
- Vox 在本项目中指一种编辑画面风格，不代表与 Vox Media 存在合作或隶属关系。

## 开发与验证

仓库包含 GitHub Actions 验证流程，会在 Windows、macOS 和 Ubuntu 上检查：

- Skill 结构与元数据；
- Python 脚本语法；
- 关键引用和跨平台路径；
- 示例输入与输出约束。

修改后可先运行环境自检，再提交代码。工作流配置位于 [`.github/workflows/validate.yml`](.github/workflows/validate.yml)。

## 版权与来源

P-Broll 在保留原项目版权与来源信息的基础上继续改编维护：

- [`gbro-collage-broll`](https://github.com/pyang5166/gbro-collage-broll)，© 2026 狗哥笔记；
- [`vox-director`](https://github.com/Alisa0808/vox-director)，© 2026 Atlas Cloud；
- 改编维护者：P-Broll contributors。

完整版权与许可信息见 [`LICENSE`](LICENSE) 和 [`NOTICE`](NOTICE)。
