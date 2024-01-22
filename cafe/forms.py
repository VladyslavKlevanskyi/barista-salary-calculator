from django import forms
from cafe.models import Cafe, Barista, Shift


class DateRangeForm(forms.Form):
    """
    Form for selecting a date range in the templates.
    """

    start_date = forms.DateField(
        label="",
        widget=forms.DateInput(attrs={"class": "datepicker"}),
        input_formats=["%Y-%m-%d"],
    )
    end_date = forms.DateField(
        label="",
        widget=forms.DateInput(attrs={"class": "datepicker"}),
        input_formats=["%Y-%m-%d"],
    )


class ShiftForm(forms.ModelForm):
    """
    Form for creating a shift. You need to select a date, cafe and barista.
    """

    date = forms.DateField(
        label="",
        widget=forms.DateInput(attrs={"class": "datepicker"}),
        input_formats=["%Y-%m-%d"],
    )

    cafe = forms.ModelChoiceField(queryset=Cafe.objects.all())
    barista = forms.ModelChoiceField(queryset=Barista.objects.all())

    class Meta:
        model = Shift
        fields = ["date", "cafe", "barista"]
