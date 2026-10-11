# Video Downloader and Utilities

A small set of interactive Python command-line tools for downloading supported online videos and converting local video files.

## Included scripts

| Script | What it does |
|---|---|
| `video_downloader.py` | Inspects a web page with `yt-dlp` and downloads a supported video or stream. It prompts for a page URL, destination folder, and format. For playlist pages, it is configured to process a single video rather than the whole playlist. |
| `video_converter.py` | Converts a local video to an H.264/AAC MP4 intended for broad player compatibility. It writes a separate file ending in `_compatible.mp4` and keeps the source. The video conversion is lossy; it cannot restore missing or badly damaged data. |
| `video_compressor.py` | Re-encodes the video in lossless H.264 mode and copies the first audio track unchanged. It writes a separate file ending in `_lossless.mp4`. Lossless compression may make an already-compressed file larger. |

The conversion and compression scripts use `imageio-ffmpeg` to obtain FFmpeg from a Python package; a separate FFmpeg installation is not needed. Some package builds may not include the H.264 encoder required by these scripts.

## Requirements

- Python 3.10 or later is recommended.
- `yt-dlp` is needed for the downloader.
- `imageio-ffmpeg` is needed for the converter and compressor.
- Internet access is needed to install packages and download online videos.

Install the Python packages from PowerShell:

```powershell
py -m pip install --upgrade yt-dlp imageio-ffmpeg
```

## Run the tools

Open PowerShell in this folder and run the script you need:

```powershell
py video_downloader.py
py video_converter.py
py video_compressor.py
```

The downloader asks for a web page address and where to save the video. The converter and compressor ask for the full path to a local video. Their output is saved next to the source file by default. The original file is kept.

## Notes and limitations

- Website support depends on `yt-dlp` and the site. Not every player or stream can be downloaded.
- These scripts do not bypass DRM, paywalls, sign-in requirements, or other access restrictions. Use them only for media you own or are authorized to download.
- The compatibility converter changes the encoding and can reduce quality slightly. The compressor's lossless mode preserves decoded video quality but may not reduce file size.
- A successful conversion cannot guarantee playback if the source file is incomplete, severely damaged, or uses unsupported codecs.
- The downloader may need FFmpeg support to combine separate audio and video streams. If the bundled `imageio-ffmpeg` build cannot do this, the download may fail to merge.
