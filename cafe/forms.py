from django import forms


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
