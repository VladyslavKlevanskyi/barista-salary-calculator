from django import forms
from cafe.models import Cafe, Barista, Shift, Income


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


class IncomeCreateForm(forms.ModelForm):
    """
    Form for creating an income. You need to select a 'date' and 'income'.
    'cafe' field is filled in automatically and is hidden
    """

    date = forms.DateField(
        label="",
        widget=forms.DateInput(attrs={"class": "datepicker"}),
        input_formats=["%Y-%m-%d"],
    )

    cafe = forms.ModelChoiceField(
        queryset=Cafe.objects.all(), widget=forms.HiddenInput()
    )
    income = forms.IntegerField(required=True)

    class Meta:
        model = Income
        fields = "__all__"


class IncomeUpdateForm(forms.ModelForm):
    """
    Form for updating an income. You need to update 'income' field only.
    'cafe' and 'date' fields are filled in automatically and are hidden
    """

    date = forms.DateField(widget=forms.HiddenInput())

    cafe = forms.ModelChoiceField(
        queryset=Cafe.objects.all(), widget=forms.HiddenInput()
    )
    income = forms.IntegerField(required=True)

    class Meta:
        model = Income
        fields = "__all__"
