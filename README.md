# P-Broll

[![Validate P-Broll](https://github.com/Pakyu/P-Broll/actions/workflows/validate.yml/badge.svg)](https://github.com/Pakyu/P-Broll/actions/workflows/validate.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

把口播文稿、观点句或完整选题，转成编辑纸拼贴 B-roll 或低多边形 3D 动画。

Turn spoken lines into editorial paper-collage or low-poly 3D B-roll with explicit approval gates, dynamic 4–15 second timing and mode-aware frame generation.

P-Broll 是一个供 AI Agent 使用的 Skill，不是独立 GUI 软件。它负责理解内容、设计视觉隐喻、生成并确认静帧、按风格准备视频输入、调用视频工具并完成 QA；具体使用哪个图片、视频或语音模型，由当前 Agent 能力和用户选择共同决定。

## 效果

- 黑白 halftone 摄影剪贴 + 平坦强色场 + 少量彩色卡纸点缀。
- 奶油色 keyline、纸张颗粒、裁切边和柔和实体阴影。
- 元素从空场逐件滑入、落位、连接或展开，而不是整体淡入或慢 zoom。
- 也支持黑白灰低多边形 3D 场景，以红色强调重点，用单首帧驱动物体、人物和镜头运动。
- 默认 9:16、720×1280，按内容复杂度动态选择 4–15 秒。
- 支持单条 B-roll、批量 B-roll，以及 beat map 驱动的 45–60 秒完整讲解片。

## 视觉风格与模式

纸拼贴模式内置十套主题。需要整片统一风格时，P-Broll 会先用同一个 beat 做 2–4 套风格试选。对话中优先展示中文名称，英文 ID 仅用于项目文件和 manifest：

| 中文名称 | 英文 ID | 适合内容 |
|---|---|---|
| 编辑半调拼贴（默认） | `editorial-halftone` | 观点、科技、商业 |
| 中国水墨木刻拼贴 | `chinese-ink` | 中国文化、历史、东方美学 |
| 瑞士现代主义拼贴 | `swiss-modern` | 方法论、系统、B2B |
| 苏联构成主义拼贴 | `soviet-constructivist` | 宣言、动员、强观点 |
| 新闻剪报编辑风 | `newsprint-editorial` | 新闻解读、时事 |
| 70 年代迷幻拼贴 | `70s-groovy` | 生活方式、消费、轻松话题 |
| 朋克手工杂志拼贴 | `punk-zine` | 反叛观点、亚文化 |
| 原子时代未来主义 | `atomic-age` | 科技乐观主义、未来话题 |
| WPA 复古宣传画 | `wpa-poster` | 公共议题、倡导 |
| 镀金装饰艺术 | `gilded-deco` | 高端、金融、品牌 |

内部 ID 保持英文以兼容已有项目；用户直接说中文名称即可选择对应风格。

另外提供独立的 **低多边形动画**（`low-poly-animation`）：黑白灰/炭黑低多边形 3D 人物和环境，使用清晰三角切面、电影高反差灯光及克制红色强调。它不是拼贴主题，生成流程为 `single-first`：Gate 2 只生成并确认起始首帧，Gate 3 使用该首帧和动画提示词生成视频，不准备尾帧。

## 工作流：三闸门审批

P-Broll 的核心不只是一套 prompt，而是三阶段审批。隐喻、静帧和视频分别确认，避免在错误方向上继续消耗图片或视频生成费用。

1. **Gate 1 · 隐喻与时长** — 只分析文稿，提出核心意思、视觉隐喻、关键物件、色板、组装顺序和 4–15 秒建议时长。
2. **Gate 2 · 静帧确认** — 拼贴生成完成态尾帧，低多边形生成起始首帧；完成图片 QA 并展示实际图片。只有用户明确批准当前文件版本，才能继续。
3. **Gate 3 · 视频生成** — 拼贴根据获准完成态静帧准备空首帧与尾帧；低多边形直接使用获准起始首帧。再次确认模型、时长和预计消耗后生成视频并执行模式对应 QA。

Gate 2 不可预先跳过。即使用户在开始前说“直接跑完”或让 Agent 自主决定，也必须在静帧生成并展示后暂停。沉默、概括授权和 Agent 自己判断“看起来没问题”都不算确认。批量任务可以一次批准多个明确编号，未被点名的条目不会进入视频生成。

如果用户要求修改图片，P-Broll 会保留旧版本，把反馈写入一份全新的完整提示词，再进行纯文生图。禁止把旧图、截图、裁剪图、蒙版、控制图或其他派生图片作为参考输入，也禁止使用 image-to-image、局部重绘或扩图修改。新版本需要重新 QA 和确认。

## 生成工具路由

每个阶段都先检查当前 Agent 已经具备的能力，再逐级选择替代路线；一旦某一级可用，就停止向下寻找。

### 图片生成

| 优先级 | 路线 | 说明 |
|---:|---|---|
| 1 | Agent 自带或已集成的图片能力 | Codex 环境优先使用内置图片生成；每张图都使用纯文生图 |
| 2 | 用户指定平台的官方 CLI | 先读取实时帮助、模型列表、尺寸和费用，不猜参数 |
| 3 | HyperFrames | 只为拼贴制作 CSS/SVG 确定性静帧；低多边形不使用该兜底 |

CLI 有多个生图模型时，先询问用户是否指定，并列出平台当前真实可用的型号、尺寸和单张消耗。

HyperFrames 不是生成式图片模型，不能凭空生成摄影人物、低多边形 3D 人物或复杂真实场景；拼贴缺少合法主体素材时会退化为抽象 CSS/SVG 隐喻，并明确说明能力差异。

### 视频生成

| 优先级 | 路线 | 说明 |
|---:|---|---|
| 1 | Agent 自带或已集成的视频能力 | 必须满足当前模式的图像输入和目标时长 |
| 2 | 用户指定平台的官方 CLI | 按 CLI 当前能力调用，不使用未公开网页接口 |
| 3 | 手动生成包 | 拼贴整理首尾帧；低多边形只整理首帧；两者都附中英文提示词和操作说明 |
| 4 | HyperFrames | 仅用于拼贴的滑入、落位和堆叠兜底，不冒充低多边形 3D 动画 |

拼贴自动/CLI 路线必须显式支持首尾帧；只支持单图的平台不合格。低多边形路线正好相反：只需支持单首帧 image-to-video，不上传尾帧。

CLI 有多个视频模型时，Agent 会先展示实时可用模型、与当前模式匹配的帧输入能力、时长档位和预计费用，并询问用户是否指定。用户没有偏好时，仅在平台实际可用且满足要求的前提下优先建议 **Seedance 1.5 Pro**，其次 **Seedance 2.0**。紧邻提交前还会再次确认静帧版本、模式、模型、时长和消耗；费用无法可靠查询时，只有用户明确接受未知消耗才会提交。


### 旁白生成

旁白路线只在用户明确制作完整讲解片时启用：

1. Agent 自带或已集成、且能保存音频文件的 TTS。
2. 用户指定其他语音平台，或由用户生成后回传音频。

普通 B-roll 直接交付视频模型的原始文件：有音轨就保留，没有音轨也不补。只有完整讲解片需要统一旁白与混音时，才额外抽离音频并生成拼装素材。

## 动态时长

P-Broll 不把每条视频固定成 5 秒。它会为每个 beat 拆解简单动作、协调动作、转化动作和关系理解时间；拼贴加入空首帧与完成态停留，低多边形加入起始画面与动作结束稳定时间，计算 4–15 秒目标时长。

| 内容复杂度 | 常见情况 | 建议时长 |
|---|---|---:|
| 极简 | 1–2 组物件、1 个动作、无关系变化 | 4 秒 |
| 简单 | 2–3 组物件、2 个简单动作 | 5–6 秒 |
| 中等 | 3–4 组物件、连接或对照关系 | 7–9 秒 |
| 复杂 | 多阶段展开、因果或转化 | 10–12 秒 |
| 高复杂 | 5 个以上动作单元，需要观察完成态 | 13–15 秒 |

平台只提供离散档位时，会选择不短于目标时长的最小档位。例如目标 7 秒、平台只有 5/10 秒，则提交 10 秒。若 15 秒仍然拥挤，P-Broll 会拆 beat 或删减动作，而不是继续拉长单镜头。

## 安装

把仓库克隆到你的 Agent 能识别的 Skills 目录。不同客户端的目录可能不同，请以客户端当前配置为准。

macOS / Linux：

```bash
git clone https://github.com/Pakyu/P-Broll.git ~/.agents/skills/p-broll
```

Windows PowerShell：

```powershell
git clone https://github.com/Pakyu/P-Broll.git "$HOME\.agents\skills\p-broll"
```

如果你的客户端使用 `~/.codex/skills`、`~/.claude/skills` 或自定义目录，请替换目标路径。安装后重启或刷新 Agent 会话。

使用兼容的 Skills 安装器时，也可以安装指定 Skill：

```bash
npx skills add Pakyu/P-Broll --skill p-broll
```

## 使用

你可以直接这样说：

```text
使用 $p-broll，把这句话做成一条纸拼贴 B-roll：
“真正困难的不是找到答案，而是先问对问题。”
```

批量任务：

```text
使用 $p-broll，把下面 5 句口播分别做成 B-roll。
先给出每句的隐喻方案和动态时长，再逐条生成。
```

完整讲解片：

```text
使用 $p-broll，把“创业早期如何判断产品市场匹配”
做成一条约 50 秒的完整讲解片。
```

低多边形动画：

```text
使用 $p-broll 的“低多边形动画”，把这句话做成一条 B-roll。
只生成一个起始首帧，发给我确认后，再用首帧和动画提示词生成视频。
```

然后按 Gate 1 → Gate 2 → Gate 3 逐步确认即可。你可以让 Agent 自主决定隐喻和构图，但静帧生成后的版本确认、模型选择与费用确认仍会保留。

## 环境要求

首次使用先运行对应平台的环境自检脚本。

| 依赖 | 用途 |
|---|---|
| Python ≥ 3.10 | 时长计算、图片处理、字幕与完整讲解片拼装 |
| Pillow | 图片 QA、联系表和中文文字渲染 |
| FFmpeg / FFprobe | 拼贴首尾帧准备、两种模式的视频 QA 和成片拼装 |
| 中文字体 | 字幕与标题 PNG 渲染 |
| Node.js / npx | 仅小云雀 CLI 或 HyperFrames 路线需要；当前自检按 Node.js ≥ 22 检查 |
| `xxd` | 仅 macOS / Linux 拼贴首尾帧取色脚本需要；低多边形不需要 |

Windows：

```powershell
pwsh -NoProfile -File scripts/check_setup.ps1
```

macOS / Linux：

```bash
bash scripts/check_setup.sh
```

不要在 Gate 1 前配置不需要的平台账号、CLI 或 API Key。只有实际选中某条生成路线时，才处理对应授权。

## 目录结构

```text
p-broll/
├── SKILL.md                         # 核心工作流与三闸门协议
├── agents/openai.yaml               # Codex 界面配置
├── evals/evals.json                 # 关键行为评测
├── references/
│   ├── image-generation-routing.md  # 生图工具路由与费用规则
│   ├── video-generation-routing.md  # 按 frame_mode 选择视频工具
│   ├── low-poly-animation.md        # 低多边形单首帧工作流
│   ├── audio-generation-routing.md  # 完整讲解片旁白路由
│   ├── duration-selection.md        # 4–15 秒动态时长规则
│   └── ...
└── scripts/
    ├── check_setup.*                # Windows / macOS / Linux 环境自检
    ├── select_duration.py           # 动作复杂度与平台时长计算
    ├── prepare_frames.*             # 仅拼贴准备空首帧与标准尾帧
    ├── create_manual_package.py     # 创建首尾帧或单首帧手动包
    ├── qa_video.*                   # 按模式执行起始帧或尾帧 QA
    └── assemble.py                  # 完整讲解片拼装
```

## 验证与发布检查

本仓库按「乔木-元技能」的包结构维护。已安装乔木元技能的开发环境可以运行：

```bash
python qiaomu-meta-skill/scripts/validate_skill.py .
python qiaomu-meta-skill/scripts/trigger_eval.py . --cases evals/trigger_cases.json
python qiaomu-meta-skill/scripts/export_skill_ir.py . --output reports/skill-ir.json
```

真实平台视频提交、人工盲评和隔离安装证据未完成前，相关能力标记为 `missing evidence`。

## Troubleshooting / FAQ

**为什么必须确认静帧？**

图片方向不对却直接进入视频生成，会继续消耗更高的视频费用。先看图、再生视频，是 P-Broll 最重要的成本控制规则。

**为什么修改图片不能用旧图做参考？**

这是本 Skill 的一致性与版本隔离规则。每次修改都把反馈写回完整文字规范并重新文生图，避免旧图缺陷、构图漂移或隐藏元素被参考链继续继承。

**可以指定自己的平台和模型吗？**

可以。提供官方 CLI 安装命令或官方文档即可。Agent 会读取实时帮助，确认模型、当前模式所需的图片输入参数、时长、费用和下载方式后再调用。

**没有任何平台 CLI 怎么办？**

拼贴手动包包含首帧、尾帧和中英文提示词；低多边形手动包只包含首帧和动画提示词。拼贴用户连网页手动生成也无法完成时，才使用 HyperFrames；低多边形不使用 HyperFrames 冒充 3D 动画。

**为什么有时不是 Seedance？**

模型推荐以平台实时可用性、当前模式所需的图片输入能力、时长和费用为前提。文档中的模型名是优先候选，不代表每个平台、地区或账号都一定开放。

**P-Broll 本身收费吗？**

P-Broll 使用 MIT License，可免费使用、修改和分发。第三方图片、视频、语音模型以及平台会员可能收费，具体以用户所选平台实时显示为准。

## 边界

- HyperFrames 只兜底纸拼贴确定性图片/动画，不能等同于低多边形 3D 生成模型。
- 画面中的品牌、人物肖像、字体和素材授权由使用者确认。
- 真人口播实拍、产品实拍广告不属于本流程的主要目标；低多边形人物是风格化生成角色。
- Vox 在本项目中表示一类编辑画面语言，不代表 P-Broll 与 Vox Media 存在合作、隶属或背书关系。
- API Key、登录凭证和 Cookie 不应写入项目文件或提交到 GitHub。

## 版权与来源

P-Broll 在保留原项目版权与来源信息的基础上继续改编维护：

- [gbro-collage-broll](https://github.com/pyang5166/gbro-collage-broll)，MIT License，© 2026 狗哥笔记；
- [vox-director](https://github.com/Alisa0808/vox-director)，MIT License，© 2026 Atlas Cloud；
- 改编维护者：P-Broll contributors。

完整许可与上游声明见 [LICENSE](LICENSE) 和 [NOTICE](NOTICE)。
