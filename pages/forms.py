from django import forms
from .models import DownloadRequest, Subscriber, Purchase, VideoRating


class DownloadRequestForm(forms.ModelForm):
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
                "class": "form-control"
            }),
        }


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