from django.urls import path
from cafe.views import (
    Index,
)

urlpatterns = [
    path("", Index.as_view(), name="index"),
]

app_name = "cafe"
