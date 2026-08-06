#!/usr/bin/env python3
"""Create a manual video-generation package for either P-Broll frame mode."""

import argparse
import shutil
from pathlib import Path


PLATFORM_NOTE = """可使用任意明确支持本模式图像输入的网站。若没有常用平台，可在小云雀网页生成；
页面当前可用且满足输入要求时，优先考虑 Seedance 1.5 Pro，其次 Seedance 2.0。
注册链接：
https://xiaoyunque.jianying.com/s/z_Wf-ql547E/

如果页面有多个模型，请先确认是否有指定模型；没有偏好时再按上述顺序考察。
不同模型消耗可能不同，提交前以页面实时显示为准。新用户可能有免费积分，
具体以平台页面实时显示为准。
"""


FIRST_LAST_README = """# {title} — 手动视频生成包

模式：首帧 + 尾帧（纸拼贴组装）

## 上传文件

1. `first-frame.png`：空场首帧，先上传。
2. `last-frame.png`：完成态尾帧，后上传。
3. `video-prompt.txt`：包含英文和中文提示词。

## 推荐参数

- {duration} 秒（根据内容复杂度动态判定）
- 判定理由：{duration_reason}
- 9:16 竖版
- 720p
- 关闭自动配音、音乐和音效
- 固定镜头，不变焦、不切镜

{platform_note}
## 验收

- 第 0 秒接近纯色空场。
- 中段逐件组装，不是整体淡入。
- 最后一帧与 `last-frame.png` 基本一致。
- 无切镜、变焦、假字、logo、水印或 UI。

生成后请回传原始 MP4，由 Agent 做统一 QA。
"""


SINGLE_FIRST_README = """# {title} — 手动视频生成包

模式：单首帧图生视频（低多边形动画）

## 上传文件

1. `first-frame.png`：获准的低多边形起始画面，作为唯一图片上传。
2. `video-prompt.txt`：包含英文和中文动画提示词。

不要上传尾帧，也不要启用平台的首尾帧模式。

## 推荐参数

- {duration} 秒（根据动作与镜头复杂度动态判定）
- 判定理由：{duration_reason}
- 9:16 竖版
- 720p
- 关闭自动配音、音乐和音效
- 使用单图图生视频；镜头运动严格按提示词执行

{platform_note}
## 验收

- 真实首帧与 `first-frame.png` 的主体、构图和场景基本一致。
- 主要动作与镜头运动符合提示词，并在结尾自然稳定。
- 低多边形切面、人物身份、灰阶和红色强调保持一致。
- 无几何融化、面部漂移、额外肢体、切镜、假字、logo、水印或 UI。

生成后请回传原始 MP4，由 Agent 做统一 QA。
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("first-last", "single-first"), default="first-last")
    parser.add_argument("--item-dir", required=True, help="Beat item directory")
    parser.add_argument("--prompt-en", required=True, help="English prompt file")
    parser.add_argument("--prompt-cn", required=True, help="Chinese prompt file")
    parser.add_argument("--first-frame", default=None, help="Approved first-frame file")
    parser.add_argument("--last-frame", default=None, help="Approved last-frame file for first-last mode")
    parser.add_argument("--title", default="P-Broll")
    parser.add_argument("--duration", required=True, type=int, help="Target duration, 4-15 seconds")
    parser.add_argument("--duration-reason", default="根据动作单元与关系复杂度计算")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    if not 4 <= args.duration <= 15:
        parser.error("--duration 必须在 4–15 秒之间")

    item = Path(args.item_dir).resolve()
    frames = item / "frames"
    if args.first_frame:
        first = Path(args.first_frame).resolve()
    elif args.mode == "single-first":
        first = frames / "first-frame-original.png"
    else:
        first = frames / "first-frame.png"

    last = Path(args.last_frame).resolve() if args.last_frame else frames / "last-frame.png"
    prompt_en = Path(args.prompt_en).resolve()
    prompt_cn = Path(args.prompt_cn).resolve()

    required = [first, prompt_en, prompt_cn]
    if args.mode == "first-last":
        required.append(last)
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise SystemExit("Missing required file(s): " + ", ".join(map(str, missing)))

    out = Path(args.output_dir).resolve() if args.output_dir else item / "manual-generation"
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(first, out / "first-frame.png")
    if args.mode == "first-last":
        shutil.copy2(last, out / "last-frame.png")
    else:
        stale_last = out / "last-frame.png"
        if stale_last.is_file():
            stale_last.unlink()

    combined = (
        "ENGLISH PROMPT\n\n"
        + prompt_en.read_text(encoding="utf-8").strip()
        + "\n\nCHINESE PROMPT\n\n"
        + prompt_cn.read_text(encoding="utf-8").strip()
        + "\n"
    )
    (out / "video-prompt.txt").write_text(combined, encoding="utf-8")
    template = SINGLE_FIRST_README if args.mode == "single-first" else FIRST_LAST_README
    (out / "README.md").write_text(
        template.format(
            title=args.title,
            duration=args.duration,
            duration_reason=args.duration_reason,
            platform_note=PLATFORM_NOTE,
        ),
        encoding="utf-8",
    )
    print(out)


if __name__ == "__main__":
    main()
