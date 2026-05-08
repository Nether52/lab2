from django.contrib import admin
from .models import VideoCategory, VideoFormat, DownloadRequest


@admin.register(VideoCategory)
class VideoCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("created_at",)


@admin.register(VideoFormat)
class VideoFormatAdmin(admin.ModelAdmin):
    list_display = ("name", "extension", "quality", "only_audio", "created_at", "updated_at")
    search_fields = ("name", "extension", "quality")
    list_filter = ("extension", "only_audio", "created_at")


@admin.register(DownloadRequest)
class DownloadRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "format", "status", "created_at", "updated_at")
    search_fields = ("title", "youtube_url")
    list_filter = ("category", "format", "status", "created_at")
