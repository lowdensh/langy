from .models import Author, Book, TranslatableWord
from django.shortcuts import get_object_or_404, render


def view_books(request):
    template = 'read/view-books.html'
    context = {
        'book_list': Book.objects.all()
    }
    return render(request, template, context)


def details(request, book_id):
    template = 'read/details.html'
    book = get_object_or_404(Book, pk=book_id)
    context = {
        'book': book,
        'author_name': book.author.western_order()
    }
    return render(request, template, context)


# wip read functionality
def read_wip(request):
    # change this in urls.py too
    book_id = 1

    file_path = r"C:\Users\Shona\Desktop\Books\002-GINGER-THE-GIRAFFE-Free-Childrens-Book-By-Monkey-Pen-unlocked.txt"
    # https://docs.python.org/3/library/functions.html#open
    file = open(file_path, encoding='utf8', errors='ignore')
    paragraph_list = file.read().split('\n\n')
    paragraph_list = [paragraph.replace('\n', ' ') for paragraph in paragraph_list]

    template = 'read/read-wip.html'
    book = get_object_or_404(Book, pk=book_id)
    context = {
        'book': book,
        'author_name': book.author.western_order(),
        'word_list': TranslatableWord.objects.all(),
        'paragraph_list': paragraph_list
    }
    return render(request, template, context)


def read(request, book_id):
    template = 'read/read.html'
    book = get_object_or_404(Book, pk=book_id)
    context = {
        'book': book,
        'author_name': book.author.western_order()
    }
    return render(request, template, context)
