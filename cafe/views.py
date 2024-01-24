from datetime import date, timedelta
from typing import Dict, List
from django.db.models import QuerySet, Sum
from django.urls import reverse_lazy
from django.views import generic
from cafe.forms import DateRangeForm, ShiftForm, IncomeCreateForm, IncomeUpdateForm
from cafe.models import Cafe, Barista, Shift, Income, Rate


def queryset_to_list(incoming_queryset: QuerySet, model: str) -> List[str]:
    """
    The incoming queryset goes through a cycle and creates a list of cafes
    or baristas, depending on the passed 'model' parameter.

    :param incoming_queryset: incoming queryset.

    :param model: name of model for queryset filtering. "Cafe" or "Barista"
    is expected.

    :return: Returns a list of cafe names, or barista full_names, depending
    on the 'model' parameter.
    """

    returning_list = []
    for element in incoming_queryset:
        if model == "Cafe":
            returning_list.append(element.name)
        if model == "Barista":
            returning_list.append(element.full_name)

    return returning_list


def queryset_to_dict(incoming_queryset: QuerySet, model: str) -> Dict:
    """
    The incoming queryset goes through a cycle and creates a dictionary of
    cafes or baristas, depending on the passed 'model' parameter.

    :param incoming_queryset: incoming queryset.

    :param model: name of model for queryset filtering. "Cafe" or "Barista"
    is expected.

    :return: Returns a dictionary were the keys are the ID and the values
    are the cafe names, or barista full_names, depending on the 'model'
    parameter.
    """

    returning_dict = {}
    for element in incoming_queryset:
        if model == "Cafe":
            returning_dict[element.id] = element.name
        if model == "Barista":
            returning_dict[element.id] = element.full_name

    return returning_dict


def rates_dictionary_creation(
    baristas: QuerySet,
    barista_rates: QuerySet,
    cafes_dict: Dict,
    cafes_list: List,
) -> Dict:
    """
    This function accepts a queryset of barista rates and using other incoming
    parameters, creates a special dictionary that is needed to fill the table
    on the page.

    :param baristas: QuerySet of all barista in DB for obtaining information

    :param barista_rates: QuerySet of all barista rates in DB for obtaining
    information

    :param cafes_dict: A dictionary with information about cafes. In this
    dictionary, the keys are ID of cafes and their values are cafe names.

    :param cafes_list: List with cafe names.

    :return: The function returns a dictionary. The key is the barista's ID.
    The value is a list of dictionaries with rates info for each cafe.
    Every dictionary about rate looks like this:
    {'cafe_name': 'Park', 'min_wage': 250, 'percent': 6, 'additive': 150}

    Example of returning dict:
    {1: [{'cafe_name': 'Park', 'min_wage': 250, 'percent': 6, 'additive': 150},
        {'cafe_name': 'Cofe2Go', 'min_wage': 300, 'percent': 4, 'additive': 50},
        {'cafe_name': 'Mega', 'min_wage': 300, 'percent': 5, 'additive': 250}],
    2: [{'cafe_name': 'Park', 'min_wage': None, 'percent': None, 'additive': None},
        {'cafe_name': 'Cofe2Go', 'min_wage': 6000, 'percent': 8, 'additive': 200},
        {'cafe_name': 'Mega', 'min_wage': 290, 'percent': 5, 'additive': 240}]}
    """

    rates_dict = {}
    rates_data_dict = {}

    # Create a 'rates_dict' dictionary where the key is the barista ID and the
    # value is a list with dictionaries. Each dictionary has only one key-value
    # pair. The key is the string 'cafe_name', and the value is a name of the
    # cafe.
    # example:
    # {1: [{'cafe_name': 'Park'}, {'cafe_name': 'Cofe2Go'},
    #      {'cafe_name': 'Mega'}, {'cafe_name': 'Warm'},
    #      {'cafe_name': 'Hot Coffee'}],
    #  2: [{'cafe_name': 'Park'}, {'cafe_name': 'Cofe2Go'},
    #      {'cafe_name': 'Mega'}, {'cafe_name': 'Warm'},
    #      {'cafe_name': 'Hot Coffee'}]}
    for barista in baristas:
        cafe_rates = []
        for cafe in cafes_list:
            cafe_rates.append({"cafe_name": cafe})
        rates_dict[barista.id] = cafe_rates

    # Create a 'rates_data_dict' dictionary where the key is the barista ID
    # and the value is a dictionaries. Each key in this dictionary is a name
    # of cafe, and the value is a dictionary with rates this barista in this
    # cafe.
    # example:
    # {1: {'Park': {'min_wage': 250, 'percent': 6, 'additive': 150},
    #   'Cofe2Go': {'min_wage': 300, 'percent': 4, 'additive': 50},
    #      'Mega': {'min_wage': 300, 'percent': 5, 'additive': 250}
    #  2: {'Cofe2Go': {'min_wage': 600, 'percent': 8, 'additive': 200},
    #         'Mega': {'min_wage': 290, 'percent': 5, 'additive': 240},
    #         'Warm': {'min_wage': 500, 'percent': 6, 'additive': 300}}}
    for rate in barista_rates.values():
        if rate["barista_id"] not in rates_data_dict:
            rates_data_dict[rate["barista_id"]] = {
                cafes_dict[rate["cafe_id"]]: {
                    "min_wage": rate["min_wage"],
                    "percent": rate["percent"],
                    "additive": rate["additive"],
                }
            }

        else:
            rates_data_dict[rate["barista_id"]][cafes_dict[rate["cafe_id"]]] = {
                "min_wage": rate["min_wage"],
                "percent": rate["percent"],
                "additive": rate["additive"],
            }

    # Update a 'rates_dict' dictionary. Add information about rates in
    # dictionaries from list for each barista. If no information from DB for
    # some barista for some cafe, then put 'None' in 'min_wage', 'percent' and
    # 'additive' values.
    for barista_id, cafes in rates_dict.items():
        for cafe in cafes:
            if cafe["cafe_name"] in rates_data_dict[barista_id]:
                cafe["min_wage"] = rates_data_dict[barista_id][cafe["cafe_name"]][
                    "min_wage"
                ]
                cafe["percent"] = rates_data_dict[barista_id][cafe["cafe_name"]][
                    "percent"
                ]
                cafe["additive"] = rates_data_dict[barista_id][cafe["cafe_name"]][
                    "additive"
                ]

            else:
                cafe["min_wage"] = None
                cafe["percent"] = None
                cafe["additive"] = None

    return rates_dict


