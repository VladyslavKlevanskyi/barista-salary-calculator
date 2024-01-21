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
