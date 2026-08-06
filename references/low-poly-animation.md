# 低多边形动画模式

本模式中文名称为「低多边形动画」，内部 ID 为 `low-poly-animation`，
`frame_mode` 固定为 `single-first`。它是独立的低多边形 3D 动画流程，
不是十套纸拼贴主题之一。

## 1. 视觉机制

- 人物、建筑、道具和环境由清晰可见的三角形或多边形切面构成。
- 主色为黑、白、灰和炭黑，红色只用于危险、冲突、关键对象或视觉焦点。
- 使用哑光低多边形材质、硬朗明暗分面、高反差电影灯光和深色空间。
- 人物保持简化但可辨识的五官、服装轮廓和肢体结构，不追求真人皮肤质感。
- 允许人物动作、车辆/机械运动、烟雾、火光、粒子，以及克制的推进、横移、摇摄或小幅环绕镜头。
- 不复制参考视频中的字幕、片头、品牌、logo 或水印；生成阶段不让模型写字。

避免：纸张剪贴边、半调纸片、卡纸阴影、光滑高模、真实皮肤、塑料玩具感、
过度霓虹、几何融化、面部漂移、额外肢体、物体凭空增删、可读文字、logo、
水印、字幕和 UI。

## 2. Gate 1：场景与动作设计

每个 beat 输出：

- 核心意思与一句话视觉命题。
- 起始场景、主体、环境和初始姿态。
- 一个主要动作、最多两个辅助动作。
- 镜头运动及其幅度；默认固定或缓慢推进，只有空间关系需要时才横移或小幅环绕。
- 灰阶层次、红色强调对象和灯光方向。
- `frame_mode=single-first`、`duration_target` 与 `duration_reason`。

动作应从首帧的初始状态自然开始。不要把首帧设计成动作已经完成的画面，也
不要在一条 4–15 秒镜头里塞入多个场景。需要切换地点或主体时拆 beat。

时长计算调用：

```bash
python <本skill目录>/scripts/select_duration.py \
  --frame-mode single-first \
  --simple <数量> --coordinated <数量> --transform <数量> \
  --relation <none|simple|complex> \
  [--complex-scene] [--platform-durations 5,10,15]
```

## 3. Gate 2：只生成起始首帧

低多边形模式只生成一张起始画面，不生成完成态尾帧。完整提示词写入
`<item>/imagegen-prompt.txt`，生成原图保存为
`<item>/frames/first-frame-original.png`。

### 首帧 prompt 模板

```text
Purpose: opening frame for a 9:16 image-to-video low-poly animation.
Primary scene: [一句话视觉命题与起始场景].
Subject and initial pose: [主体、服装/轮廓、初始姿态，动作尚未开始].
Environment: [低多边形空间、关键道具与层次].
Style/medium: cinematic stylized low-poly 3D animation; clearly faceted triangular geometry across characters, objects and environment; matte surfaces; simplified but coherent anatomy.
Palette: predominantly black, white, gray and charcoal, with selective red accents only on [关键对象].
Lighting: high-contrast directional cinematic lighting, deep shadows, readable silhouette, no glossy plastic reflections.
Composition/framing: vertical 9:16; subject inside the middle 70 percent; enough motion space for [主要动作与镜头方向].
Motion readiness: a stable opening pose immediately before [动作]; all geometry and objects already present for the planned shot.
Avoid: paper collage, halftone paper, photoreal skin, smooth high-poly surfaces, toy-like plastic, extra limbs, malformed hands, duplicate people, text, letters, numerals, logos, watermark, UI, subtitles.
```

Gate 2 QA：

- 全场景具有一致、清晰的低多边形切面，不是普通写实 3D 加少量几何滤镜。
- 人物身份、肢体、服装和关键物体结构正常，起始动作可继续展开。
- 灰阶层次可读，红色强调克制且指向明确。
- 画面为单一连续镜头的起点，并给主体和镜头运动留出空间。
- 无文字、logo、水印、字幕或 UI。

展示实际首帧并取得用户对该文件版本的明确批准后，才进入 Gate 3。用户要求
修改时仍执行全新纯文生图，禁止把旧图或派生图作为参考输入。

## 4. Gate 3：单首帧图生视频

直接把获准的 `first-frame-original.png` 作为唯一图像输入；不要运行
`prepare_frames.*`，不要生成空首帧或尾帧，也不要为平台虚构尾帧参数。

### 动画 prompt 模板

```text
Target duration: approximately [duration_target] seconds. Use Image 1 as the exact opening frame of one continuous vertical shot.

Begin from the supplied low-poly scene. [按时间段描述主要动作、最多两个辅助动作，以及环境中的烟雾/火光/粒子或机械运动]. Camera: [固定 / 缓慢推进 / 横移 / 小幅环绕] with restrained speed and no cuts. Let the action resolve naturally and stabilize for the final [0.8–1.2] seconds; no required end-frame match.

Preserve the subject identity, clothing silhouette, environment layout, matte faceted triangular geometry, grayscale palette, selective red accents and high-contrast directional lighting throughout. Keep faces, hands, limbs and object topology coherent from frame to frame.

No scene cuts, no sudden camera jump, no paper-collage transformation, no photoreal morphing, no smooth high-poly conversion, no geometry melting, no extra limbs, no duplicate people, no new objects, no disappearing objects, no text, no letters, no numbers, no logos, no watermark, no UI, no subtitles.
```

自动/CLI 路线的合格条件改为：明确支持单张首帧图生视频、9:16 和目标时长。
只支持首帧的平台在本模式下是合格路线；尾帧能力不是准入条件。提交前仍需
确认当前首帧版本、模型、时长、分辨率和预计费用。

手动生成包使用：

```bash
python <本skill目录>/scripts/create_manual_package.py \
  --mode single-first --item-dir <item> \
  --prompt-en <item>/video-prompt.txt \
  --prompt-cn <item>/video-prompt-cn.txt \
  --title "<概念名>" --duration <4-15> \
  --duration-reason "<判定理由>"
```

## 5. 视频 QA

运行：

```powershell
pwsh -NoProfile -File <本skill目录>/scripts/qa_video.ps1 \
  <成片.mp4> <确认首帧.png> -Mode single-first
```

```bash
bash <本skill目录>/scripts/qa_video.sh \
  <成片.mp4> <确认首帧.png> --mode single-first
```

验收：

- 视频真实首帧与确认首帧构图、身份和场景基本一致。
- 主要动作和镜头运动与 prompt 一致，节奏在目标时长内可读。
- 低多边形切面、灰阶/红色体系和人物身份贯穿全程。
- 无几何融化、面部漂移、肢体增生、物体闪现消失或突然写实化。
- 无切镜、文字、logo、水印、字幕或 UI。
- 不要求尾帧匹配某张图片；结尾只需动作自然完成并稳定。

HyperFrames 无法等价生成该模式的低多边形 3D 人物、拓扑稳定动作和电影镜头。
若没有合格的视频生成能力，停在手动生成包并等待用户回传，不把 HyperFrames
结果冒充低多边形 AI 动画。
