from django.urls import path
from cafe.views import (
    Index,
    CafeListView,
    CafeDetailView,
    BaristaListView,
    BaristaDetailView,
    ShiftListView,
    ShiftCreateView,
    ShiftUpdateView,
    ShiftDeleteView,
    IncomeCreateView,
    IncomeUpdateView,
)

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("cafes/", CafeListView.as_view(), name="cafe-list-view"),
    path("cafes/<int:pk>/", CafeDetailView.as_view(), name="cafe-detail-view"),
    path("baristas/", BaristaListView.as_view(), name="barista-list-view"),
    path("baristas/<int:pk>/", BaristaDetailView.as_view(), name="barista-detail-view"),
    path("shifts/", ShiftListView.as_view(), name="shift-list-view"),
    path("shifts/create/", ShiftCreateView.as_view(), name="shift-create"),
    path("shifts/<int:pk>/update/", ShiftUpdateView.as_view(), name="shift-update"),
    path("shifts/<int:pk>/delete/", ShiftDeleteView.as_view(), name="shift-delete"),
    path("incomes/create/", IncomeCreateView.as_view(), name="income-create"),
    path("incomes/<int:pk>/update/", IncomeUpdateView.as_view(), name="income-update"),
]

app_name = "cafe"
