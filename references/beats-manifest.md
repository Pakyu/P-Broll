# beats.json — 项目唯一事实源

完整讲解片项目的所有 beat 元数据集中在项目根目录的 `beats.json`，
所有脚本（prepare / assemble / overview / qa）读它，不再把口播时长、
tempo、路径散落在文档和脚本硬编码里。

## Schema

```json
{
  "title": "两种PMF",
  "target_duration": 50,
  "canvas": { "width": 1080, "height": 1920, "fps": 24 },
  "defaults": { "theme": "editorial-halftone", "lead": 0.4 },
  "beats": [
    {
      "id": "01-提出问题",
      "line": "AI 创业者都在找 PMF，但很少有人告诉你：PMF 其实有两种。",
      "role": "hook",
      "image_generation_route": null,
      "image_generation_platform": null,
      "image_generation_model": null,
      "gate2_approved": false,
      "gate2_approved_file": null,
      "gate2_approval_note": null,
      "generation_route": null,
      "generation_platform": null,
      "generation_model": null,
      "voice_generation_route": null,
      "voice_generation_platform": null,
      "voice_generation_model": null,
      "duration_target": 8,
      "duration_submitted": 10,
      "duration_reason": "3 组物件、3 个动作单元、包含一次连接关系",
      "bg_hex": "D6A429",
      "caption": "AI 创业者都在找 PMF，\\n但很少有人告诉你：PMF 有两种",
      "video": "01-提出问题/video/run-v01/final-noaudio.mp4",
      "vo": "assembly/vo/01.wav",
      "tempo": null,
      "tail": null
    }
  ]
}
```

字段说明（路径一律相对项目根目录）：

- **role** → 决定变速档位与尾停，`null` 的 tempo/tail 由角色表推导，
  显式数值可覆盖。角色表（与 SKILL.md 变速表一致）：

  | role | tempo | tail |
  |---|---|---|
  | hook | 1.04 | 0.35 |
  | definition / mechanism | 1.10 | 0.35 |
  | risk | 1.09 | 0.35 |
  | authority | 1.05 | 0.50 |
  | synthesis | 1.07 | 0.35 |
  | closing | 1.02 | 0.85 |

- **target_duration**：完整讲解片目标总时长，通常为 45–60 秒。所有 beat 的预计时长之和应尽量控制在目标 ±3 秒；超出时调整 beat 数、旁白或动作，不把单条强行压缩。

- **generation_route**：Gate 3 才回填，可选 `agent-integrated`、
  `platform-cli`、`xiaoyunque-cli`、`manual`、`hyperframes`。Gate 1 不预设。
- **image_generation_route / image_generation_platform / image_generation_model**：
  Gate 2 回填。route 可选 `agent-integrated`、`platform-cli`、
  `xiaoyunque-cli`、`xiaoyunque-web`、`hyperframes`；完整路由见
  `image-generation-routing.md`。
- **gate2_approved / gate2_approved_file / gate2_approval_note**：图片生成并完成 QA 后，把实际版本展示给用户；只有用户明确同意该文件进入视频生成时才设为 `true`，同时记录相对路径和确认摘要。重生新版本时立即重置为 `false/null/null`，旧版本确认不得继承。
- **generation_platform / generation_model**：记录实际使用的平台与模型；
  手动生成也要根据用户回传信息尽量补全。拼装层只认 `video` 路径。
- **duration_target**：Gate 1 按 `duration-selection.md` 计算的 4–15 秒目标。
- **duration_submitted**：Gate 3 实际提交给平台的时长档位；平台支持精确时长时
  与 target 相同，只提供离散档位时选择不短于 target 的最小档位。
- **duration_reason**：记录物件组数、动作单元及关系复杂度，必须可解释。
- **video**：本文件只用于完整讲解片，因此应指向显式抽离音轨后的
  `final-noaudio.mp4`；同目录的 `final.mp4` 始终保留为模型原片。
- **voice_generation_route / voice_generation_platform / voice_generation_model**：
  旁白生成后回填。route 可选 `agent-integrated`、`dreamina-cli`、
  `external-platform`、`user-provided`；完整路由见 `audio-generation-routing.md`。
- **bg_hex**：`prepare_frames.sh` 实测回填，不手填。
- **caption**：两行制字幕文本，`\\n` 分行；`assemble.py` 自动渲染缺失的
  字幕 PNG。
- **headline**（可选）：画内标题卡纸文本（`render_headline.py` 确定性渲染，
  零假字），配套可选 `headline_accent_line` / `headline_accent_hex` /
  `headline_strip_hex` / `headline_y`（1920 基准 y 坐标，默认 150，
  按各 beat 视频高度自动折算）。通常只给 hook 和 closing beat 上标题。
- **defaults.theme**（可选）：视觉主题预设名（见 theme-presets.md，
  缺省 editorial-halftone）。**Restyle 玩法**：复制 manifest 换 theme，
  `assemble.py --manifest <变体文件>` 重跑 Gate 2/3——叙事与旁白零改动。
- **vo_duration** 不入库：拼装时 ffprobe 实测，杜绝手抄。

## 生命周期

1. Gate 1：写入 title/target_duration/beats（line/role/caption），计算每条 duration_target/reason，并核对全片总时长预算，底色进 brief 讨论
2. Gate 2：按图片生成路由执行，回填 image generation 字段；展示实际静帧并取得明确确认后回填 gate2 approval 字段，再由 `prepare_frames.sh` 回填 bg_hex
3. Gate 3：先核验 gate2 approval 与实际尾帧一致，再确认模型和费用，按视频生成路由执行并回填 duration_submitted、generation_route/platform/model 与 video
4. 旁白：按音频生成路由执行，回填 voice generation 字段并确认 `vo` 文件存在
5. 拼装：`assemble.py --project <dir>` 全自动
