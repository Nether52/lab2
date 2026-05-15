from django import forms
from .models import DownloadRequest, Subscriber, Purchase, VideoRating, VideoFormat


DEFAULT_FORMAT_NAMES = (
    "MP3",
    "MP3 HD",
    "M4A",
    "MP4",
    "MP4 HD",
    "MP4 2K",
    "WAV",
    "3GP",
    "WEBM",
)


class DownloadRequestForm(forms.ModelForm):
    rights_confirmed = forms.BooleanField(
        required=True,
        label="I confirm that I have the right to download this video",
        widget=forms.CheckboxInput(attrs={
            "class": "rights-input"
        })
    )

    class Meta:
        model = DownloadRequest
        fields = ("title", "youtube_url", "category", "format")

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Video title"
            }),
            "youtube_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "Paste YouTube link here"
            }),
            "category": forms.Select(attrs={
                "class": "form-control"
            }),
            "format": forms.Select(attrs={
                "class": "form-control format-select"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].required = False
        self.fields["category"].empty_label = "Choose category"
        self.fields["format"].empty_label = "Choose format"

        default_formats = VideoFormat.objects.filter(name__in=DEFAULT_FORMAT_NAMES)

        if default_formats.exists():
            self.fields["format"].queryset = default_formats

    def clean_youtube_url(self):
        youtube_url = self.cleaned_data["youtube_url"]
        allowed_hosts = (
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "music.youtube.com",
            "youtu.be",
        )

        from urllib.parse import urlparse

        parsed_url = urlparse(youtube_url)
        hostname = (parsed_url.hostname or "").lower()

        if hostname not in allowed_hosts:
            raise forms.ValidationError("Please enter a valid YouTube URL.")

        return youtube_url


class YouTubeSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        label="Search YouTube",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Search video by title"
        })
    )


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ("name", "email")

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Your name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Your email"
            }),
        }


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ("customer_name", "customer_email")

        widgets = {
            "customer_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Your name"
            }),
            "customer_email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Your email"
            }),
        }


class VideoRatingForm(forms.ModelForm):
    class Meta:
        model = VideoRating
        fields = ("name", "score", "comment")

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Your name"
            }),
            "score": forms.Select(attrs={
                "class": "form-control"
            }),
            "comment": forms.Textarea(attrs={
                "class": "form-control textarea",
                "placeholder": "Write your comment",
                "rows": 4
            }),
        }
