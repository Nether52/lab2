from django.core.management.base import BaseCommand

from pages.models import VideoFormat


class Command(BaseCommand):
    help = "Create or update default downloader formats."

    def handle(self, *args, **options):
        formats = [
            {
                "name": "MP3",
                "display_name": "MP3 Audio",
                "extension": "mp3",
                "quality": "audio",
                "only_audio": True,
                "needs_ffmpeg": True,
                "ytdlp_format": "bestaudio/best",
            },
            {
                "name": "MP3 HD",
                "display_name": "MP3 HD Audio",
                "extension": "mp3",
                "quality": "high audio",
                "only_audio": True,
                "needs_ffmpeg": True,
                "ytdlp_format": "bestaudio/best",
            },
            {
                "name": "M4A",
                "display_name": "M4A Audio",
                "extension": "m4a",
                "quality": "audio",
                "only_audio": True,
                "needs_ffmpeg": False,
                "ytdlp_format": "bestaudio[ext=m4a]/bestaudio/best",
            },
            {
                "name": "MP4",
                "display_name": "MP4 Video",
                "extension": "mp4",
                "quality": "720p",
                "only_audio": False,
                "needs_ffmpeg": False,
                "ytdlp_format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]/best",
            },
            {
                "name": "MP4 HD",
                "display_name": "MP4 HD Video",
                "extension": "mp4",
                "quality": "1080p",
                "only_audio": False,
                "needs_ffmpeg": False,
                "ytdlp_format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]/best",
            },
            {
                "name": "MP4 2K",
                "display_name": "MP4 2K Video",
                "extension": "mp4",
                "quality": "1440p",
                "only_audio": False,
                "needs_ffmpeg": False,
                "ytdlp_format": "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best[height<=1440][ext=mp4]/best[height<=1440]/best",
            },
            {
                "name": "WAV",
                "display_name": "WAV Audio",
                "extension": "wav",
                "quality": "audio",
                "only_audio": True,
                "needs_ffmpeg": True,
                "ytdlp_format": "bestaudio/best",
            },
            {
                "name": "WEBM",
                "display_name": "WEBM Video",
                "extension": "webm",
                "quality": "best",
                "only_audio": False,
                "needs_ffmpeg": False,
                "ytdlp_format": "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best",
            },
            {
                "name": "3GP",
                "display_name": "3GP Mobile Video",
                "extension": "3gp",
                "quality": "low",
                "only_audio": False,
                "needs_ffmpeg": False,
                "ytdlp_format": "best[ext=3gp]/worst",
            },
        ]

        created_count = 0
        updated_count = 0

        for format_data in formats:
            _, created = VideoFormat.objects.update_or_create(
                name=format_data["name"],
                defaults=format_data,
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Formats seeded. Created: {created_count}. Updated: {updated_count}."
            )
        )
