from django import forms
from .models import DownloadRequest, Subscriber, Purchase


class DownloadRequestForm(forms.ModelForm):
    class Meta:
        model = DownloadRequest
        fields = ("title", "youtube_url", "category", "format")

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Video title, for example: F1 Highlights"
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