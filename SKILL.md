---
name: p-broll
description: 这是一个可复用的 Agent Skill 工作流，用于创建、整理和优化口播 B-roll 与完整讲解片。它支持十套纸拼贴主题的空首帧+完成态尾帧组装动画，以及低多边形动画的单首帧图生视频；支持动态 4–15 秒单句、批量 B-roll 和 beat map 驱动的 45–60 秒讲解片。根据动作与关系复杂度判断时长，静帧按 Agent 图片能力、用户平台 CLI、小云雀、HyperFrames 动态路由，视频按 Agent 能力、平台 CLI、小云雀、手动包、HyperFrames 动态路由，旁白按 Agent 内置 TTS、即梦 CLI、其他语音平台动态路由。严格要求静帧经用户明确确认后才进入付费视频生成，图片修改只能重新文生图且禁止把旧图作为参考图。用户提到拼贴 B-roll、纸拼贴视频、半调拼贴动画、低多边形动画、单首帧图生视频、给口播配画面、动态判断视频时长、把选题视频化、整理工作流或优化 Skill 时使用。
---

# P-Broll

把一句口播压成一个清晰视觉隐喻，再按所选模式做成纸拼贴组装动画或低多边形 3D 动画。

遵守去品牌化原则：把“某媒体/某艺术家风格”转译为可描述的视觉机制，如半调网点、卡纸、奶油色 keyline、纸张阴影和平坦色场，不复制可识别签名。

## 三闸门协议

1. Gate 1：只设计视觉隐喻、主题、`frame_mode`、动作和时长，等待确认。
2. Gate 2：拼贴生成完成态静帧，低多边形生成起始首帧；完成图片 QA 并展示实际图片，等待用户针对该版本明确确认。
3. Gate 3：仅在 Gate 2 明确通过后继续。拼贴准备首尾帧；低多边形直接使用获准的单首帧。确认视频模型与费用后再执行生成和 QA。

Gate 2 是不可预先放弃的费用闸门。即使用户在开始前说“直接跑完”“你自己决定”或同意连续执行，也必须在静帧实际生成并展示后暂停；只有用户明确表示该版本图片可以用于生视频，才可进入 Gate 3。沉默、之前的概括授权、Agent 自己判断“看起来没问题”都不算确认。批量项目可让用户一次确认联系表中的多个明确编号，但只放行被点名通过的条目。

## 环境自检

先运行与系统对应的脚本：

```powershell
pwsh -NoProfile -File <本skill目录>/scripts/check_setup.ps1
```

```bash
bash <本skill目录>/scripts/check_setup.sh
```

自检验证 Python、Pillow、中文字体、ffmpeg、ffprobe，并报告 Node/npx 版本与即梦 CLI 语音能力；macOS/Linux 额外检查拼贴首尾帧取色所需的 `xxd`。不要在 Gate 1 前要求任何特定平台的账号、CLI 或 API Key。

## 成功标准

- 一句话只表达一个隐喻；单镜头只保留一个主要动作和必要辅助动作。
- `theme` 与 `frame_mode` 匹配：十套拼贴主题为 `first-last`；
  `low-poly-animation` 为 `single-first`。
- 拼贴：关键物件不超过 4 组，平坦强色场，黑白 halftone 摄影剪贴为骨架，
  纸片有清晰裁切边、奶油色 keyline、柔和阴影与纸张颗粒；动作是
  assemble-from-empty，不是整体淡入或慢 zoom。
- 低多边形：人物、物体和环境具有一致三角切面，黑白灰为主、红色克制点题，
  人物/物体拓扑稳定；动作和镜头从确认首帧自然展开，不要求尾帧匹配。
- 两种模式都无模型生成字幕、口播全文、logo、水印或 UI。
- 默认目标：9:16、动态 4–15 秒、720×1280。根据内容复杂度选最短可读时长；普通 B-roll 直接保留并交付模型原始视频，不剥离音轨、不生成无音频版，也不改变帧率或编码；只有用户明确需要完整讲解片时才额外抽离音频。

### 色彩语义

| 底色 | 语意 |
|---|---|
| 焦橙 / 红 | 时间消耗、劳动、紧迫 |
| 芥末黄 | 工具、警示、经验漏失 |
| 墨绿 / 深青 | 认知、判断、协作、自动执行 |
| 深紫 | 规范、沉淀、长期记忆 |

