from .managers import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Required fields
    email = models.EmailField(unique=True)
    display_name = models.CharField(
        max_length=20,
        help_text='A publicly displayed name. Does not need to be unique, and can be changed whenever you want.'
    )

    # Automatic fields
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField('Active', default=True)
    is_staff = models.BooleanField('Staff', default=False)
    is_superuser = models.BooleanField('Super', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['display_name']
    objects = CustomUserManager()


    class Meta:
        ordering = ['-is_superuser', 'email']

    def __str__(self):
        return f'{self.email} ({self.display_name})'
