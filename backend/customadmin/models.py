from django.contrib.auth.models import AbstractUser
from django.db import models

class AdminUser(AbstractUser):
    first_name = models.CharField(max_length=150, null=True)
    last_name = models.CharField(max_length=150, null=True)
    username = models.CharField(max_length=150, unique=True, null=True)
    email = models.EmailField(unique=True, null=True)
    password = models.TextField(null=False, blank=False)  # Ensure enough space for encrypted passwords

    # Adding related_name to prevent clashes
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='adminuser_set', 
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='adminuser_permissions', 
        blank=True
    )

    def __str__(self):
        return self.email
