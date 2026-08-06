#!/usr/bin/env python3
"""Batch overview sheets from beats.json — 批量总览图.

前置:每个 beat 的 QA 产物已由 qa_video.sh 生成在成片同目录。
输出到项目根:still-contact-sheet.jpg / video-contact-sheet-all.jpg /
video-first-frame-all.jpg / frame-comparison-all.jpg。纯首尾帧或纯单首帧项目
另外保留对应的 end/start-frame-comparison-all.jpg 兼容名。

Usage: python overview.py --project <dir>
"""

import argparse
import json
import os
import shutil
import subprocess
import sys


def hstack(inputs, out, w=203, h=360):
    n = len(inputs)
    if n == 1:
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", inputs[0],
             "-vf", f"scale={w}:{h}", out],
            check=True,
        )
        return
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for f in inputs:
        cmd += ["-i", f]
    fc = "".join(f"[{i}:v]scale={w}:{h}[s{i}];" for i in range(n)) + \
         "".join(f"[s{i}]" for i in range(n)) + f"hstack={n}"
    subprocess.run(cmd + ["-filter_complex", fc, out], check=True)


def vstack(inputs, out):
    n = len(inputs)
    if n == 1:
        shutil.copy2(inputs[0], out)
        return
    widths = []
    for path in inputs:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width", "-of", "csv=p=0", path],
            capture_output=True, text=True,
        )
        if r.returncode != 0 or not r.stdout.strip():
            sys.exit(f"无法读取总览图片宽度: {path}")
        widths.append(int(r.stdout.strip().splitlines()[0]))
    max_width = max(widths)
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for f in inputs:
        cmd += ["-i", f]
    fc = "".join(
        f"[{i}:v]pad={max_width}:ih:(ow-iw)/2:0:color=0x1A1A1A[p{i}];"
        for i in range(n)
    ) + "".join(f"[p{i}]" for i in range(n)) + f"vstack={n}"
    subprocess.run(cmd + ["-filter_complex", fc, out], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()
    P = os.path.abspath(args.project)
    with open(os.path.join(P, "beats.json"), encoding="utf-8") as f:
        mf = json.load(f)
    beats = mf.get("beats")
    if not isinstance(beats, list) or not beats:
        sys.exit("beats.json 的 beats 必须是非空数组")

    defaults = mf.get("defaults") or {}

    def frame_mode(beat):
        return beat.get("frame_mode") or defaults.get("frame_mode") or "first-last"

    def paths(rel_name):
        out = []
        for b in beats:
            vdir = os.path.join(P, os.path.dirname(b["video"]))
            f = os.path.join(vdir, rel_name)
            if not os.path.exists(f):
                sys.exit(f"缺 {f}(先对每条成片跑 qa_video.sh)")
            out.append(f)
        return out

    stills = []
    for b in beats:
        approved = b.get("gate2_approved_file")
        if approved:
            f = os.path.join(P, approved)
        else:
            filename = (
                "first-frame-original.png"
                if frame_mode(b) == "single-first"
                else "last-frame-original.png"
            )
            f = os.path.join(P, b["id"], "frames", filename)
        if os.path.exists(f):
            stills.append(f)
    if len(stills) == len(beats):
        hstack(stills, os.path.join(P, "still-contact-sheet.jpg"))

    vstack(paths("contact-sheet.jpg"),
           os.path.join(P, "video-contact-sheet-all.jpg"))
    hstack(paths("video-first-frame.jpg"),
           os.path.join(P, "video-first-frame-all.jpg"), w=180, h=320)
    comparisons = []
    modes = []
    for b in beats:
        mode = frame_mode(b)
        modes.append(mode)
        filename = (
            "start-frame-comparison.jpg"
            if mode == "single-first"
            else "end-frame-comparison.jpg"
        )
        vdir = os.path.join(P, os.path.dirname(b["video"]))
        comparison = os.path.join(vdir, filename)
        if not os.path.exists(comparison):
            sys.exit(f"缺 {comparison}(先按 frame_mode 跑 qa_video)")
        comparisons.append(comparison)
    generic = os.path.join(P, "frame-comparison-all.jpg")
    vstack(comparisons, generic)
    if all(mode == "first-last" for mode in modes):
        shutil.copy2(generic, os.path.join(P, "end-frame-comparison-all.jpg"))
    elif all(mode == "single-first" for mode in modes):
        shutil.copy2(generic, os.path.join(P, "start-frame-comparison-all.jpg"))
    print("overview sheets ->", P)


if __name__ == "__main__":
    main()
