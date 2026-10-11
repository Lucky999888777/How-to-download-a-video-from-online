#!/usr/bin/env python3
"""Interactive video downloader for media you are authorized to save.

Uses yt-dlp's site extractors to inspect a page and download supported media,
including many embedded players and HLS/DASH streams. It does not bypass DRM,
logins, paywalls, or other access restrictions.
"""
from __future__ import annotations

import sys
from pathlib import Path


def pause(message: str = "Press Enter to continue...") -> None:
    input(f"\n{message}")


def main() -> int:
    print("VIDEO PAGE CHECKER AND DOWNLOADER")
    print("Use only for videos you own or are authorized to download.")
    print("This tool cannot download DRM-protected content or bypass site restrictions.\n")

    try:
        import yt_dlp
    except ImportError:
        print("Step 1 — setup")
        print("The required package 'yt-dlp' is not installed.")
        print("Install it in this Python environment with:")
        print("    py -m pip install -U yt-dlp")
        return 1

    while True:
        url = input("Step 1 — paste the page address (URL): ").strip()
        if url.lower() in {"q", "quit", "exit"}:
            return 0
        if url.startswith(("https://", "http://")):
            break
        print("Please enter a complete address beginning with https:// or http://, or type q to quit.")

    print("\nStep 2 — checking the page for video sources...")
    print("This may find a direct video file or a supported embedded/streaming player.")
    inspect_opts = {"quiet": True, "no_warnings": False, "noplaylist": True}
    try:
        with yt_dlp.YoutubeDL(inspect_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:
        print(f"\nThe page could not be inspected: {exc}")
        print("The site may be unsupported, require a permitted sign-in, or block automated access.")
        print("This script will not attempt to bypass DRM or access controls.")
        return 2

    if not info:
        print("No video information was returned for this page.")
        return 2

    entries = info.get("entries")
    if entries:
        entries = [item for item in entries if item]
        if not entries:
            print("The page did not expose any video entries.")
            return 2
        if len(entries) > 1:
            print(f"Found a playlist with {len(entries)} entries. Downloading the page as a whole.")
        info = entries[0]

    title = info.get("title") or "Unknown title"
    extractor = info.get("extractor_key") or info.get("extractor") or "site extractor"
    formats = info.get("formats") or []
    print(f"Found: {title}")
    print(f"Detected by: {extractor}")
    if formats:
        kinds = sorted({(f.get("protocol") or "file") for f in formats})
        print(f"Available media formats/streams: {len(formats)} ({', '.join(kinds)})")
    else:
        print("A video entry was identified; the site did not list separate format choices.")

    print("\nStep 3 — choose where to save it.")
    default_dir = Path.home() / "Downloads"
    folder_text = input(f"Save folder [{default_dir}]: ").strip()
    folder = Path(folder_text).expanduser() if folder_text else default_dir
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"Could not create/access that folder: {exc}")
        return 2

    print("\nStep 4 — select download quality.")
    print("Enter a format ID to choose one listed by the site, or press Enter for best available quality.")
    print("To see format IDs first, type 'list'.")
    format_choice = input("Format ID [best]: ").strip()
    ydl_opts = {
        "outtmpl": str(folder / "%(title).180B [%(id)s].%(ext)s"),
        "noplaylist": True,
        "windowsfilenames": True,
        "continuedl": True,
        "format": "bestvideo*+bestaudio/best" if not format_choice else format_choice,
    }
    if format_choice.lower() == "list":
        print("\nAvailable formats:")
        with yt_dlp.YoutubeDL({"quiet": True, "listformats": True, "noplaylist": True}) as ydl:
            ydl.extract_info(url, download=False)
        format_choice = input("Enter a format ID, or press Enter for best: ").strip()
        ydl_opts["format"] = format_choice or "bestvideo*+bestaudio/best"

    print(f"\nStep 5 — downloading to: {folder.resolve()}")
    print("If audio and video need combining, yt-dlp may need ffmpeg installed.")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except KeyboardInterrupt:
        print("\nDownload stopped. A partial file may be resumable on the next run.")
        return 130
    except Exception as exc:
        print(f"\nDownload failed: {exc}")
        print("Some sites require browser cookies or an official download option. DRM-protected media cannot be handled by this tool.")
        return 2

    print(f"\nFinished. Check this folder: {folder.resolve()}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (EOFError, BrokenPipeError):
        print("\nInput ended.")
        raise SystemExit(1)
