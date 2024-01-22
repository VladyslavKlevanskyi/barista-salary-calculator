from django.urls import path
from cafe.views import (
    Index,
    ShiftListView,
    ShiftCreateView,
    ShiftUpdateView,
)

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("shifts/", ShiftListView.as_view(), name="shift-list-view"),
    path("shifts/create/", ShiftCreateView.as_view(), name="shift-create"),
    path("shifts/<int:pk>/update/", ShiftUpdateView.as_view(), name="shift-update"),
]

app_name = "cafe"
