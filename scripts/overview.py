#!/usr/bin/env python3
"""Batch overview sheets from beats.json — 批量四张总览图.

前置:每个 beat 的 QA 产物已由 qa_video.sh 生成在成片同目录。
输出到项目根:still-contact-sheet.jpg / video-contact-sheet-all.jpg /
video-first-frame-all.jpg / end-frame-comparison-all.jpg

Usage: python overview.py --project <dir>
"""

import argparse
import json
import os
import subprocess
import sys


def hstack(inputs, out, w=203, h=360):
    n = len(inputs)
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for f in inputs:
        cmd += ["-i", f]
    fc = "".join(f"[{i}:v]scale={w}:{h}[s{i}];" for i in range(n)) + \
         "".join(f"[s{i}]" for i in range(n)) + f"hstack={n}"
    subprocess.run(cmd + ["-filter_complex", fc, out], check=True)


def vstack(inputs, out):
    n = len(inputs)
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

    def paths(rel_name, base="video_dir"):
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
        item_dir = b["id"]
        f = os.path.join(P, item_dir, "frames", "last-frame-original.png")
        if os.path.exists(f):
            stills.append(f)
    if len(stills) == len(beats):
        hstack(stills, os.path.join(P, "still-contact-sheet.jpg"))

    vstack(paths("contact-sheet.jpg"),
           os.path.join(P, "video-contact-sheet-all.jpg"))
    hstack(paths("video-first-frame.jpg"),
           os.path.join(P, "video-first-frame-all.jpg"), w=180, h=320)
    vstack(paths("end-frame-comparison.jpg"),
           os.path.join(P, "end-frame-comparison-all.jpg"))
    print("overview sheets ->", P)


if __name__ == "__main__":
    main()
