from django.views import generic

from cafe.models import Cafe, Barista


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
