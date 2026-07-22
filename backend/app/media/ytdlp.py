from __future__ import annotations

from pathlib import Path

import yt_dlp


def download_video(url: str, dest_dir: Path) -> Path:
    """Download a YouTube video (including ended-livestream VODs, which
    yt-dlp treats the same as any other video URL once the stream has
    ended) to dest_dir. Returns the path to the downloaded file.
    """
    outtmpl = str(dest_dir / "original.%(ext)s")
    opts = {
        "outtmpl": outtmpl,
        "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    downloaded = Path(filename)
    if downloaded.suffix != ".mp4":
        downloaded = downloaded.with_suffix(".mp4")
    if not downloaded.exists():
        # merge_output_format can change the container after prepare_filename
        # is computed; fall back to scanning dest_dir for the merged output.
        candidates = sorted(dest_dir.glob("original.*"))
        if not candidates:
            raise FileNotFoundError(f"yt-dlp did not produce an output file in {dest_dir}")
        downloaded = candidates[0]

    return downloaded
