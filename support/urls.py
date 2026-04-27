from django.urls import path
from . import views

urlpatterns = [
    path("", views.support_list, name="support_list"),
    path("<int:pk>/", views.support_detail, name="support_detail"),
    path("create/", views.create_ticket, name="create_ticket"),
]