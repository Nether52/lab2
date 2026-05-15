from pathlib import Path

from django.db.models import Avg
from django.http import FileResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .forms import (
    DownloadRequestForm,
    SubscriberForm,
    PurchaseForm,
    VideoRatingForm,
    YouTubeSearchForm,
)
from .models import VideoCategory, VideoFormat, DownloadRequest
from .services import (
    download_youtube_file,
    get_video_thumbnail,
    safe_filename,
    search_youtube_videos,
)


def get_download_filename(request_item, file_path):
    filename = safe_filename(request_item.title)
    extension = file_path.suffix.lstrip(".")

    if not extension and request_item.format:
        extension = request_item.format.extension

    if extension:
        return f"{filename}.{extension.lower()}"

    return filename


def get_cart(request):
    return request.session.get("download_cart", [])


def get_base_context(request):
    categories = VideoCategory.objects.all()
    cart = get_cart(request)

    return {
        "nav_categories": categories,
        "cart_count": len(cart),
    }


def get_converter_formats():
    download_form = DownloadRequestForm()
    return download_form.fields["format"].queryset


def get_search_payload(results):
    return {
        "results": results,
        "formats": [
            {
                "id": video_format.id,
                "label": str(video_format),
            }
            for video_format in get_converter_formats()
        ],
        "categories": [
            {
                "id": category.id,
                "name": category.name,
            }
            for category in VideoCategory.objects.all()
        ],
    }


def home(request):
    categories = VideoCategory.objects.all()

    download_requests = DownloadRequest.objects.select_related(
        "category", "format"
    ).order_by("-created_at")[:6]

    download_form = DownloadRequestForm()
    formats = get_converter_formats()
    search_form = YouTubeSearchForm()
    subscriber_form = SubscriberForm()
    search_results = []
    search_error = ""
    subscribed_success = False

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "download":
            download_form = DownloadRequestForm(request.POST)

            if download_form.is_valid():
                download_request = download_form.save(commit=False)
                download_request.image_url = get_video_thumbnail(download_request.youtube_url)
                download_request.status = "new"
                download_request.save()

                return redirect("download_request_detail", request_id=download_request.id)

        elif form_type == "search":
            search_form = YouTubeSearchForm(request.POST)

            if search_form.is_valid():
                try:
                    search_results = search_youtube_videos(search_form.cleaned_data["query"])
                except Exception as error:
                    search_error = str(error)

        elif form_type == "subscribe":
            subscriber_form = SubscriberForm(request.POST)

            if subscriber_form.is_valid():
                subscriber_form.save()
                subscribed_success = True
                subscriber_form = SubscriberForm()

    context = get_base_context(request)
    context.update({
        "page_title": "YouTube Video Downloader",
        "hero_title": "Download YouTube videos by copied link",
        "hero_text": "Paste a YouTube link, choose a category and format, and create your download request.",
        "categories": categories,
        "formats": formats,
        "download_requests": download_requests,
        "download_form": download_form,
        "search_form": search_form,
        "search_results": search_results,
        "search_error": search_error,
        "subscriber_form": subscriber_form,
        "subscribed_success": subscribed_success,
    })

    return render(request, "pages/home.html", context)


@require_POST
def youtube_search_view(request):
    search_form = YouTubeSearchForm(request.POST)

    if not search_form.is_valid():
        return JsonResponse({
            "ok": False,
            "error": "Enter a video title to search.",
        }, status=400)

    try:
        search_results = search_youtube_videos(search_form.cleaned_data["query"])
    except Exception as error:
        return JsonResponse({
            "ok": False,
            "error": str(error),
        }, status=400)

    payload = get_search_payload(search_results)
    payload["ok"] = True

    return JsonResponse(payload)


def category_detail(request, category_id):
    category = get_object_or_404(VideoCategory, id=category_id)

    download_requests = DownloadRequest.objects.filter(
        category=category
    ).select_related("category", "format").order_by("-created_at")

    context = get_base_context(request)
    context.update({
        "page_title": category.name,
        "category": category,
        "download_requests": download_requests,
    })

    return render(request, "pages/category_detail.html", context)


