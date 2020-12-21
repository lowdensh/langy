from .forms import BookPDFForm
from .models import Book
from language.models import TranslatableWord
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from googletrans import Translator
import re


@login_required
def my_books(request):
    template = 'read/my-books.html'
    context = {
        'book_list': Book.objects.all()
    }
    return render(request, template, context)


@login_required
def details(request, book_id):
    template = 'read/details.html'
    book = get_object_or_404(Book, pk=book_id)
    context = {
        'book': book
    }
    return render(request, template, context)


@login_required
@staff_member_required
def pages_manage(request, book_id):
    template = 'read/pages-manage.html'
    book = get_object_or_404(Book, pk=book_id)
    form = BookPDFForm(instance=book)
    context = {
        'book': book,
        'form':  form
    }
    return render(request, template, context)


@login_required
@staff_member_required
def pages_generate(request, book_id):
    template = 'read/pages-generate.html'
    book = get_object_or_404(Book, pk=book_id)
    form = BookPDFForm(instance=book) 
    context = {
        'book': book,
        'form':  form
    }
    return render(request, template, context)


@login_required
@staff_member_required
def pages_upload_pdf(request, book_id):
    try:
        template = 'read/pages-manage.html'
        book = get_object_or_404(Book, pk=book_id)

        if request.method == 'POST':
            form = BookPDFForm(request.POST, request.FILES, instance=book)
            book.pdf.delete()
            if form.is_valid():
                form.save()

        form = BookPDFForm(instance=book)  
        context = {
            'book': book,
            'form':  form
        }
        return render(request, template, context)

    except Exception:
        return HttpResponseBadRequest('Bad request')


# wip read functionality
@login_required
def read_wip(request):
    # change this in urls.py too
    book_id = 1

    # TODO where should translations be done and stored?
    # user account section when selecting learning language? translations fetched on language selection?
    # TODO translation for plurals
    # plurals are not stored in the database - yet!
    # TODO direct translation of single words vs word in the context of the whole sentence - NLP?
    # as it stands, translation is for single words and this means things are sometimes incorrect
    # e.g. genders, word order etc.

    # https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages
    learning_language = 'sv'

    english_word_list = TranslatableWord.objects.all()
    english_word_list = [word.english_word for word in english_word_list]
    translator = Translator()
    foreign_word_list = translator.translate(
        english_word_list,
        src='en',
        dest=learning_language)

    # TODO how and where should book text be stored?
    file_path = 'static/books/monkeypen/002-GINGER-THE-GIRAFFE-Free-Childrens-Book-By-Monkey-Pen-unlocked.txt'
    file_text = open(file_path, encoding='utf8', errors='ignore').read()

    # TODO efficiency of search/replace
    # go through every word in word_list? or file_text?
    # time complexity of search/replace
    for i, english_word in enumerate(english_word_list):
        foreign_word = foreign_word_list[i].text
        pattern = re.compile(rf'(?<![^\W]){english_word}(?![^\W])', re.I)
        replacement = f'<button class="tappyWord"> {foreign_word} <span> {english_word} </span></button>'
        file_text = re.sub(pattern, replacement, file_text)

    # TODO should text be large paragraphs or short sentences?
    # text file into paragraphs
    paragraph_list = file_text.split('\n\n')
    paragraph_list = [paragraph.replace('\n', ' ') for paragraph in paragraph_list]

    # text file into paragraphs into sentences - rudimentary splitting
    # paragraph_list = file_text.split('\n\n')
    # paragraph_list = [paragraph.replace('\n', ' ') for paragraph in paragraph_list]
    # sentence_list = []
    # for paragraph in paragraph_list:
    #     sentences = paragraph.split('. ')
    #     for s in sentences:
    #         sentence_list.append(s + '.')

    template = 'read/read-wip.html'
    book = get_object_or_404(Book, pk=book_id)
    context = {
        'book': book,
        'author_name': book.author.full_name,
        'word_list': english_word_list,
        'paragraph_list': paragraph_list
    }
    return render(request, template, context)


# https://docs.djangoproject.com/en/3.1/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test
# user should own the book
@login_required
def read(request, book_id):
    template = 'read/read.html'
    book = get_object_or_404(Book, pk=book_id)
    context = {
        'book': book,
        'author_name': book.author.full_name
    }
    return render(request, template, context)
