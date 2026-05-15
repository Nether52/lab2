# YT Downloader

Educational Django project for preparing downloadable files from YouTube links.

## FFmpeg note

MP3, WAV, M4A and some video conversions may require FFmpeg. Install `ffmpeg`
and make sure it is available in your system `PATH`.

If FFmpeg is missing, the site catches the error and shows a clear message on
the download request page instead of returning a 500 error.
