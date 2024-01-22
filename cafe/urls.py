from django.urls import path
from cafe.views import (
    Index,
    ShiftListView,
    ShiftCreateView,
    ShiftUpdateView,
    ShiftDeleteView,
)

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("shifts/", ShiftListView.as_view(), name="shift-list-view"),
    path("shifts/create/", ShiftCreateView.as_view(), name="shift-create"),
    path("shifts/<int:pk>/update/", ShiftUpdateView.as_view(), name="shift-update"),
    path("shifts/<int:pk>/delete/", ShiftDeleteView.as_view(), name="shift-delete"),
]

app_name = "cafe"
