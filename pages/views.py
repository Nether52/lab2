from urllib.parse import urlparse, parse_qs

from django.db.models import Avg
from django.shortcuts import render, get_object_or_404, redirect

from .forms import (
    DownloadRequestForm,
    SubscriberForm,
    PurchaseForm,
    VideoRatingForm,
)
from .models import VideoCategory, VideoFormat, DownloadRequest


def get_youtube_thumbnail(youtube_url):
    parsed_url = urlparse(youtube_url)
    hostname = parsed_url.hostname
    video_id = None

    if hostname in ["www.youtube.com", "youtube.com", "m.youtube.com"]:
        if parsed_url.path == "/watch":
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
        elif parsed_url.path.startswith("/shorts/"):
            video_id = parsed_url.path.split("/shorts/")[1].split("/")[0]

    elif hostname == "youtu.be":
        video_id = parsed_url.path.strip("/")

    if video_id:
        return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    return ""


def get_cart(request):
    return request.session.get("download_cart", [])


def get_base_context(request):
    categories = VideoCategory.objects.all()
    cart = get_cart(request)

    return {
        "nav_categories": categories,
        "cart_count": len(cart),
    }


def home(request):
    categories = VideoCategory.objects.all()
    formats = VideoFormat.objects.all()

    download_requests = DownloadRequest.objects.select_related(
        "category", "format"
    ).order_by("-created_at")[:6]

    download_form = DownloadRequestForm()
    subscriber_form = SubscriberForm()
    subscribed_success = False

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "download":
            download_form = DownloadRequestForm(request.POST)

            if download_form.is_valid():
                download_request = download_form.save(commit=False)
                download_request.image_url = get_youtube_thumbnail(download_request.youtube_url)
                download_request.status = "new"
                download_request.save()

                return redirect("download_request_detail", request_id=download_request.id)

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
        "subscriber_form": subscriber_form,
        "subscribed_success": subscribed_success,
    })

    return render(request, "pages/home.html", context)


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
        "title": "About this project",
        "text": "This website is a Django project that represents a YouTube video downloader by copied link.",
    })

    return render(request, "pages/page.html", context)


def contacts(request):
    context = get_base_context(request)
    context.update({
        "page_title": "Contacts",
        "title": "Contacts",
        "text": "Here users can find contact information for the website owner.",
    })

    return render(request, "pages/page.html", context)