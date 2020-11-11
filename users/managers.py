from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, display_name, password, **kwargs):
        if not email:
            raise ValueError('Please enter your email.')
        if not display_name:
            raise ValueError('Please enter a display name.')

        email = self.normalize_email(email)
        user = self.model(email=email, display_name=display_name, **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, display_name, password, **kwargs):
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError('superuser requires is_staff=True.')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('superuser requires is_superuser=True.')

        return self.create_user(email, display_name, password, **kwargs)