以上色彩语义用于拼贴主题。点色优先在奶油白、芥末黄、橙一族内取。
低多边形模式固定以黑白灰/炭黑为骨架，红色仅标记关键对象、冲突或风险。

## 项目结构

```text
<project>/
├── brief.md
├── beats.json                       # 完整讲解片才需要
├── gate2-qa.md / gate3-qa.md
├── still-contact-sheet.jpg
├── video-contact-sheet-all.jpg
├── video-first-frame-all.jpg
├── frame-comparison-all.jpg
├── assembly/vo/                     # 完整讲解片逐 beat 旁白
│   ├── 01.wav
│   └── 02.wav
└── 01-概念名/
    ├── imagegen-prompt.txt
    ├── hyperframes-still/             # 仅静帧最终兜底需要
    │   ├── frame.md
    │   ├── index.html
    │   └── snapshots/
    ├── video-prompt.txt
    ├── video-prompt-cn.txt
    ├── frames/
    │   ├── last-frame-original.png    # first-last 拼贴完成态
    │   ├── first-frame-original.png   # single-first 低多边形起始画面
    │   ├── first-frame.png            # 仅拼贴准备出的空首帧
    │   ├── last-frame.png             # 仅拼贴标准尾帧
    │   └── bg-hex.txt                 # 仅拼贴需要
    ├── manual-generation/
    │   ├── README.md
    │   ├── first-frame.png
    │   ├── last-frame.png             # single-first 模式不存在
    │   └── video-prompt.txt
    └── video/run-v01/
        ├── final.mp4
        ├── final-noaudio.mp4          # 仅完整讲解片需要
        ├── contact-sheet.jpg
        ├── video-first-frame.jpg
        ├── video-last-frame.jpg
        ├── end-frame-comparison.jpg   # first-last
        └── start-frame-comparison.jpg # single-first
```

## Gate 1：隐喻设计

对每条文稿交付：

- 核心意思
- 情绪与动作动词
- 一句话视觉命题
- 中文主题名称、内部 `theme` ID 与 `frame_mode`
- 拼贴：不超过 4 组关键物件、底色/点色与预期组装顺序
- 低多边形：起始场景、主体初始姿态、主要/辅助动作、镜头运动、红色强调对象
- 动作单元及其类型（简单 / 协调 / 转化）
- `duration_target`（4–15 秒）与 `duration_reason`

读取 `references/duration-selection.md`，再运行 `scripts/select_duration.py` 计算时长；
`--frame-mode` 必须与主题一致。用户明确指定 4–15 秒时优先服从，但仍按动作单元做安全检查；若脚本返回 `user_duration_insufficient=true`，不擅自改长时长，先简化动作或拆 beat。未指定时按动作单元计算并说明理由。拼贴物件过多、缠绕穿插关系复杂时，尾帧更容易漂移；低多边形动作或镜头过多时更容易出现拓扑和身份漂移。批量内容优先形成叙事弧，并保持统一主题。

```bash
python <本skill目录>/scripts/select_duration.py \
  --frame-mode first-last \
  --simple 2 --coordinated 1 --transform 0 --relation simple \
  --platform-durations 5,10,15
```

完整讲解片先从 `references/narrative-arcs.md` 选择叙事弧，再写 `beats.json`；字段见 `references/beats-manifest.md`。

## Gate 1.5：视觉主题试选

需要整片统一风格时，从 `references/theme-presets.md` 选 2–4 套候选，用同一复杂 beat 各生成一张，用户选定后只锁定文字化的风格字段、色板和构图规则。向用户展示时优先使用中文名称，并在括号中保留英文 ID：编辑半调拼贴（`editorial-halftone`，默认）、中国水墨木刻拼贴（`chinese-ink`）、瑞士现代主义拼贴（`swiss-modern`）、苏联构成主义拼贴（`soviet-constructivist`）、新闻剪报编辑风（`newsprint-editorial`）、70 年代迷幻拼贴（`70s-groovy`）、朋克手工杂志拼贴（`punk-zine`）、原子时代未来主义（`atomic-age`）、WPA 复古宣传画（`wpa-poster`）、镀金装饰艺术（`gilded-deco`）。用户说中文名或英文 ID 时，映射到同一个预设；写入 `beats.json` 或 manifest 时始终保存英文 ID。后续图片重复使用完整文字规范，不把胜出图作为生图参考图。