def schedule_array_creation(
    cafe_list: List[str], shifts: QuerySet, start_date: str, end_date: str
) -> List:
    """
    This function creates a list. Each value in this list is needed to fill
    one line in the table on the page.

    :param cafe_list: List of cafe names. Each cafe is a separate column in the
    table.
    :param shifts: QuerySet of shifts for obtaining information
    :param start_date: Range start date
    :param end_date: Range end date

    :return: The function returns a list. Each value in the list is a list
    of dictionaries. The number of dictionaries will always be equal to the
    number of cafes in the database plus 1. The first dictionary is a key-value
    pair. The key is a string: 'date', and the value is the date to which the
    information in this value of the first list belongs
    (example: {'date': '2024-01-15'}). The following dictionaries are dictionaries
    with information about the shift, if it exists, for a specific date for
    each cafe. (example: {'name': 'Max Smith', 'shift_id': 9, 'barista_id': 1})

    Example of returning list:
    [[{'date': '2024-01-15'}, {'name': 'Max Smith', 'shift_id': 9, 'barista_id': 1}, '-=-', '-=-'],
    [{'date': '2024-01-16'}, '-=-', '-=-']]
    """

    schedule_array = []
    date_dict = {}
    start_date_format = date.fromisoformat(start_date)
    end_date_format = date.fromisoformat(end_date)
    delta = end_date_format - start_date_format

    # Create a dictionary in which the keys are dates from the range and the
    # values are a list with '-=-' values, the number of which is equal to the
    # number of cafes.
    for index in range(delta.days + 1):
        date_insert = str(start_date_format + timedelta(index))
        date_dict[date_insert] = ["-=-"] * len(cafe_list)

    # Go through the cycle through the shifts and fill the 'date_dict'
    # dictionary with information.
    for shift in shifts:
        index = cafe_list.index(shift.cafe.name)
        date_dict[str(shift.date)][index] = {
            "name": shift.barista.full_name,
            "shift_id": shift.id,
            "barista_id": shift.barista.id,
        }

    # Convert the dictionary into a list of the desired view
    for day, baristas in date_dict.items():
        date_shifts = [{"date": day}]
        date_shifts.extend(baristas)
        schedule_array.append(date_shifts)

    return schedule_array


def income_array_creation(
    incomes: QuerySet, start_date: str, end_date: str
) -> List[Dict]:
    """
    This function creates a list. Each value in the list is a dictionary that
    is needed to fill one line in the table on the page.

    :param incomes: QuerySet of incomes for obtaining information
    :param start_date: Range start date
    :param end_date: Range end date

    :return: The function returns a list. Each value in the list is a
    dictionary. Each dictionary has three keys: 'date', 'income' and 'id'
    (example: {'date': '2024-01-16', 'income': 100, 'id': 2}).
    The values of these keys correspond to the values of one income instance
    from the Income model.

    Example of returning list:
    [{'date': '2024-01-16', 'income': 100, 'id': 2},
     {'date': '2024-01-17', 'income': 0, 'id': None},
     {'date': '2024-01-18', 'income': 4560, 'id': 3}]
    """

    income_array = []
    income_dict = {}

    start_date_format = date.fromisoformat(start_date)
    end_date_format = date.fromisoformat(end_date)
    delta = end_date_format - start_date_format

    # Create a dictionary in which the keys are dates from the range and the
    # values are a dictionary with two keys. 'income': 0 and 'id': None.
    for index in range(delta.days + 1):
        date_insert = str(start_date_format + timedelta(index))
        income_dict[date_insert] = {"income": 0, "id": None}

    # Go through the cycle through the incomes and fill the 'income_dict'
    # dictionary with information form DB.
    for income in incomes:
        income_dict[str(income.date)] = {"income": income.income, "id": income.id}

    # Convert the dictionary into a list of the desired view
    for day, income in income_dict.items():
        income_day = {"date": day}
        income_day["income"] = income["income"]
        income_day["id"] = income["id"]
        income_array.append(income_day)

    return income_array


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
