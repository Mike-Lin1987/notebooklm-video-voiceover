#!/usr/bin/env python3
"""Inspect, stream-copy mux, and verify prepared H.264 MP4 + AAC media."""

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys


def run(argv):
    result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if result.returncode:
        raise ValueError(f"工具失敗 ({result.returncode}): {result.stderr.strip()[-700:]}")
    return result


def nonempty(path):
    p = Path(path).resolve()
    if not p.is_file() or p.stat().st_size == 0:
        raise ValueError(f"檔案不存在或為空：{p}")
    return p


def metadata(path, ffprobe):
    p = nonempty(path)
    data = json.loads(run([ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(p)]).stdout)
    try:
        duration = float(data["format"]["duration"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"缺少有效媒體時長：{p}") from exc
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f"媒體時長無效：{p}")
    streams = data.get("streams", [])
    if not streams:
        raise ValueError(f"沒有媒體 stream：{p}")
    return {"path": str(p), "bytes": p.stat().st_size, "duration": duration,
            "format": data["format"].get("format_name"),
            "streams": [{"index": s.get("index"), "type": s.get("codec_type"),
                         "codec": s.get("codec_name"), "duration": s.get("duration"),
                         "start_time": s.get("start_time")}
                        for s in streams]}


def first(meta, kind):
    for s in meta["streams"]:
        if s["type"] == kind:
            return s
    raise ValueError(f"{meta['path']} 缺少 {kind} stream")


def duration_of(stream, meta):
    value = stream.get("duration")
    try:
        duration = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{meta['path']} 的 {stream['type']} stream 缺少有效時長") from exc
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f"{meta['path']} 的 {stream['type']} stream 時長無效")
    return duration


def start_of(stream, meta):
    try:
        start = float(stream.get("start_time"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{meta['path']} 的 {stream['type']} stream 缺少有效起點") from exc
    if not math.isfinite(start) or abs(start) > 0.005:
        raise ValueError(f"{meta['path']} 的 {stream['type']} stream 非近零起點；需先處理時間軸")
    return start


def compressed_audio_hash(path, ffmpeg):
    # FFmpeg hash muxer sees compressed AAC packets because -c:a copy is explicit.
    result = run([ffmpeg, "-v", "error", "-i", str(path), "-map", "0:a:0",
                  "-c:a", "copy", "-f", "hash", "-hash", "SHA256", "-"])
    value = result.stdout.strip()
    if not value.startswith("SHA256=") or len(value) != 71:
        raise ValueError("無法取得壓縮音軌 SHA256")
    return value.partition("=")[2].lower()


def prepared(video, audio, ffprobe):
    vm, am = metadata(video, ffprobe), metadata(audio, ffprobe)
    vs, aus = first(vm, "video"), first(am, "audio")
    if Path(video).suffix.lower() != ".mp4" or vs["codec"] != "h264":
        raise ValueError("僅支援已準備好的 H.264 MP4 影像；請另行準備格式")
    if aus["codec"] != "aac":
        raise ValueError("僅支援可 stream-copy 至 MP4 的 AAC 原聲；請另行準備格式")
    vd, ad = duration_of(vs, vm), duration_of(aus, am)
    start_of(vs, vm)
    start_of(aus, am)
    if vd + 0.005 < ad:
        raise ValueError(f"原聲 {ad:.3f}s 長於影像 {vd:.3f}s；請先重排或重錄畫面")
    return vm, am


def mux(args):
    video, audio = nonempty(args.video), nonempty(args.audio)
    output = Path(args.output).resolve()
    if output == video or output == audio:
        raise ValueError("輸入與輸出不可為同一路徑")
    if output.exists():
        raise ValueError(f"拒絕覆寫既有檔案：{output}")
    if output.suffix.lower() != ".mp4" or not output.parent.is_dir():
        raise ValueError("輸出需為既有目錄中的 .mp4 檔")
    prepared(video, audio, args.ffprobe)
    run([args.ffmpeg, "-v", "error", "-xerror", "-n", "-i", str(video),
         "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
         "-c:a", "copy", "-movflags", "+faststart", str(output)])
    result = metadata(output, args.ffprobe)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def verify(args):
    source, output = nonempty(args.audio), nonempty(args.output)
    sm, om = metadata(source, args.ffprobe), metadata(output, args.ffprobe)
    sa, oa = first(sm, "audio"), first(om, "audio")
    ov = first(om, "video")
    sd, od, vd = duration_of(sa, sm), duration_of(oa, om), duration_of(ov, om)
    start_of(sa, sm)
    start_of(oa, om)
    start_of(ov, om)
    if sa["codec"] != "aac" or oa["codec"] != "aac" or ov["codec"] != "h264":
        raise ValueError("成品需有 H.264 影像及 AAC 原聲")
    if abs(sd - od) > 0.005 or vd + 0.005 < od:
        raise ValueError("音訊時長不符或影像不足")
    sh = compressed_audio_hash(source, args.ffmpeg)
    oh = compressed_audio_hash(output, args.ffmpeg)
    if sh != oh:
        raise ValueError("來源與成品壓縮音軌 SHA256 不相同")
    run([args.ffmpeg, "-v", "error", "-xerror", "-i", str(output), "-f", "null", os.devnull])
    print(json.dumps({"output": str(output), "audio_stream_sha256": oh,
                      "audio_duration": od, "video_duration": vd,
                      "full_decode": "passed", "human_listening": "not_assessed"}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="顯示媒體 metadata")
    inspect.add_argument("input")
    inspect.add_argument("--ffprobe", default="ffprobe")
    m = sub.add_parser("mux", help="將已準備的 H.264 MP4 與 AAC 原聲 stream-copy 合成")
    m.add_argument("video")
    m.add_argument("audio")
    m.add_argument("output")
    m.add_argument("--ffmpeg", default="ffmpeg")
    m.add_argument("--ffprobe", default="ffprobe")
    v = sub.add_parser("verify", help="核對壓縮音軌 hash 並完整解碼成品")
    v.add_argument("audio")
    v.add_argument("output")
    v.add_argument("--ffmpeg", default="ffmpeg")
    v.add_argument("--ffprobe", default="ffprobe")
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            print(json.dumps(metadata(args.input, args.ffprobe), ensure_ascii=False, indent=2))
        elif args.command == "mux":
            mux(args)
        else:
            verify(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"錯誤：{exc}\n")


if __name__ == "__main__":
    main()