低多边形动画（`low-poly-animation`）是独立非拼贴模式，不与十套拼贴主题混为一表。用户选择后读取 `references/low-poly-animation.md`，设置 `frame_mode=single-first`；若拿它与拼贴风格试选，必须明确说明后续生成步骤不同。英文 ID 仍写入 manifest。

## Gate 2：生成静帧

生成前读取 `references/image-generation-routing.md`；低多边形模式同时读取
`references/low-poly-animation.md`。严格按以下顺序执行，一旦某级可用就停止向下寻找：

1. Agent 自带或已集成的图片生成功能；在 Codex 中优先使用内置 `image_gen`。
2. 用户常用或指定图片平台的官方 CLI。
3. 推荐小云雀；优先使用其 CLI，用户不使用 CLI 时可转小云雀网页手动生成。
4. 前述路线都不可用或用户不会操作时，拼贴可使用 HyperFrames 输出确定性静帧兜底；低多边形不得用 HyperFrames 冒充 3D 生图。

不要在 Agent 图片能力可用时推荐外部平台。首次付费或扣积分生图前说明消耗并征得用户确认；失败后不自动换模型或重复扣费。

平台 CLI 暴露多个生图模型时，先列出当前真实可用模型、尺寸能力和单张积分/费用，并询问用户是否指定模型。用户没有偏好或不知道怎么选时，在平台确实提供的型号中优先考察 **Seedream 5.0 Pro、NanoBanana、GPT Image 2**，按当前价格、9:16 支持和画面需求给出建议；这些是候选名，不代表所有平台都存在，也不得跳过费用确认。费用无法可靠查询时明确说明未知，只有用户接受未知消耗后才提交。

### 拼贴完成态静帧 prompt 模板（`first-last`）

```text
Purpose: final still frame for a 9:16 image-to-video B-roll clip
Primary request: Create a finished editorial paper-collage image expressing [一句话视觉命题].
Scene/backdrop: perfectly flat [颜色] paper field [hex] with subtle uncoated paper fiber.
Style/medium: premium editorial stop-motion paper collage; black-and-white halftone photographic cut-outs mixed with selective [点色] colored cardstock.
Composition/framing: vertical 9:16 locked poster frame; central subject within the middle 70 percent; generous negative space; [N] large separable paper groups for later assemble-from-empty animation.
Materials/textures: visible halftone dots, crisp machine-cut edges, warm-cream keylines and soft physical shadows.
Constraints: [必须一眼看懂的关系].
Avoid: typography, readable letters, numerals, logos, watermark, UI, subtitles, glossy 3D, photoreal environment, clutter.
```

便签、卡片、书页类物件追加：`carrying only abstract wavy squiggle doodle lines — absolutely no letters or words`。

### 低多边形起始首帧（`single-first`）

使用 `references/low-poly-animation.md` 的首帧 prompt 模板。它表达动作尚未开始的
起始状态，保存为 `<item>/frames/first-frame-original.png`；不要生成完成态尾帧。

生成流程：

1. 把完整 prompt 写入 `<item>/imagegen-prompt.txt`。
2. 按图片生成路由选择工具，每条静帧单独生成。拼贴保存为
   `<item>/frames/last-frame-original.png`；低多边形保存为
   `<item>/frames/first-frame-original.png`。
3. 记录实际 `image_generation_route/platform/model`；HyperFrames 兜底时 model 写 `deterministic-html-snapshot`。
4. 批量时先做 1–2 张试水；后续只重复使用锁定后的完整文字风格描述，不上传任何已生成图片作为生图参考。
5. QA：拼贴检查隐喻、色场、纸张质感、物件组数和留白；低多边形检查切面、人物/物体结构、灰阶红色体系、起始动作和镜头空间。两种模式都检查假字/logo/水印/UI 和同批一致性。
6. 展示实际静帧和 QA 结论，明确说明它在当前模式中是“完成态尾帧”还是“起始首帧”，询问用户是否批准该文件进入视频生成。在 `gate2-qa.md` 记录 `frame_mode`、获准文件版本和用户确认内容；完整讲解片还要回填 `gate2_approved=true` 与 `gate2_approved_file`。
7. 用户要求修改时，保留旧版并递增 `-v2`、`-v3`，把反馈改写进一份全新的完整 prompt，然后执行纯文生图。**禁止把旧图、其裁剪图、截图、蒙版、控制图或任何由旧图派生的图像作为参考输入，也禁止使用 image-to-image、局部重绘或扩图来修改。**这条禁令适用于 Agent 图片工具、平台 CLI、小云雀和其他生图方式。若当前路线不能纯文生图，切换到可纯文生图的上级路线或报告阻塞，不得退回参考图修改。
8. 每次重生后重新执行 QA、展示新版本并等待确认；旧版本的确认不自动继承。

