from django.urls import path
from cafe.views import (
    Index,
    ShiftListView,
    ShiftCreateView,
)

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("shifts/", ShiftListView.as_view(), name="shift-list-view"),
    path("shifts/create/", ShiftCreateView.as_view(), name="shift-create"),
]

app_name = "cafe"
