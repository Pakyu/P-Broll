---
name: p-broll
description: 把口播文稿、观点句或完整选题做成编辑隐喻拼贴视频（黑白半调剪贴、平坦色场、从空场逐件组装）。支持动态 4–15 秒单句 B-roll、批量 B-roll 和 beat map 驱动的 45–60 秒讲解片；根据物件组数、动作阶段和关系复杂度判断时长，静帧按 Agent 图片能力、用户平台 CLI、小云雀、HyperFrames 动态路由，视频按 Agent 能力、平台 CLI、小云雀、手动包、HyperFrames 动态路由，旁白按 Agent 内置 TTS、即梦 CLI、其他语音平台动态路由。用户提到拼贴 B-roll、纸拼贴视频、半调拼贴动画、给口播配画面、动态判断视频时长、把选题视频化或需要整理首尾帧生成包时使用。
---

# P-Broll

把一句口播压成一个清晰视觉隐喻，再做成从空色场逐件组装的编辑拼贴动画。

遵守去品牌化原则：把“某媒体/某艺术家风格”转译为可描述的视觉机制，如半调网点、卡纸、奶油色 keyline、纸张阴影和平坦色场，不复制可识别签名。

## 三闸门协议

1. Gate 1：只设计视觉隐喻，等待确认。
2. Gate 2：只生成最终静帧，等待确认。
3. Gate 3：准备首尾帧，按视频生成路由执行并完成 QA。

用户明确授权“直接跑完”时可连续执行，但仍要写 Gate 2/3 QA。批量时只放行已通过的条目。

## 环境自检

先运行与系统对应的脚本：

```powershell
pwsh -NoProfile -File <本skill目录>/scripts/check_setup.ps1
```

```bash
bash <本skill目录>/scripts/check_setup.sh
```

自检验证 Python、Pillow、中文字体、ffmpeg、ffprobe，并报告 Node/npx 版本与即梦 CLI 语音能力；macOS/Linux 额外检查首尾帧取色所需的 `xxd`。不要在 Gate 1 前要求任何特定平台的账号、CLI 或 API Key。

## 成功标准

- 一句话只表达一个隐喻，关键物件不超过 4 组。
- 背景是平坦均匀的强色场；同批统一设计语言、底色按语义变化。
- 主体以黑白 halftone photographic cut-outs 为骨架，彩色卡纸只服务信息层级。
- 纸片有清晰裁切边、奶油色 keyline、柔和阴影与纸张颗粒。
- 动作是 assemble-from-empty，不是整体淡入、漂移、晃动或慢 zoom。
- 无字幕、口播全文、logo、水印或 UI。
- 默认目标：9:16、动态 4–15 秒、720×1280。根据内容复杂度选最短可读时长；普通 B-roll 直接保留并交付模型原始视频，不剥离音轨、不生成无音频版，也不改变帧率或编码；只有用户明确需要完整讲解片时才额外抽离音频。

### 色彩语义

| 底色 | 语意 |
|---|---|
| 焦橙 / 红 | 时间消耗、劳动、紧迫 |
| 芥末黄 | 工具、警示、经验漏失 |
| 墨绿 / 深青 | 认知、判断、协作、自动执行 |
| 深紫 | 规范、沉淀、长期记忆 |

点色优先在奶油白、芥末黄、橙一族内取。

## 项目结构

```text
<project>/
├── brief.md
├── beats.json                       # 完整讲解片才需要
├── gate2-qa.md / gate3-qa.md
├── still-contact-sheet.jpg
├── video-contact-sheet-all.jpg
├── video-first-frame-all.jpg
├── end-frame-comparison-all.jpg
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
    │   ├── last-frame-original.png
    │   ├── first-frame.png
    │   ├── last-frame.png
    │   └── bg-hex.txt
    ├── manual-generation/
    │   ├── README.md
    │   ├── first-frame.png
    │   ├── last-frame.png
    │   └── video-prompt.txt
    └── video/run-v01/
        ├── final.mp4
        ├── final-noaudio.mp4          # 仅完整讲解片需要
        ├── contact-sheet.jpg
        ├── video-first-frame.jpg
        ├── video-last-frame.jpg
        └── end-frame-comparison.jpg
```

## Gate 1：隐喻设计

对每条文稿交付：

- 核心意思
- 情绪与动作动词
- 一句话视觉命题
- 不超过 4 组关键物件
- 建议底色与点色
- 预期组装顺序
- 动作单元及其类型（简单 / 协调 / 转化）
- `duration_target`（4–15 秒）与 `duration_reason`