HyperFrames 只负责拼贴排版、CSS/SVG 纸片、纹理与已有合法素材的确定性合成，不能凭空生成摄影人物、低多边形 3D 人物或复杂场景。使用拼贴兜底时必须说明视觉能力会降级；低多边形没有生成式首帧路线时交付 prompt 等待用户手动生成或回传，不得把 HTML 截图描述成低多边形 AI 生图结果。

## Gate 3：生成视频

进入本节前先核对：`gate2-qa.md` 已记录用户对当前静帧文件的明确确认；完整讲解片对应 beat 的 `gate2_approved` 必须为 `true`，且 `gate2_approved_file` 必须与即将使用的图像一致。拼贴核对完成态尾帧，低多边形核对起始首帧。任一条件不满足就停止，不准备付费视频任务。

### 1. 按 `frame_mode` 准备图像输入

`first-last` 拼贴：从过审完成态静帧采样实际底色，生成纯色空首帧和标准尾帧：

```powershell
pwsh -NoProfile -File <本skill目录>/scripts/prepare_frames.ps1 <item-dir> [采样点x:y]
```

```bash
bash <本skill目录>/scripts/prepare_frames.sh <item-dir> [采样点x:y]
```

脚本输出：`bg-hex.txt`、`first-frame.png`、`last-frame.png`。默认采样点为左上角 `28:58`；物件贴边时换干净色场坐标。

`single-first` 低多边形：直接使用过审的
`frames/first-frame-original.png` 作为唯一图像输入。不要运行 `prepare_frames.*`，
不要生成空首帧或尾帧。

### 2. 写视频 prompt

`first-last` 拼贴使用：

```text
Target duration: approximately [duration_target] seconds. Keep the exact empty first frame visible for [0.5–0.8] seconds.

Paper-collage stop-motion assembly, using Image 1 as the exact empty first frame and Image 2 as the exact completed last frame. In one continuous locked-off vertical shot, open on the empty flat [color] paper field.

Assemble the scene piece by piece with crisp physical stop-motion timing: [按时间段描述各动作单元如何 slide in / snap into place / 展开 / 完成关系]. Use the middle of the clip for assembly, then hold the supplied completed composition unchanged for the final [1.2–2.0] seconds.

Preserve the exact 9:16 framing, [实测 hex] color field, cardstock accents, uncoated paper grain, halftone dots, cream keylines, crisp cut edges and soft shadows. Restrained tactile 2D paper craft only.

No scene cuts, no camera movement, no zoom, no new objects, no text, no letters, no numbers, no logos, no watermark, no UI.
```

`single-first` 低多边形使用 `references/low-poly-animation.md` 的动画 prompt
模板：从确认首帧开始，描述主体动作、辅助动作、环境效果和克制镜头运动；保持
低多边形切面、人物身份、灰阶红色体系和拓扑稳定，不要求尾帧匹配。

把 `duration_target` 和时间分配写进 prompt，再保存到 `<item>/video-prompt.txt`。默认提供英文版；手动生成包再附中文版，便于不同网站使用。

需要手动生成包时，再写 `<item>/video-prompt-cn.txt`，然后运行：

```bash
python <本skill目录>/scripts/create_manual_package.py --item-dir <item> \
  --prompt-en <item>/video-prompt.txt --prompt-cn <item>/video-prompt-cn.txt \
  --title "<概念名>" --duration <4-15> --duration-reason "<判定理由>"
```

低多边形手动包在同一命令中追加 `--mode single-first`，包内只包含首帧和提示词。

### 3. 严格按五级路由选择生成方式

读取 `references/video-generation-routing.md` 并按以下顺序执行；一旦某级可用就停止向下寻找：

