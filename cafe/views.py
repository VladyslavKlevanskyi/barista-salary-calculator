from datetime import date, timedelta
from typing import Dict
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views import generic
from cafe.forms import DateRangeForm, ShiftForm, IncomeCreateForm, IncomeUpdateForm
from cafe.models import Cafe, Barista, Shift, Income, Rate
from cafe.utils import (
    income_array_creation,
    queryset_to_dict,
    queryset_to_list,
    rates_dictionary_creation,
    schedule_array_creation,
)


class Index(generic.TemplateView):
    """
    Index page displaying the total number of cafes and baristas.
    """

    template_name = "cafe/index.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        num_cafes = Cafe.objects.count()
        num_baristas = Barista.objects.count()

        context = {
            "num_cafes": num_cafes,
            "num_baristas": num_baristas,
        }

        return context


class CafeListView(generic.ListView):
    """
    This view displays list of all cafes from DB.
    """

    model = Cafe


class CafeDetailView(generic.DetailView):
    """
    This view displays information about income a specified period for one
    cafe.
    """

    model = Cafe

    def get_context_data(self, **kwargs):
        """
        We override this method to add such data to the context as
        'date_range', 'income_array' and 'total_income'.

        'date_range' - date range for which we can view shifts. Uses
        DateRangeForm. By default, the 'start_date' is a date seven days ago
        from the current one, and the 'end_date' is a date seven days ahead
        from the current one. So, by default, when we go to the page for the
        first time, we will see a range of shifts for two weeks, where the
        current date will be in the middle.

        'income_array' - an array for displaying information in the income
        table on the page. To create an array, use the income_array_creation()
        function.

        'total_income' - amount of income for the specified period.
        """

        context = super().get_context_data(**kwargs)

        start_date = self.request.GET.get(
            "start_date", str(date.today() - timedelta(7))
        )
        end_date = self.request.GET.get("end_date", str(date.today() + timedelta(7)))

        context["date_range"] = DateRangeForm(
            initial={"start_date": start_date, "end_date": end_date}
        )

        incomes = Income.objects.select_related("cafe").filter(
            cafe=self.object.id,
            date__gte=start_date,
            date__lte=end_date,
        )

        income_array = income_array_creation(incomes, start_date, end_date)
        total_income = incomes.aggregate(Sum("income"))

        context["income_array"] = income_array
        context["total_income"] = total_income["income__sum"]

        return context


class BaristaListView(generic.ListView):
    """
    This view displays information about all baristas including their rates in
    different cafes.
    """

    model = Barista
    paginate_by = 10

    def get_context_data(self, **kwargs):
        """
        We override this method to add such data to the context as 'rates' and
        'cafe_list'.

        'rates' - Barista rates, which have been converted into a dictionary to
        reduce the number of requests in DB. In this way, one request is made
        and the queryset is passed to the rates_dictionary_creation() function
        that returns a dictionary, which is passed it to the template.

        'cafe_list' - a list of names of all cafes for adding them into
        the table header. This parameter is passed into template as a list in
        order to reduce the number of requests in the database. The request is
        created once, then using the queryset_to_list() function the queryset
        is converted into a list.
        """

        context = super().get_context_data(**kwargs)
        cafes = Cafe.objects.all()
        all_cafes_dict = queryset_to_dict(cafes, "Cafe")
        all_cafes_list = queryset_to_list(cafes, "Cafe")
        all_barista_rates = Rate.objects.select_related("barista", "cafe")
        all_baristas = Barista.objects.all()

        context["rates"] = rates_dictionary_creation(
            baristas=all_baristas,
            barista_rates=all_barista_rates,
            cafes_dict=all_cafes_dict,
            cafes_list=all_cafes_list,
        )
        context["cafe_list"] = all_cafes_list

        return context


class BaristaDetailView(generic.DetailView):
    """
    This view calculates the barista's salary for the specified date range.
    """

    model = Barista

    def get_context_data(self, **kwargs):
        """
        Override this method to add such data to the context as 'date_range',
        'shifts' and 'salary'.

        'date_range' - date range for which we can view shifts. Uses
        DateRangeForm. By default, the 'start_date' is a date seven days ago
        from the current one, and the 'end_date' is a date seven days ahead
        from the current one. So, by default, when we go to the page for the
        first time, we will see a range of shifts for two weeks, where the
        current date will be in the middle.

        'shifts' - list of incomes for each shift

        'salary' - salary amount for the specified period
        """
        context = super().get_context_data(**kwargs)

        start_date = self.request.GET.get(
            "start_date", str(date.today() - timedelta(7))
        )
        end_date = self.request.GET.get("end_date", str(date.today() + timedelta(7)))

        context["date_range"] = DateRangeForm(
            initial={"start_date": start_date, "end_date": end_date}
        )

        shifts = Shift.objects.select_related("barista", "cafe").filter(
            barista__id=context["object"].id,
            date__gte=start_date,
            date__lte=end_date,
        )

        salary = shifts.aggregate(Sum("salary"))

        context["shifts"] = shifts
        context["salary"] = salary["salary__sum"]

        return context


