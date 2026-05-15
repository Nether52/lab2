from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("youtube-search/", views.youtube_search_view, name="youtube_search"),

    path("category/<int:category_id>/", views.category_detail, name="category_detail"),
    path("video/<int:request_id>/", views.download_request_detail, name="download_request_detail"),
    path("video/<int:request_id>/prepare-download/", views.prepare_download_view, name="prepare_download"),
    path("video/<int:request_id>/download-file/", views.download_file_view, name="download_file"),

    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:request_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:request_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),

    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
]