1. Agent 自带或已集成的视频生成能力。
2. 用户常用或指定平台的 CLI。
3. 推荐并接入小云雀 CLI；平台当前可用且满足当前 `frame_mode` 时，优先考虑 Seedance 1.5 Pro，其次 Seedance 2.0。
4. 输出与模式匹配的手动生成包：拼贴为首尾帧 + 提示词，低多边形为单首帧 + 提示词；等待用户回传视频。
5. 只有拼贴模式且用户连手动网站生成也无法完成时，才使用 HyperFrames 做最终兜底；低多边形不进入 HyperFrames。

自动/CLI 路线必须支持 `duration_target` 或存在不短于目标的时长档位。拼贴必须显式支持**首帧 + 尾帧**；低多边形只需显式支持单张首帧 image-to-video，只支持单图的平台在该模式下合格。CLI 暴露多个视频模型时，先展示当前可用模型、与 `frame_mode` 匹配的图像输入能力、时长档位和预计积分/费用，并询问用户是否指定；用户没有偏好时，平台实际可用的前提下优先建议 **Seedance 1.5 Pro**，其次 **Seedance 2.0**。紧邻提交前再次确认静帧版本、模式、模型、时长和消耗；失败后不自动换模型或重投。费用无法可靠查询时，只有用户明确接受未知消耗才可提交。

### 4. 接收与 QA

自动生成或用户回传视频后，把模型原始文件直接保存到 `<item>/video/run-v01/final.mp4`。普通 B-roll 不另存无音频版，直接运行：

```powershell
pwsh -NoProfile -File <本skill目录>/scripts/qa_video.ps1 <成片.mp4> <确认静帧.png> [输出目录] [bg-hex]
```

```bash
bash <本skill目录>/scripts/qa_video.sh <成片.mp4> <确认静帧.png> [输出目录] [bg-hex]
```

低多边形必须加 `-Mode single-first`（PowerShell）或
`--mode single-first`（bash），并把确认首帧作为第二个参数。

QA 标准：

- 拼贴：首帧接近纯色空场，中段逐件组装而非整体淡入，尾帧与确认完成态
  静帧一致；无切镜、zoom、3D 化或写实漂移。
- 低多边形：真实首帧与确认首帧基本一致；动作、环境效果和镜头运动符合 prompt；
  低多边形切面、人物身份、灰阶红色体系贯穿全程；无几何融化、面部漂移、
  肢体增生、物体闪现消失、突然写实化或意外切镜；不要求尾帧匹配图片。
- 两种模式都无假字、logo、水印或 UI。
- 直接交付模型原始视频；原视频有音轨就保留，没有音轨也不补音。平台输出帧率、编码或封装不同不自动转码，除非用户要求。
- 实际时长应与 `duration_submitted` 接近；若平台返回时长档位有偏差，记录真实值，不自动裁切。
- 只有用户明确制作完整讲解片时，才为拼装额外生成 `final-noaudio.mp4`；模型原片始终保留。

逐条结论写入 `gate3-qa.md`，同时记录 `frame_mode`。失败只重跑失败条目；记录平台、模型、提交次数和实际积分/费用。

批量项目运行 `scripts/overview.py --project <dir>` 生成四张总览图。

## 完整讲解片模式

先确定 45–60 秒的全片目标并写入 `beats.json.target_duration`，通常拆成 8–10 个 beat，每 beat 一句 20–30 字口播和一个隐喻。每个 beat 独立计算 4–15 秒，不统一写死；所有 beat 预计时长之和应尽量落在全片目标 ±3 秒，必要时调整 beat 数或合并/拆分内容。`beats.json` 是唯一事实源；生成平台在 Gate 3 才选择，不要在 Gate 1 预设供应商。

- 旁白：生成前读取 `references/audio-generation-routing.md`，严格按 **Agent 自带/内置 TTS → 即梦 CLI → 推荐其他语音平台或用户回传** 选择；一旦上一级可用就停止向下寻找。
- 即梦约束：先读取当前 `dreamina --help`；只有 CLI 真实暴露 TTS/语音命令时才调用。当前 CLI 没有语音命令时进入其他平台路线，不得编造命令，也不得用视频原声冒充旁白。
- 其他平台：询问用户是否有常用语音平台或官方 CLI；没有时整理逐 beat 文本、音色与语气要求，推荐用户选择可用平台生成后回传。
- 文件：每个 beat 输出到 `assembly/vo/<序号>.wav`，并在 manifest 记录实际 voice route、platform、model；拼装前检查所有 `vo` 文件存在。
- 节奏：hook 1.04、definition/mechanism 1.10、risk 1.09、authority 1.05、synthesis 1.07、closing 1.02；重要话慢，收尾停顿更长。
- 字幕：用 `scripts/render_caption.py` 渲染两行字幕 PNG。
- 视频静音素材：只有用户明确需要完整讲解片时，对每个 beat 运行 `qa_video.ps1 ... -StripAudio` 或 `qa_video.sh ... --strip-audio`，生成 `final-noaudio.mp4`，并把 manifest 的 `video` 指向该文件。
- 拼装：运行 `python <本skill目录>/scripts/assemble.py --project <dir>`；以旁白时长为主时钟，不足的视频用尾帧定格补齐。
- 节奏调整只改 manifest 后重拼，不重生已经过审的视频素材。