class ShiftListView(generic.ListView):
    """
    This view displays information about all barista shifts in all cafes for
    the selected period.
    """

    model = Shift

    def get_context_data(self, **kwargs) -> Dict:
        """
        We override this method to add such data to the context as 'date_range',
        'column_headers' and 'schedule_array'.

        'date_range' - date range for which we can view shifts. Uses
        DateRangeForm. By default, the 'start_date' is a date seven days ago
        from the current one, and the 'end_date' is a date seven days ahead
        from the current one. So, by default, when we go to the page for the
        first time, we will see a range of shifts for two weeks, where the
        current date will be in the middle.

        'column_headers' - a list of names of all cafes for adding them into
        the table header. This parameter is passed into template as a list in
        order to reduce the number of requests in the database. The request is
        created once, then using the queryset_to_list() function the queryset
        is converted into a list.

        'schedule_array' - a list of lines for the shift table. Generated by
        schedule_array_creation() function.
        """

        context = super().get_context_data(**kwargs)
        all_cafes_list = queryset_to_list(Cafe.objects.all(), "Cafe")

        start_date = self.request.GET.get(
            "start_date", str(date.today() - timedelta(7))
        )
        end_date = self.request.GET.get("end_date", str(date.today() + timedelta(7)))

        context["date_range"] = DateRangeForm(
            initial={"start_date": start_date, "end_date": end_date}
        )

        shifts = Shift.objects.select_related("barista", "cafe").filter(
            date__gte=start_date,
            date__lte=end_date,
        )

        schedule_array = schedule_array_creation(
            all_cafes_list, shifts, start_date, end_date
        )

        context["column_headers"] = all_cafes_list
        context["schedule_array"] = schedule_array

        return context


class ShiftCreateView(generic.CreateView):
    """
    This view creates a shift using a 'ShiftForm' form.
    """

    model = Shift
    form_class = ShiftForm
    success_url = reverse_lazy("cafe:shift-list-view")


class ShiftUpdateView(generic.UpdateView):
    """
    This view updates a shift using a 'ShiftForm' form.
    """

    model = Shift
    form_class = ShiftForm
    success_url = reverse_lazy("cafe:shift-list-view")


class ShiftDeleteView(generic.DeleteView):
    """
    This view deletes a shift using.
    """

    model = Shift
    success_url = reverse_lazy("cafe:shift-list-view")


class IncomeCreateView(generic.CreateView):
    """
    This view is for creating an income instance. You only need to enter the
    'date' and 'income'. The cafe is selected automatically and transferred
    from the page of the cafe on which the button 'Add income' was clicked.
    """

    model = Income
    form_class = IncomeCreateForm

    def get_context_data(self, **kwargs):
        """
        Override this method to add such data to the context as 'cafe_name'.
        """

        context = super().get_context_data(**kwargs)
        cafe_name = Cafe.objects.get(id=self.request.GET.get("cafe"))
        context["cafe_name"] = cafe_name
        return context

    def get_initial(self):
        """
        Override this method for sending cafe's ID as 'cafe' parameter to the
        form
        """
        return {"cafe": self.request.GET.get("cafe")}

    def get_success_url(self):
        """
        Override this method for returning to the previous cafe detail page
        """
        return reverse_lazy(
            "cafe:cafe-detail-view", kwargs={"pk": int(self.request.POST.get("cafe"))}
        )


class IncomeUpdateView(generic.UpdateView):
    """
    This view is for updating an income. You only need to update the 'income'
    field. The cafe and date are selected automatically and transferred
    from the page of the cafe on which the button 'edit' was clicked.
    """

    model = Income
    form_class = IncomeUpdateForm

    def get_success_url(self):
        """
        Override this method for returning to the previous cafe detail page
        """
        return reverse_lazy(
            "cafe:cafe-detail-view", kwargs={"pk": int(self.request.POST.get("cafe"))}
        )
