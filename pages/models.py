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
    image_url = models.URLField(blank=True, default="")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

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


class Subscriber(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subscriber"
        verbose_name_plural = "Subscribers"

    def __str__(self):
        return self.email


class Purchase(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    download_request = models.ForeignKey(
        DownloadRequest,
        on_delete=models.CASCADE,
        related_name="purchases"
    )

    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Purchase"
        verbose_name_plural = "Purchases"

    def __str__(self):
        return f"{self.customer_name} - {self.download_request.title}"


class VideoRating(models.Model):
    SCORE_CHOICES = [
        (1, "1 - Very bad"),
        (2, "2 - Bad"),
        (3, "3 - Normal"),
        (4, "4 - Good"),
        (5, "5 - Excellent"),
    ]

    download_request = models.ForeignKey(
        DownloadRequest,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    name = models.CharField(max_length=100)
    score = models.IntegerField(choices=SCORE_CHOICES)
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Video rating"
        verbose_name_plural = "Video ratings"

    def __str__(self):
        return f"{self.download_request.title} - {self.score}"