def download_request_detail(request, request_id):
    request_item = get_object_or_404(
        DownloadRequest.objects.select_related("category", "format"),
        id=request_id
    )

    purchase_form = PurchaseForm()
    rating_form = VideoRatingForm()

    purchase_success = False
    rating_success = False

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "purchase":
            purchase_form = PurchaseForm(request.POST)

            if purchase_form.is_valid():
                purchase = purchase_form.save(commit=False)
                purchase.download_request = request_item
                purchase.status = "created"
                purchase.save()

                purchase_success = True
                purchase_form = PurchaseForm()

        elif form_type == "rating":
            rating_form = VideoRatingForm(request.POST)

            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.download_request = request_item
                rating.save()

                rating_success = True
                rating_form = VideoRatingForm()

        elif form_type == "prepare_download":
            download_youtube_file(request_item)
            return redirect("download_request_detail", request_id=request_item.id)

    average_rating = request_item.ratings.aggregate(
        average=Avg("score")
    )["average"]

    ratings_count = request_item.ratings.count()
    latest_ratings = request_item.ratings.order_by("-created_at")[:5]

    context = get_base_context(request)
    context.update({
        "page_title": request_item.title,
        "request_item": request_item,
        "purchase_form": purchase_form,
        "rating_form": rating_form,
        "purchase_success": purchase_success,
        "rating_success": rating_success,
        "average_rating": average_rating,
        "ratings_count": ratings_count,
        "latest_ratings": latest_ratings,
    })

    return render(request, "pages/download_request_detail.html", context)


@require_POST
def prepare_download_view(request, request_id):
    request_item = get_object_or_404(
        DownloadRequest.objects.select_related("category", "format"),
        id=request_id
    )

    download_youtube_file(request_item)
    return redirect("download_request_detail", request_id=request_item.id)


def download_file_view(request, request_id):
    request_item = get_object_or_404(DownloadRequest, id=request_id)

    if request_item.status == "completed" and request_item.downloaded_file:
        file_path = Path(request_item.downloaded_file.path)

        if file_path.exists():
            return FileResponse(
                file_path.open("rb"),
                as_attachment=True,
                filename=get_download_filename(request_item, file_path),
            )

    request_item.status = "failed"
    request_item.error_message = "The prepared file was not found. Please prepare the download again."
    request_item.save(update_fields=["status", "error_message", "updated_at"])

    return redirect("download_request_detail", request_id=request_item.id)


def add_to_cart(request, request_id):
    get_object_or_404(DownloadRequest, id=request_id)

    cart = get_cart(request)

    if request_id not in cart:
        cart.append(request_id)

    request.session["download_cart"] = cart
    request.session.modified = True

    return redirect("cart_detail")


def remove_from_cart(request, request_id):
    cart = get_cart(request)

    if request_id in cart:
        cart.remove(request_id)

    request.session["download_cart"] = cart
    request.session.modified = True

    return redirect("cart_detail")


def clear_cart(request):
    request.session["download_cart"] = []
    request.session.modified = True

    return redirect("cart_detail")


def cart_detail(request):
    cart = get_cart(request)

    cart_items = DownloadRequest.objects.filter(
        id__in=cart
    ).select_related("category", "format")

    total_price = sum(item.price for item in cart_items)

    context = get_base_context(request)
    context.update({
        "page_title": "Download cart",
        "cart_items": cart_items,
        "total_price": total_price,
    })

    return render(request, "pages/cart_detail.html", context)


def about(request):
    context = get_base_context(request)
    context.update({
        "page_title": "About",
        "title": "About YT Downloader",
        "text": (
            "YT Downloader is an educational Django project that works like a simple video "
            "converter: paste a YouTube link, choose a format, prepare the file, and download it."
        ),
        "details": [
            {
                "title": "What it can do",
                "text": "The site creates download requests, shows thumbnails, saves prepared files, and keeps request status visible to the user.",
            },
            {
                "title": "Safe usage",
                "text": "Users must confirm that they have the right to download the selected video before creating a request.",
            },
            {
                "title": "Project features",
                "text": "The project also includes categories, cart, purchases, ratings, subscriptions, authentication, and profile pages.",
            },
        ],
    })

    return render(request, "pages/page.html", context)


def contacts(request):
    context = get_base_context(request)
    context.update({
        "page_title": "Contacts",
        "title": "Contacts",
        "text": "Example contact details for the project owner or support team.",
        "contacts": [
            {
                "label": "Email",
                "value": "support@ytdownloader.local",
            },
            {
                "label": "Phone",
                "value": "+380 67 123 45 67",
            },
            {
                "label": "Address",
                "value": "Kyiv, Ukraine",
            },
            {
                "label": "Working hours",
                "value": "Monday - Friday, 09:00 - 18:00",
            },
        ],
    })

    return render(request, "pages/page.html", context)
