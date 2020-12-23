from .models import Book
from django import forms


class BookPDFForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['pdf']
