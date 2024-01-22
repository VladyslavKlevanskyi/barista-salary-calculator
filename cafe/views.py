from datetime import date, timedelta
from typing import Dict, List
from django.db.models import QuerySet
from django.views import generic
from cafe.forms import DateRangeForm
from cafe.models import Cafe, Barista, Shift


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

        'date_range' - date range for which we can view shifts. Uses DateRangeForm.
        By default, the 'start_date' is a date seven days ago from the current one,
        and the 'end_date' is a date seven days ahead from the current one.
        So, by default, when we go to the page for the first time, we will see
        a range of shifts for two weeks, where the current date will be in the
        middle.

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
