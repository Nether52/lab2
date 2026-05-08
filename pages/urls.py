from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<int:category_id>/", views.category_detail, name="category_detail"),
    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
]