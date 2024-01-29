from datetime import date as day
from django.core.exceptions import ValidationError
from django.test import TestCase
from cafe.models import Cafe, Barista, Shift, Rate, Income

DATE1 = day(year=2022, month=2, day=24)
DATE2 = day(year=2023, month=2, day=24)
CAFE1_NAME = "SuperCafe"
CAFE2_NAME = "MegaCafe"
BARISTA1_NAME = "John Smith"
BARISTA2_NAME = "Mr Martin"


class ShiftModelTests(TestCase):
    def setUp(self):
        self.date = DATE1
        self.cafe1 = Cafe.objects.create(name=CAFE1_NAME)
        self.cafe2 = Cafe.objects.create(name=CAFE2_NAME)
        self.barista = Barista.objects.create(full_name=BARISTA1_NAME)
        self.rate1 = Rate.objects.create(
            min_wage=500,
            percent=5,
            additive=300,
            cafe=self.cafe1,
            barista=self.barista,
        )
        self.rate2 = Rate.objects.create(
            min_wage=400,
            percent=4,
            additive=200,
            cafe=self.cafe2,
            barista=self.barista,
        )

        self.shift = Shift.objects.create(
            date=self.date, cafe=self.cafe1, barista=self.barista
        )

    def test_str_in_shift_model(self):
        """
        Test that the __str__ method shows all fields correctly
        """

        self.assertEqual(
            str(self.shift),
            f"{self.date} | Cafe: {self.cafe1} | "
            f"Barista: {self.barista} | Salary: None",
        )

    def test_create_shift_if_barista_is_busy(self):
        """
        Impossible to create a shift with a barista who is busy that day in
        another cafe
        """
        barista = Barista.objects.get(full_name=BARISTA1_NAME)

        with self.assertRaisesMessage(
            ValidationError,
            f"On {self.date}, barista {barista} "
            f"is already busy in the another cafe.",
        ):
            Shift.objects.create(date=DATE1, cafe=self.cafe2, barista=barista)

    def test_create_shift_for_barista_without_rates(self):
        """
        Impossible to create a shift with a barista who has no rete in this
        cafe
        """
        barista = Barista.objects.create(full_name=BARISTA2_NAME)

        with self.assertRaisesMessage(
            ValidationError, f"Barista {barista} has"
                             f" no rate for '{self.cafe1}' cafe!"
        ):
            Shift.objects.create(date=DATE2, cafe=self.cafe1, barista=barista)

    def test_calculation_salary(self):
        """
        The test is that the salary is calculated if income exists in this cafe
        on that day.
        """
        # Create new Income for existing shift. We must do this for the
        # existing shift, otherwise the income will not be created.
        Income.objects.create(date=self.date, cafe=self.cafe1, income=5870)

        # Get existing shift
        existing_shift = Shift.objects.get(date=self.date, cafe=self.cafe1)

        # Remember the ID of the old shift
        existing_shift_id = existing_shift.id

        # Delete existing shift
        existing_shift.delete()

        # Create another shift for the day for which there is income.
        shift_new = Shift.objects.create(
            date=self.date, cafe=self.cafe1, barista=self.barista
        )

        self.assertEqual(shift_new.salary, 593)
        # Different IDs show that the old shift was deleted and a new one was
        # created
        self.assertNotEqual(existing_shift_id, shift_new.id)


class IncomeModelTests(TestCase):
    def setUp(self):
        self.date = DATE1
        self.cafe = Cafe.objects.create(name=CAFE1_NAME)
        self.barista = Barista.objects.create(full_name=BARISTA1_NAME)
        self.rate = Rate.objects.create(
            min_wage=500,
            percent=5,
            additive=300,
            cafe=self.cafe,
            barista=self.barista,
        )
        self.shift = Shift.objects.create(
            date=self.date, cafe=self.cafe, barista=self.barista
        )
        self.income = Income.objects.create(
            date=self.date,
            cafe=self.cafe,
            income=5555
        )

    def test_str_in_income_model(self):
        """
        Test that the __str__ method shows all fields correctly
        """

        self.assertEqual(
            str(self.income),
            f"{self.date}, Cafe: {self.cafe}, "
            f"Income - ${self.income.income}",
        )

    def test_create_income_if_there_is_no_shift(self):
        """
        Impossible to create income if there is no shift that day at this cafe
        """

        date = DATE2

        with self.assertRaisesMessage(
            ValidationError,
            f"There is no barista on shift at the "
            f"'{self.cafe}' Cafe on {date}!",
        ):
            Income.objects.create(date=DATE2, cafe=self.cafe, income=5555)

    def test_create_income_if_there_is_no_barista_rates(self):
        """
        Impossible to create an income with a barista who has no rete in this
        cafe
        """

        date = DATE2
        Shift.objects.create(date=date, cafe=self.cafe, barista=self.barista)

        rate = Rate.objects.get(
            cafe=self.cafe,
            barista=self.barista,
        )
        rate.delete()

        with self.assertRaisesMessage(
            ValidationError,
            f"Barista {self.barista} "
            f"has no rate for '{self.cafe}' cafe!",
        ):
            Income.objects.create(date=date, cafe=self.cafe, income=5555)

    def test_calculation_salary(self):
        """
        The test is that the salary is calculated if shift exists in this cafe
        on that day.
        """

        # Create shift.
        date = DATE2
        shift = Shift.objects.create(
            date=date,
            cafe=self.cafe,
            barista=self.barista
        )

        # Create income
        Income.objects.create(date=date, cafe=self.cafe, income=6870)

        # Refresh variable
        shift.refresh_from_db()

        self.assertEqual(shift.salary, 643)