## 常见问题

- 组装感弱：减少物件组数，把动作写成明确的 `slide in / snap into place` 顺序。
- 动作来不及完成：重新按 `duration-selection.md` 计算；平台档位不足时拆 beat，不静默压缩。
- 画面简单却过长：选择更短档位；拼贴保留至少 1.2 秒完成态，低多边形保留至少 0.8 秒动作结束稳定时间，不用慢 zoom 填时长。
- 拼贴尾帧漂移：强调第二张图是 exact completed last frame；仍漂移则简化空间关系。
- 低多边形几何或人物漂移：减少主体与辅助动作，收小镜头幅度，在 prompt 中锁定 faceted geometry、identity、anatomy 和 object topology；不要补尾帧。
- 出现假字：回到 Gate 2 重生静帧，不用视频 prompt 修补。
- 用户要求改静帧：把反馈写入全新 prompt 后纯文生图，不上传旧图或任何派生图；新版本重新走 Gate 2 确认。
- 用户开始前说“直接跑完”：可以连续完成不付费的规划和检查，但静帧生成后仍必须暂停等待当前图片版本的明确确认。
- CLI 有多个模型：先问用户是否指定；没有偏好再按平台实时可用性、费用和质量推荐候选，未经确认不提交。
- Agent 没有图片生成能力：先询问用户常用图片平台 CLI；没有时推荐小云雀。拼贴最后可转 HyperFrames 静帧兜底；低多边形只能等待生成式平台或用户回传首帧。
- HyperFrames 静帧缺少摄影主体：要求用户提供合法素材，或改用抽象 CSS/SVG 纸片隐喻；不要声称它能进行生成式摄影生图。
- 平台没有尾帧参数：拼贴模式不可使用并转下一级；低多边形模式若支持单图图生视频则可以使用。
- 用户没有 CLI：先推荐小云雀；不愿开通则输出手动生成包。
- 拼贴用户不会手动生成：最后才转 HyperFrames；接受其刚体动作、无纸张形变的限制。
- 低多边形用户不会手动生成：HyperFrames 不能等价兜底，停在单首帧手动包并等待合格平台或用户回传。
- 模型视频带音频：普通 B-roll 保留原始音轨并直接交付；仅完整讲解片额外创建 `final-noaudio.mp4`，供独立旁白拼装使用。
- 即梦 CLI 没有语音命令：不要把图片/视频生成命令当成 TTS；记录探测结果后询问用户的其他语音平台。
- 用户没有语音平台：整理逐 beat 文本、统一音色和语气要求，让用户选择其他平台生成并回传；缺少旁白文件时不要拼装完整讲解片。

## 边界

- 拼贴需要逐层编辑、精确遮挡或逐帧调入场时，直接使用 HyperFrames 类分层工作流。
- 只需要视频提示词时，不进入完整生成流程。
- 真人口播实拍、产品实拍广告不使用本视觉流程；低多边形人物是生成式风格化角色，不是实拍替代。

## 出处

工作流最初改编自 [gbro-collage-broll](https://github.com/pyang5166/gbro-collage-broll)（MIT，© 2026 狗哥笔记），并结合实际使用迭代为 Agent 能力检测、平台 CLI、小云雀、手动生成包、HyperFrames 拼贴兜底与低多边形单首帧模式的供应商中立流程。同类开源参考：[vox-director](https://github.com/Alisa0808/vox-director)（MIT，© 2026 Atlas Cloud）。完整许可与上游声明见 `LICENSE`、`NOTICE`。

改编维护者：P-Broll contributors。
