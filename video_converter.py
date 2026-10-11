#!/usr/bin/env python3
"""Convert video to broadly compatible H.264/AAC MP4 using imageio-ffmpeg.
The source file is never modified. Damaged or missing data may be unrecoverable.
"""
from __future__ import annotations
import subprocess
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".m4v", ".ts", ".mts", ".m2ts", ".wmv", ".mpg", ".mpeg", ".3gp"}


def choose_source() -> Path:
    while True:
        raw = input("Enter the full path to the downloaded video: ").strip().strip('"')
        path = Path(raw).expanduser()
        if not path.is_file():
            print("File not found. Check the path and try again.")
            continue
        if path.suffix.lower() not in VIDEO_EXTS:
            if input(f"Unusual extension {path.suffix!r}. Try it anyway? [y/N]: ").strip().lower() not in {"y", "yes"}:
                continue
        return path.resolve()


def main() -> int:
    print("VIDEO COMPATIBILITY CONVERTER")
    print("Creates an H.264/AAC MP4 and keeps your original file.\n")
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        print("Required Python library not installed. Install it with:")
        print("    py -m pip install imageio-ffmpeg")
        return 1
    except (RuntimeError, OSError) as exc:
        print(f"Could not locate the FFmpeg executable supplied by the package: {exc}")
        print("Try reinstalling with: py -m pip install --force-reinstall imageio-ffmpeg")
        return 1

    print("Step 1 — select the source video")
    source = choose_source()
    output = source.with_name(source.stem + "_compatible.mp4")
    print(f"\nStep 2 — output: {output}")
    if output.exists():
        if input("Output exists. Replace it? [y/N]: ").strip().lower() not in {"y", "yes"}:
            raw = input("Enter a different .mp4 output path, or press Enter to cancel: ").strip().strip('"')
            if not raw:
                print("Cancelled; original file is unchanged.")
                return 0
            output = Path(raw).expanduser().resolve()
            if output.suffix.lower() != ".mp4" or output.exists():
                print("Output must be a new filename ending in .mp4. Cancelled.")
                return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    print("\nStep 3 — converting; this may take several minutes...")
    command = [ffmpeg, "-hide_banner", "-y", "-fflags", "+genpts+discardcorrupt", "-err_detect", "ignore_err",
               "-i", str(source), "-map", "0:v:0", "-map", "0:a:0?", "-sn", "-dn",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output)]
    try:
        result = subprocess.run(command, check=False)
    except OSError as exc:
        print(f"Could not start the FFmpeg executable provided by imageio-ffmpeg: {exc}")
        return 2

    if result.returncode != 0 or not output.exists() or output.stat().st_size == 0:
        print("Conversion failed. The original is untouched. The source may be damaged, incomplete, or unsupported.")
        if output.exists() and output.stat().st_size == 0:
            output.unlink()
        return result.returncode or 2
    print(f"\nFinished. Open this file in VLC:\n{output}")
    print("Conversion can fix codec/container compatibility, but cannot recreate missing video data.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        raise SystemExit(130)
