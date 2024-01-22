from django.urls import path
from cafe.views import (
    Index,
    ShiftListView,
)

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("shifts/", ShiftListView.as_view(), name="shift-list-view"),
]

app_name = "cafe"