读取 `references/duration-selection.md`，再运行 `scripts/select_duration.py` 计算时长。用户明确指定 4–15 秒时优先服从，但仍按动作单元做安全检查；若脚本返回 `user_duration_insufficient=true`，不擅自改长时长，先简化动作或拆 beat。未指定时按动作单元计算并说明理由。物件过多、缠绕穿插关系复杂时，尾帧更容易漂移。需要严格落位时使用少组数和平铺关系。批量内容优先形成叙事弧，并让相邻底色不同。

```bash
python <本skill目录>/scripts/select_duration.py \
  --simple 2 --coordinated 1 --transform 0 --relation simple \
  --platform-durations 5,10,15
```

完整讲解片先从 `references/narrative-arcs.md` 选择叙事弧，再写 `beats.json`；字段见 `references/beats-manifest.md`。

## Gate 1.5：视觉主题试选

需要整片统一风格时，从 `references/theme-presets.md` 选 2–4 套候选，用同一复杂 beat 各生成一张，用户选定后锁定全片。第一张过审图作为后续风格参考。

## Gate 2：生成静帧

生成前读取 `references/image-generation-routing.md`，严格按以下顺序执行；一旦某级可用就停止向下寻找：

1. Agent 自带或已集成的图片生成功能；在 Codex 中优先使用内置 `image_gen`。
2. 用户常用或指定图片平台的官方 CLI。
3. 推荐小云雀；优先使用其 CLI，用户不使用 CLI 时可转小云雀网页手动生成。
4. 前述路线都不可用或用户不会操作时，使用 HyperFrames 输出确定性拼贴静帧兜底。

不要在 Agent 图片能力可用时推荐外部平台。首次付费或扣积分生图前说明消耗并征得用户确认；失败后不自动换模型或重复扣费。

### 静帧 prompt 模板

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

生成流程：

1. 把完整 prompt 写入 `<item>/imagegen-prompt.txt`。
2. 按图片生成路由选择工具，每条静帧单独生成，保存到 `<item>/frames/last-frame-original.png`。
3. 记录实际 `image_generation_route/platform/model`；HyperFrames 兜底时 model 写 `deterministic-html-snapshot`。
4. 批量时先做 1–2 张试水；后续用第一张过审图作风格参考。平台不支持参考图时，重复使用锁定后的完整风格描述。
5. 重生或局部修改时保留旧版，递增 `-v2`、`-v3`。
6. QA：隐喻可读、主体集中、无假字/logo/水印/UI、留白充足、物件组数合规、同批质感统一。

HyperFrames 只负责排版、CSS/SVG 纸片、纹理与已有合法素材的确定性合成，不能凭空生成摄影人物或物件。使用该兜底时必须向用户说明视觉能力会降级，不得把 HTML 截图描述成 AI 生图结果。

## Gate 3：生成视频

### 1. 准备首尾帧

从过审静帧采样实际底色，生成纯色空首帧和标准尾帧：

```powershell
pwsh -NoProfile -File <本skill目录>/scripts/prepare_frames.ps1 <item-dir> [采样点x:y]
```

```bash
bash <本skill目录>/scripts/prepare_frames.sh <item-dir> [采样点x:y]
```

脚本输出：`bg-hex.txt`、`first-frame.png`、`last-frame.png`。默认采样点为左上角 `28:58`；物件贴边时换干净色场坐标。

### 2. 写视频 prompt

```text
Target duration: approximately [duration_target] seconds. Keep the exact empty first frame visible for [0.5–0.8] seconds.

Paper-collage stop-motion assembly, using Image 1 as the exact empty first frame and Image 2 as the exact completed last frame. In one continuous locked-off vertical shot, open on the empty flat [color] paper field.

Assemble the scene piece by piece with crisp physical stop-motion timing: [按时间段描述各动作单元如何 slide in / snap into place / 展开 / 完成关系]. Use the middle of the clip for assembly, then hold the supplied completed composition unchanged for the final [1.2–2.0] seconds.

Preserve the exact 9:16 framing, [实测 hex] color field, cardstock accents, uncoated paper grain, halftone dots, cream keylines, crisp cut edges and soft shadows. Restrained tactile 2D paper craft only.

No scene cuts, no camera movement, no zoom, no new objects, no text, no letters, no numbers, no logos, no watermark, no UI.
```

把 `duration_target` 和时间分配写进 prompt，再保存到 `<item>/video-prompt.txt`。默认提供英文版；手动生成包再附中文版，便于不同网站使用。

需要手动生成包时，再写 `<item>/video-prompt-cn.txt`，然后运行：

