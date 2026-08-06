#!/usr/bin/env python3
"""Select a 4-15 second P-Broll duration from visual action complexity."""

from __future__ import annotations

import argparse
import json
import math


ACTION_SECONDS = {
    "simple": 0.9,
    "coordinated": 1.3,
    "transform": 1.8,
}
RELATION_SECONDS = {
    "none": 0.0,
    "simple": 0.8,
    "complex": 1.5,
}
RELATION_LABELS = {
    "none": "无新增关系",
    "simple": "简单连接/对照",
    "complex": "复杂因果/转化",
}


def parse_platform_durations(value: str | None) -> list[int]:
    if not value:
        return []
    try:
        durations = sorted({int(item.strip()) for item in value.split(",") if item.strip()})
    except ValueError as exc:
        raise argparse.ArgumentTypeError("平台时长必须是逗号分隔的整数") from exc
    if not durations or any(duration < 4 or duration > 15 for duration in durations):
        raise argparse.ArgumentTypeError("平台时长档位必须全部位于 4–15 秒")
    return durations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--frame-mode",
        choices=("first-last", "single-first"),
        default="first-last",
        help="first-last for collage assembly; single-first for low-poly image-to-video",
    )
    parser.add_argument("--simple", type=int, default=0, help="Simple action units")
    parser.add_argument("--coordinated", type=int, default=0, help="Coordinated action units")
    parser.add_argument("--transform", type=int, default=0, help="Transform action units")
    parser.add_argument("--relation", choices=RELATION_SECONDS, default="none")
    parser.add_argument("--complex-scene", action="store_true", help="Use a longer opening hold")
    parser.add_argument("--end-hold", type=float, default=None, help="Override final stabilization hold")
    parser.add_argument("--user-duration", type=int, default=None, help="Explicit user duration, 4-15s")
    parser.add_argument("--platform-durations", default=None, help="Available slots, e.g. 5,10,15")
    args = parser.parse_args()

    for name in ("simple", "coordinated", "transform"):
        if getattr(args, name) < 0:
            parser.error(f"--{name} 不能为负数")
    if args.user_duration is not None and not 4 <= args.user_duration <= 15:
        parser.error("--user-duration 必须在 4–15 秒之间")
    if args.end_hold is not None:
        hold_range = (1.2, 2.0) if args.frame_mode == "first-last" else (0.8, 1.5)
        if not hold_range[0] <= args.end_hold <= hold_range[1]:
            parser.error(
                f"--end-hold 在 {args.frame_mode} 模式下必须位于 "
                f"{hold_range[0]:.1f}–{hold_range[1]:.1f} 秒"
            )

    try:
        platform_durations = parse_platform_durations(args.platform_durations)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    action_units = args.simple + args.coordinated + args.transform
    if args.frame_mode == "first-last":
        initial_hold = 0.8 if args.complex_scene else 0.5
    else:
        initial_hold = 0.6 if args.complex_scene else 0.3
    end_hold = args.end_hold
    if end_hold is None:
        if args.frame_mode == "first-last":
            end_hold = 2.0 if args.relation == "complex" or action_units >= 5 else 1.2
        else:
            end_hold = 1.2 if args.relation == "complex" or action_units >= 5 else 0.8

    calculated_raw = (
        initial_hold
        + args.simple * ACTION_SECONDS["simple"]
        + args.coordinated * ACTION_SECONDS["coordinated"]
        + args.transform * ACTION_SECONDS["transform"]
        + RELATION_SECONDS[args.relation]
        + end_hold
    )

    if args.user_duration is not None:
        raw_duration = calculated_raw
        target_duration = args.user_duration
        needs_split = calculated_raw > args.user_duration
        reason = (
            f"用户明确指定 {args.user_duration} 秒；按 {action_units} 个动作单元与"
            f"{RELATION_LABELS[args.relation]}估算需要 {calculated_raw:.1f} 秒"
        )
        if needs_split:
            reason += "，当前动作无法完整容纳，需简化动作或拆分 beat"
    else:
        raw_duration = calculated_raw
        target_duration = min(15, max(4, math.ceil(raw_duration)))
        needs_split = raw_duration > 15
        reason = (
            f"{action_units} 个动作单元（简单 {args.simple}、协调 {args.coordinated}、"
            f"转化 {args.transform}），{RELATION_LABELS[args.relation]}，"
            f"原始计算 {raw_duration:.1f} 秒"
        )

    duration_submitted = None
    platform_insufficient = False
    if platform_durations and not needs_split:
        candidates = [duration for duration in platform_durations if duration >= target_duration]
        if candidates:
            duration_submitted = min(candidates)
        else:
            platform_insufficient = True

    result = {
        "frame_mode": args.frame_mode,
        "duration_target": target_duration,
        "duration_submitted": duration_submitted,
        "duration_reason": reason,
        "initial_hold": initial_hold,
        "empty_hold": initial_hold if args.frame_mode == "first-last" else None,
        "end_hold": end_hold,
        "raw_duration": round(raw_duration, 2),
        "needs_split": needs_split,
        "user_duration_insufficient": bool(args.user_duration is not None and needs_split),
        "platform_insufficient": platform_insufficient,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
