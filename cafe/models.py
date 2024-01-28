from django.core.exceptions import ValidationError
from django.db import models


def calculation_salary(income: int, rate: "Rate") -> int:
    """
    :param income: - Cafe income per day
    :param rate: - Barista's rate in this cafe
    :return: - If the income is less than min_wage, then the function
    returns min_wage. If the income is greater than min_wage, then the function
    returns the result of the calculation using the formula:

    income / 100 * rate.percent + rate.additive

    We don't need much precision; we can round the value to an integer.
    """
    if income < rate.min_wage:
        return int(rate.min_wage)
    else:
        salary = income / 100 * rate.percent + rate.additive
        return int(salary)


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


class Shift(models.Model):
    """
    The Shift model is responsible for creating a shift for a certain
    date in a certain cafe for one barista.
    The shift has two main parameters:

    'date' - shift date.

    'salary' - This is the barista's salary for the current shift. By default,
    when creating a shift, this field remains empty. Information in this field
    appears after income for the current date is entered into the Income model.

    One barista can only have one shift in one cafe on a certain date.
    This checks the clean() method.
    """

    date = models.DateField(blank=False)
    salary = models.IntegerField(blank=True, null=True)
    cafe = models.ForeignKey(
        Cafe, on_delete=models.CASCADE, blank=False, related_name="shifts"
    )
    barista = models.ForeignKey(
        Barista, on_delete=models.CASCADE, blank=False, related_name="shifts"
    )

    @staticmethod
    def validate_rate(cafe, barista):
        try:
            Rate.objects.get(cafe=cafe, barista=barista)
        except Rate.DoesNotExist:
            raise ValidationError(f"Barista {barista} has no rate for '{cafe}' cafe!")

    @staticmethod
    def validate_shift(date, barista):
        shift = Shift.objects.filter(date=date, barista_id=barista)
        if len(shift) != 0:
            raise ValidationError(
                {
                    "barista": f"On {date}, barista {barista}"
                    f" is already busy in the another cafe."
                }
            )

    @staticmethod
    def income_calculation(shift, date, cafe):
        rate = Rate.objects.get(cafe=cafe, barista=shift.barista.id)
        try:
            income = Income.objects.get(date=date, cafe=cafe)
            shift.salary = calculation_salary(income=income.income, rate=rate)
        except Income.DoesNotExist:
            print("No INCOME for this date", Income.DoesNotExist)

    def clean(self):
        Shift.validate_rate(self.cafe, self.barista)
        Shift.validate_shift(date=self.date, barista=self.barista)
        Shift.income_calculation(self, self.date, self.cafe)

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Shift, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.date} | Cafe: {self.cafe} | Barista: {self.barista}"

    class Meta:
        unique_together = ("date", "cafe")
        ordering = ["date", "cafe", "barista"]


class Income(models.Model):
    """
    The Income model is responsible for creating a shift for a certain
    date in a certain cafe for one barista.
    The Income has two parameters:

    'date' - income date.

    'income' - amount of income. In this project we can neglect accuracy.
    We only need integers.

    While saving income for a certain date, when running the clean() method,
    the barisa's salary for a given shift is calculated using the
    calculation_salary() function and entered into the 'salary' field in the
    'Shift' model.
    """

    date = models.DateField(blank=False)
    income = models.IntegerField(blank=False)
    cafe = models.ForeignKey(
        Cafe, on_delete=models.DO_NOTHING, blank=False, related_name="incomes"
    )

    def clean(self):
        """
        This method, using the calculation_salary() function, calculates the
        salary of a barista in a specific cafe for one day and enters it into
        the 'salary' field of the 'Shift' model
        """

        try:
            shift = Shift.objects.get(date=self.date, cafe=self.cafe)
        except Shift.DoesNotExist:
            raise ValidationError("No barista on shift!")
        try:
            rate = Rate.objects.get(cafe=self.cafe, barista=shift.barista.id)
        except Rate.DoesNotExist:
            raise ValidationError("No barista rates for this cafe!")
        salary = calculation_salary(income=self.income, rate=rate)
        shift.salary = salary
        shift.save()

    def __str__(self):
        return f"{self.date}, Cafe: {self.cafe}, Income - ${self.income}"

    class Meta:
        unique_together = ("date", "cafe")
        ordering = ["date", "cafe"]