```bash
python <本skill目录>/scripts/create_manual_package.py --item-dir <item> \
  --prompt-en <item>/video-prompt.txt --prompt-cn <item>/video-prompt-cn.txt \
  --title "<概念名>" --duration <4-15> --duration-reason "<判定理由>"
```

### 3. 严格按五级路由选择生成方式

读取 `references/video-generation-routing.md` 并按以下顺序执行；一旦某级可用就停止向下寻找：

1. Agent 自带或已集成的视频生成能力。
2. 用户常用或指定平台的 CLI。
3. 推荐并接入小云雀 CLI；默认推荐 Seedance 2.0 mini。
4. 输出首尾帧 + 提示词的手动生成包，等待用户回传视频。
5. 只有用户连手动网站生成也无法完成时，才使用 HyperFrames 做最终兜底。

任何自动/CLI 路线都必须显式支持**首帧 + 尾帧**，并支持 `duration_target` 或存在不短于目标的时长档位；只支持单图生视频的平台不满足本 Skill 的完成态锚定要求。首次付费或扣积分提交前说明时长、消耗并征得用户确认；失败后不自动换模型或重投。

### 4. 接收与 QA

自动生成或用户回传视频后，把模型原始文件直接保存到 `<item>/video/run-v01/final.mp4`。普通 B-roll 不另存无音频版，直接运行：

```powershell
pwsh -NoProfile -File <本skill目录>/scripts/qa_video.ps1 <成片.mp4> <确认静帧.png> [输出目录] [bg-hex]
```

```bash
bash <本skill目录>/scripts/qa_video.sh <成片.mp4> <确认静帧.png> [输出目录] [bg-hex]
```

QA 标准：

- 首帧接近纯色空场；轻微边缘提前露出可接受。
- 中段能看见逐件组装，不是整体淡入。
- 无切镜、zoom、3D 化、写实漂移、假字、logo、水印或 UI。
- 尾帧与确认静帧一致；轻微细节漂移不影响语义即可放行。
- 直接交付模型原始视频；原视频有音轨就保留，没有音轨也不补音。平台输出帧率、编码或封装不同不自动转码，除非用户要求。
- 实际时长应与 `duration_submitted` 接近；若平台返回时长档位有偏差，记录真实值，不自动裁切。
- 只有用户明确制作完整讲解片时，才为拼装额外生成 `final-noaudio.mp4`；模型原片始终保留。

逐条结论写入 `gate3-qa.md`。失败只重跑失败条目；记录平台、模型、提交次数和实际积分/费用。

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
- 画面简单却过长：选择更短档位，把时间留给至少 1.2 秒的完成态，不用慢 zoom 填时长。
- 尾帧漂移：强调第二张图是 exact completed last frame；仍漂移则简化空间关系。
- 出现假字：回到 Gate 2 重生静帧，不用视频 prompt 修补。
- Agent 没有图片生成能力：先询问用户常用图片平台 CLI；没有时推荐小云雀，最后才转 HyperFrames 静帧兜底。
- HyperFrames 静帧缺少摄影主体：要求用户提供合法素材，或改用抽象 CSS/SVG 纸片隐喻；不要声称它能进行生成式摄影生图。
- 平台没有尾帧参数：不可作为自动生成路线，转下一级。
- 用户没有 CLI：先推荐小云雀；不愿开通则输出手动生成包。
- 用户不会手动生成：最后才转 HyperFrames；接受其刚体动作、无纸张形变的限制。
- 模型视频带音频：普通 B-roll 保留原始音轨并直接交付；仅完整讲解片额外创建 `final-noaudio.mp4`，供独立旁白拼装使用。
- 即梦 CLI 没有语音命令：不要把图片/视频生成命令当成 TTS；记录探测结果后询问用户的其他语音平台。
- 用户没有语音平台：整理逐 beat 文本、统一音色和语气要求，让用户选择其他平台生成并回传；缺少旁白文件时不要拼装完整讲解片。

## 边界

- 需要逐层编辑、精确遮挡或逐帧调入场时，直接使用 HyperFrames 类分层工作流。
- 只需要视频提示词时，不进入完整生成流程。
- 真人口播、产品实拍广告不使用本拼贴流程。

## 出处

工作流最初改编自 [gbro-collage-broll](https://github.com/pyang5166/gbro-collage-broll)（MIT，© 2026 狗哥笔记），并结合实际使用迭代为 Agent 能力检测、平台 CLI、小云雀、手动生成包与 HyperFrames 兜底的供应商中立流程。同类开源参考：[vox-director](https://github.com/Alisa0808/vox-director)（MIT，© 2026 Atlas Cloud）。完整许可与上游声明见 `LICENSE`、`NOTICE`。

改编维护者：P-Broll contributors。
