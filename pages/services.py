import re
import shutil
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.utils import timezone


def get_video_thumbnail(url):
    parsed_url = urlparse(url)
    hostname = (parsed_url.hostname or "").lower()
    video_id = None

    if hostname in ("www.youtube.com", "youtube.com", "m.youtube.com", "music.youtube.com"):
        if parsed_url.path == "/watch":
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
        elif parsed_url.path.startswith("/shorts/"):
            video_id = parsed_url.path.split("/shorts/", 1)[1].split("/", 1)[0]
    elif hostname == "youtu.be":
        video_id = parsed_url.path.strip("/").split("/", 1)[0]

    if video_id:
        return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    return ""


def safe_filename(value):
    value = str(value or "").strip()
    value = re.sub(r'[\\/:*?"<>|]+', "", value)
    value = re.sub(r"[\x00-\x1f]+", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" ._") or "download"


def format_duration(seconds):
    if not seconds:
        return ""

    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return ""

    minutes, remaining_seconds = divmod(seconds, 60)
    hours, remaining_minutes = divmod(minutes, 60)

    if hours:
        return f"{hours}:{remaining_minutes:02d}:{remaining_seconds:02d}"

    return f"{remaining_minutes}:{remaining_seconds:02d}"


def clean_error_message(error):
    message = str(error)
    message = re.sub(r"\x1b\[[0-9;]*m", "", message)
    message = re.sub(r"\s+", " ", message).strip()
    lower_message = message.lower()

    if "confirm your age" in lower_message or "inappropriate for some users" in lower_message:
        return (
            "This video requires age confirmation or sign-in. "
            "Please choose a public video that does not require age verification."
        )

    if "private video" in lower_message or "members-only" in lower_message:
        return (
            "This video is private, members-only, or otherwise restricted. "
            "Please choose a public video you have the right to download."
        )

    if "sign in" in lower_message and "youtube" in lower_message:
        return (
            "YouTube requires sign-in for this video. "
            "This site can only prepare public videos that do not require authentication."
        )

    return message


def search_youtube_videos(query, max_results=6):
    try:
        import yt_dlp
    except ImportError as error:
        raise RuntimeError(
            "yt-dlp is not installed. Install dependencies with pip install -r requirements.txt."
        ) from error

    clean_query = str(query or "").strip()

    if not clean_query:
        return []

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "noplaylist": True,
        "color": "never",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{max_results}:{clean_query}", download=False)
    except Exception as error:
        raise RuntimeError(
            "Could not search YouTube right now. Check your internet connection and try again."
        ) from error

    results = []

    for entry in info.get("entries", []):
        if not entry:
            continue

        video_id = entry.get("id")
        url = entry.get("url") or ""

        if url.startswith("http://") or url.startswith("https://"):
            video_url = url
        elif video_id:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
        else:
            continue

        thumbnail = entry.get("thumbnail") or get_video_thumbnail(video_url)

        title = entry.get("title") or "Untitled video"

        results.append({
            "title": title[:200],
            "youtube_url": video_url,
            "thumbnail": thumbnail,
            "channel": entry.get("uploader") or entry.get("channel") or "",
            "duration": format_duration(entry.get("duration")),
        })

    return results


def _get_ytdlp_format(video_format):
    if video_format and video_format.ytdlp_format:
        return video_format.ytdlp_format

    extension = (video_format.extension if video_format else "").lower()
    only_audio = bool(video_format.only_audio) if video_format else False

    if only_audio and extension == "mp3":
        return "bestaudio/best"
    if extension == "m4a":
        return "bestaudio[ext=m4a]/bestaudio/best"
    if extension == "wav":
        return "bestaudio/best"
    if extension == "mp4":
        return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    if extension == "webm":
        return "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best"
    if extension == "3gp":
        return "best[ext=3gp]/worst"

    return "best"


def _get_postprocessors(video_format):
    if not video_format:
        return []

    extension = video_format.extension.lower()

    if video_format.only_audio and extension == "mp3":
        preferred_quality = "320" if "hd" in video_format.name.lower() else "192"
        return [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": preferred_quality,
        }]

    if extension == "wav":
        return [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }]

    return []


def _friendly_error(error):
    message = clean_error_message(error)

    if "ffmpeg" in message.lower():
        return (
            "FFmpeg is required for this format or conversion. "
            "Install ffmpeg and make sure it is available in PATH, then try again."
        )

    return message


def _mark_failed(download_request, error):
    download_request.status = "failed"
    download_request.error_message = _friendly_error(error)
    download_request.save(update_fields=["status", "error_message", "updated_at"])


def download_youtube_file(download_request):
    download_request.status = "processing"
    download_request.error_message = ""
    download_request.save(update_fields=["status", "error_message", "updated_at"])

    try:
        try:
            import yt_dlp
        except ImportError as error:
            raise RuntimeError(
                "yt-dlp is not installed. Install dependencies with pip install -r requirements.txt."
            ) from error

        video_format = download_request.format

        if video_format and video_format.needs_ffmpeg and not shutil.which("ffmpeg"):
            raise RuntimeError(
                "FFmpeg is required for this format. Install ffmpeg and make sure it is available in PATH."
            )

        request_dir = (
            Path(settings.MEDIA_ROOT)
            / "downloads"
            / f"request_{download_request.id}"
        )
        request_dir.mkdir(parents=True, exist_ok=True)

        output_template = str(
            request_dir
            / f"request_{download_request.id}_%(id)s.%(ext)s"
        )

        ydl_opts = {
            "format": _get_ytdlp_format(video_format),
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "restrictfilenames": True,
            "color": "never",
            "postprocessors": _get_postprocessors(video_format),
        }

        if video_format and video_format.extension.lower() in ("mp4", "webm"):
            ydl_opts["merge_output_format"] = video_format.extension.lower()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([download_request.youtube_url])

        created_files = [
            file_path
            for file_path in request_dir.rglob("*")
            if file_path.is_file()
            and not file_path.name.endswith(".part")
            and file_path.suffix.lower() not in (".part", ".tmp", ".ytdl")
        ]

        if not created_files:
            raise RuntimeError("The file was not created. Please try another format.")

        extension = (video_format.extension if video_format else "").lower()
        preferred_files = [
            file_path
            for file_path in created_files
            if extension and file_path.suffix.lower() == f".{extension}"
        ]

        final_file = max(
            preferred_files or created_files,
            key=lambda file_path: file_path.stat().st_mtime,
        )

        relative_path = Path("downloads") / f"request_{download_request.id}" / final_file.name
        download_request.downloaded_file.name = str(relative_path).replace("\\", "/")
        download_request.status = "completed"
        download_request.error_message = ""
        download_request.downloaded_at = timezone.now()
        download_request.save(update_fields=[
            "downloaded_file",
            "status",
            "error_message",
            "downloaded_at",
            "updated_at",
        ])
    except Exception as error:
        _mark_failed(download_request, error)

    return download_request
