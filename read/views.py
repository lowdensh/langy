from django.shortcuts import get_object_or_404, render

from .models import Book


def view_books(request):
    book_list = Book.objects.all()
    context = {'book_list': book_list}
    return render(request, 'read/view-books.html', context)


def details(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    context = {'book': book}
    return render(request, 'read/details.html', context)


def read(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    context = {'book': book}
    return render(request, 'read/read.html', context)
