from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    # Main list
    list_display = ('is_superuser', 'email', 'display_name', 'date_joined', 'last_login', 'is_active',)
    list_display_links = ('email', 'display_name',)
    list_filter = ('is_active',)
    search_fields = ('email', 'display_name',)
    ordering = ('-is_superuser', 'email')

    # Specific CustomUser instance
    fieldsets = (
        ('Account', {'fields': ('email', 'password', 'display_name',)}),
        ('Dates', {'fields': ('date_joined', 'last_login',)}),
        ('Permissions', {'fields': ('is_active', 'is_superuser',)}),
    )
    add_fieldsets = (
        ('Account', {'fields': ('email', 'display_name', 'password1', 'password2',)}),
        ('Permissions', {'fields': ('is_superuser',)}),
    )
    readonly_fields = ['date_joined', 'last_login',]
