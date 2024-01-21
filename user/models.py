from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    User model with the '_group' method. This method is needed to display a
    list of groups to which the user belongs in the Django admin panel.
    """

    def _groups(self):
        return ",".join([str(p) for p in self.groups.all()])
