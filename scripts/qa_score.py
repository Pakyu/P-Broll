#!/usr/bin/env python3
"""Objective QA scores for P-Broll first-last and single-first videos.

first-last:
  first_frame_purity: empty opening field vs expected background
  end_frame_similarity: final video frame vs approved completed still

single-first:
  start_frame_similarity: first video frame vs approved opening still

Scores are lightweight visual proxies and never replace human review.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
from PIL import Image  # noqa: E402


def extract_frame(video, out, last=False):
    cmd = ["ffmpeg", "-y", "-v", "error"]
    if last:
        cmd += ["-sseof", "-0.1"]
    cmd += ["-i", video, "-frames:v", "1", out]
    subprocess.run(cmd, check=True)


def purity(frame_path, bg_hex=None, tol=20):
    im = Image.open(frame_path).convert("RGB").resize((90, 160))
    px = list(im.getdata())
    if bg_hex:
        target = tuple(int(bg_hex[i:i + 2], 16) for i in (0, 2, 4))
    else:
        corners = [px[0], px[89], px[-90], px[-1]]
        target = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    ok = sum(
        1 for p in px if all(abs(p[i] - target[i]) <= tol for i in range(3))
    )
    return ok / len(px)


def similarity(a_path, b_path):
    def gray(path):
        return list(Image.open(path).convert("L").resize((90, 160)).getdata())

    a, b = gray(a_path), gray(b_path)
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va == 0 or vb == 0:
        mae = sum(abs(x - y) for x, y in zip(a, b)) / n
        return round(max(0.0, 1.0 - mae / 255.0), 4)
    corr = cov / (va ** 0.5 * vb ** 0.5)
    return max(0.0, round((corr + 1) / 2, 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--still", required=True, help="Approved reference still")
    ap.add_argument("--mode", choices=("first-last", "single-first"), default="first-last")
    ap.add_argument("--bg-hex", default=None, help="Expected empty opening color for first-last mode")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as td:
        first = os.path.join(td, "first.png")
        extract_frame(args.video, first)
        if args.mode == "single-first":
            result = {
                "video": args.video,
                "frame_mode": args.mode,
                "start_frame_similarity": similarity(args.still, first),
            }
        else:
            last = os.path.join(td, "last.png")
            extract_frame(args.video, last, last=True)
            result = {
                "video": args.video,
                "frame_mode": args.mode,
                "first_frame_purity": round(purity(first, args.bg_hex), 4),
                "end_frame_similarity": similarity(args.still, last),
            }

    print(json.dumps(result, ensure_ascii=False))
    if args.mode == "single-first":
        if result["start_frame_similarity"] < 0.90:
            print("  ! 首帧与确认首帧相似度偏低(<0.90)，请目测身份与构图", file=sys.stderr)
    else:
        if result["first_frame_purity"] < 0.97:
            print("  ! 首帧不够纯净(<0.97)，检查是否提前露出", file=sys.stderr)
        if result["end_frame_similarity"] < 0.90:
            print("  ! 尾帧还原偏低(<0.90)，对照确认静帧目测", file=sys.stderr)


if __name__ == "__main__":
    main()
