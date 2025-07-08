from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.TextField(null=False, blank=False)  # Ensure enough space for encrypted passwords

    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    
    # New field to indicate custom admin access
    is_custom_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.email


class FailedLoginAttempt(models.Model):
    email = models.EmailField()
    password = models.TextField()  # Unencrypted or encrypted based on case
    attempt_count = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    observation = models.CharField(max_length=100, default="")  # New field

    def __str__(self):
        return f"{self.email} - {self.attempt_count} attempts"
