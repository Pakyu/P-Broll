#!/usr/bin/env python3
"""Cross-platform CJK font discovery for P-Broll render scripts."""

from __future__ import annotations

import os
from pathlib import Path

from PIL import ImageFont


REGULAR_CANDIDATES = [
    (r"C:\Windows\Fonts\msyh.ttc", 0),
    (r"C:\Windows\Fonts\Deng.ttf", 0),
    (r"C:\Windows\Fonts\simhei.ttf", 0),
    ("/System/Library/Fonts/PingFang.ttc", 2),
    ("/System/Library/Fonts/PingFang.ttc", 0),
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),
    ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 0),
    ("/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf", 0),
    ("/usr/share/fonts/opentype/adobe-source-han-sans/SourceHanSansCN-Regular.otf", 0),
    ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
]

BOLD_CANDIDATES = [
    (r"C:\Windows\Fonts\msyhbd.ttc", 0),
    (r"C:\Windows\Fonts\Dengb.ttf", 0),
    (r"C:\Windows\Fonts\simhei.ttf", 0),
    ("/System/Library/Fonts/PingFang.ttc", 8),
    ("/System/Library/Fonts/PingFang.ttc", 2),
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 1),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 0),
    ("/usr/share/fonts/opentype/noto/NotoSansCJKsc-Bold.otf", 0),
    ("/usr/share/fonts/opentype/adobe-source-han-sans/SourceHanSansCN-Bold.otf", 0),
    ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
]


def load_font(size: int, explicit_path: str | None = None, *, bold: bool = False):
    candidates: list[tuple[str, int]] = []
    requested = explicit_path or os.environ.get("P_BROLL_FONT")
    if requested:
        candidates.append((requested, 0))
    candidates.extend(BOLD_CANDIDATES if bold else REGULAR_CANDIDATES)

    for path, index in candidates:
        if not Path(path).is_file():
            continue
        try:
            return ImageFont.truetype(path, size, index=index)
        except OSError:
            continue

    raise SystemExit(
        "找不到可用的中文字体。请安装微软雅黑、苹方或 Noto Sans CJK，"
        "或通过 --font / P_BROLL_FONT 指定字体文件。"
    )
