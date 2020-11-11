from .models import Author, Book
from django.contrib import admin


admin.site.register([Author, Book])
