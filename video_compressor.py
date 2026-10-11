#!/usr/bin/env python3
"""Strictly lossless video recompression using imageio-ffmpeg's bundled FFmpeg.

Lossless recompression preserves decoded video pixels and copies audio as-is.
It cannot guarantee a smaller file; already-compressed videos often grow.
"""
from __future__ import annotations
import subprocess
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".m4v", ".ts", ".mts", ".m2ts", ".wmv", ".mpg", ".mpeg", ".3gp"}


def get_source() -> Path:
    while True:
        raw = input("Enter the full path to the video: ").strip().strip('"')
        source = Path(raw).expanduser()
        if not source.is_file():
            print("File not found. Check the path and try again.")
            continue
        if source.suffix.lower() not in VIDEO_EXTS:
            if input(f"Unusual extension {source.suffix!r}. Try it anyway? [y/N]: ").strip().lower() not in {"y", "yes"}:
                continue
        return source.resolve()


def main() -> int:
    print("LOSSLESS VIDEO COMPRESSOR")
    print("Keeps decoded video quality unchanged and copies the first audio track unchanged.")
    print("The output may be larger than the input if it is already compressed.\n")
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        print("Install the required Python package with: py -m pip install imageio-ffmpeg")
        return 1
    except (RuntimeError, OSError) as exc:
        print(f"Could not get the FFmpeg executable from imageio-ffmpeg: {exc}")
        return 1

    source = get_source()
    output = source.with_name(source.stem + "_lossless.mp4")
    if output.exists():
        print(f"Output already exists: {output}")
        raw = input("Enter a new output path ending in .mp4, or press Enter to cancel: ").strip().strip('"')
        if not raw:
            print("Cancelled; source was not changed.")
            return 0
        output = Path(raw).expanduser().resolve()
        if output.suffix.lower() != ".mp4" or output.exists():
            print("Choose a new, unused filename ending in .mp4. Cancelled.")
            return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    print("\nCompressing in lossless mode. This can take a while...")
    args = [ffmpeg, "-hide_banner", "-y", "-i", str(source),
            "-map", "0:v:0", "-map", "0:a:0?", "-sn", "-dn",
            "-c:v", "libx264", "-qp", "0", "-pix_fmt", "+",
            "-c:a", "copy", "-movflags", "+faststart", str(output)]
    try:
        result = subprocess.run(args, check=False)
    except OSError as exc:
        print(f"Could not start FFmpeg: {exc}")
        return 2

    if result.returncode != 0 or not output.exists() or output.stat().st_size == 0:
        print("Compression failed. The original file is unchanged.")
        if output.exists() and output.stat().st_size == 0:
            output.unlink()
        print("The bundled FFmpeg may lack H.264 encoding support, or the input may be damaged/unsupported.")
        return result.returncode or 2

    old_size, new_size = source.stat().st_size, output.stat().st_size
    delta = old_size - new_size
    percent = delta / old_size * 100 if old_size else 0
    print(f"\nOutput: {output}")
    print(f"Original: {old_size / (1024 * 1024):.1f} MiB; output: {new_size / (1024 * 1024):.1f} MiB")
    if delta > 0:
        print(f"Saved {delta / (1024 * 1024):.1f} MiB ({percent:.1f}%).")
    else:
        print(f"Output is {abs(delta) / (1024 * 1024):.1f} MiB larger; this is common for already-compressed video.")
    print("The source file was kept. Lossless mode cannot promise a smaller output.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        raise SystemExit(130)

