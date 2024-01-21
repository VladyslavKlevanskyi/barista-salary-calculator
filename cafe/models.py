from django.db import models


class Cafe(models.Model):
    """
    Cafe model with name field.
    """

    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Barista(models.Model):
    """
    Barista model with full_name field.
    """

    full_name = models.CharField(max_length=150, blank=False)

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ["id"]


class Rate(models.Model):
    """
    Barista rates model. Based on these data, it is estimated how much a
    barista earned per day in a certain cafe.
    The rate has three main parameters:

    'min_wage' - the minimum amount that the barista will receive if the cafe’s
    income that day is less than this parameter.

    'percent' - this is the percentage of the cafe’s income that the barista
    will receive if the cafe’s daily income is higher than the 'min_rate'.

    'additive' - an additional amount to the barista’s salary if the cafe’s
    daly income is higher than the minimum rate.

    Each barista have only one rate for each cafe.
    """

    min_wage = models.IntegerField(blank=False)
    percent = models.IntegerField(blank=False)
    additive = models.IntegerField(blank=False)
    cafe = models.ForeignKey(
        Cafe, on_delete=models.CASCADE, blank=False, related_name="rates"
    )
    barista = models.ForeignKey(
        Barista, on_delete=models.CASCADE, blank=False, related_name="rates"
    )

    def __str__(self):
        return f"Barista: {self.barista} | Cafe: {self.cafe}"

    class Meta:
        unique_together = ("barista", "cafe")
        ordering = ["barista", "cafe"]
