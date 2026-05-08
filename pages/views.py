from django.shortcuts import render, get_object_or_404
from .models import VideoCategory, VideoFormat, DownloadRequest


def home(request):
    categories = VideoCategory.objects.all()
    formats = VideoFormat.objects.all()
    download_requests = DownloadRequest.objects.select_related(
        "category", "format"
    ).order_by("-created_at")[:6]

    context = {
        "page_title": "YouTube Video Downloader",
        "hero_title": "Download YouTube videos by link",
        "hero_text": "Paste a YouTube link, choose a category and format, and prepare your video for downloading.",
        "nav_categories": categories,
        "categories": categories,
        "formats": formats,
        "download_requests": download_requests,
    }

    return render(request, "pages/home.html", context)


def category_detail(request, category_id):
    categories = VideoCategory.objects.all()
    category = get_object_or_404(VideoCategory, id=category_id)

    download_requests = DownloadRequest.objects.filter(
        category=category
    ).select_related("format").order_by("-created_at")

    context = {
        "page_title": category.name,
        "nav_categories": categories,
        "category": category,
        "download_requests": download_requests,
    }

    return render(request, "pages/category_detail.html", context)


def about(request):
    categories = VideoCategory.objects.all()

    context = {
        "page_title": "About",
        "title": "About this project",
        "text": "This website is a Django project that represents a YouTube video downloader by copied link.",
        "nav_categories": categories,
    }

    return render(request, "pages/page.html", context)


def contacts(request):
    categories = VideoCategory.objects.all()

    context = {
        "page_title": "Contacts",
        "title": "Contacts",
        "text": "Here users can find contact information for the website owner.",
        "nav_categories": categories,
    }

    return render(request, "pages/page.html", context)