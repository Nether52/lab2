from django.db import models


class VideoCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Video category"
        verbose_name_plural = "Video categories"

    def __str__(self):
        return self.name


class VideoFormat(models.Model):
    name = models.CharField(max_length=100)
    extension = models.CharField(max_length=10)
    quality = models.CharField(max_length=50)
    only_audio = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Video format"
        verbose_name_plural = "Video formats"

    def __str__(self):
        return f"{self.name} ({self.quality})"


class DownloadRequest(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    title = models.CharField(max_length=200)
    youtube_url = models.URLField()
    category = models.ForeignKey(
        VideoCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="download_requests"
    )
    format = models.ForeignKey(
        VideoFormat,
        on_delete=models.SET_NULL,
        null=True,
        related_name="download_requests"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Download request"
        verbose_name_plural = "Download requests"

    def __str__(self):
        return self.title