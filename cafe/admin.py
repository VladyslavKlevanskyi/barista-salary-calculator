from django.contrib import admin
from cafe.models import Cafe, Shift, Rate, Barista, Income


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "cafe", "income", "barista")

    @staticmethod
    def barista(income):
        return Shift.objects.get(date=income.date, cafe=income.cafe.id).barista


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_filter = ["barista", "cafe"]
    list_display = (
        "id",
        "barista",
        "cafe",
        "min_wage",
        "percent",
        "additive",
    )


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date",
        "cafe",
        "barista",
        "salary",
    )


@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )


@admin.register(Barista)
class BaristaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
    )
