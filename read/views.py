from .forms import BookPDFForm
from .models import Book, Page
from language.models import ForeignLanguage, TranslatableWord
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from googletrans import Translator
import json, nltk, pdfplumber, re
nltk.download('stopwords')


@login_required
def my_books(request):
    books = Book.objects.all()
    books_readable = []
    books_unreadable = []

    for book in books:
        if book.has_pages:
            books_readable.append(book)
        else:
            books_unreadable.append(book)

    context = {
        'books_readable': books_readable,
        'books_unreadable': books_unreadable
    }
    return render(request, 'read/my-books.html', context)


@login_required
def details(request, book_id):
    context = {
        'book': get_object_or_404(Book, pk=book_id)
    }
    return render(request, 'read/details.html', context)


@login_required
@staff_member_required
def pages_manage(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    context = {
        'book': book,
        'form':  BookPDFForm(instance=book)
    }
    return render(request, 'read/pages-manage.html', context)


@login_required
@staff_member_required
def pages_upload_pdf(request, book_id):
    try:
        book = get_object_or_404(Book, pk=book_id)

        if request.method == 'POST':
            form = BookPDFForm(request.POST, request.FILES, instance=book)
            book.pdf.delete()
            if form.is_valid():
                form.save()

        form = BookPDFForm(instance=book)  

        context = {
            'book': book,
            'form': form
        }
        return render(request, 'read/pages-manage.html', context)

    except Exception:
        return HttpResponseBadRequest('Bad request')


@login_required
@staff_member_required
def pages_generate(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if book.has_pdf:
        text_content = []
        with pdfplumber.open(book.pdf) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                text = text.replace('\n', ' ')
                text = text.replace('  ', ' ')
                text_content.append(text)
    else:
        text_content = None

    context = {
        'book': book,
        'text_content': text_content
    }
    return render(request, 'read/pages-generate.html', context)


@login_required
@staff_member_required
def pages_save(request, book_id):
    try:
        if request.method == 'POST':
            book = get_object_or_404(Book, pk=book_id)
            json_data = json.loads(request.body)
            text_content = json_data['text_content']

            # Delete existing pages
            Page.objects.filter(book__id=book_id).delete()

            # Create new pages
            for i, text in enumerate(text_content, 1):
                Page.objects.create(
                    book = book,
                    number = i,
                    text = text
                )
                
            return JsonResponse({'success': True})

        else:
            return HttpResponseBadRequest('Invalid request method')

    except Exception:
        return HttpResponseBadRequest('Bad request')


@login_required
@staff_member_required
def words_manage(request, book_id):
    context = {
        'book': get_object_or_404(Book, pk=book_id)
    }
    return render(request, 'read/words-manage.html', context)


@login_required
@staff_member_required
def words_generate(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    # One string containing all book text
    text = ""
    for page in book.pages.all():
        text += page.text

    # Separate book text into individual words
    # Remove punctuation, stopwords, and convert to lowercase
    words = nltk.tokenize.word_tokenize(text)
    words = [w.lower() for w in words if w.isalnum()]
    words = [w for w in words if not w in nltk.corpus.stopwords.words()]

    # Dictionary of unique words and their frequencies
    fdist = nltk.probability.FreqDist(words)
    unique_word_count = len(fdist)

    # List of all unique words and their frequencies
    # List of tuples of the form ('word', frequency), ordered by most frequent first
    common_words = fdist.most_common(unique_word_count)

    # Keep a maximum amount of tuples for words which meet a minimum frequency
    MIN_FREQUENCY = 3
    MAX_COMMON_WORDS = 50
    common_words = list(filter(lambda f: f[1] >= MIN_FREQUENCY, common_words))[:MAX_COMMON_WORDS]

    context = {
        'book': book,
        'unique_word_count': unique_word_count,
        'minimum_frequency': MIN_FREQUENCY,
        'common_words': common_words
    }
    return render(request, 'read/words-generate.html', context)


@login_required
@staff_member_required
def words_save(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=book_id)
        json_data = json.loads(request.body)
        words = json_data['words']

        for word in words:
            try:
                # Find the TranslatableWord matching this English word
                translatable_word = TranslatableWord.objects.get(english_word=word)
            except TranslatableWord.DoesNotExist:
                # If it doesn't exist, create it
                translatable_word = TranslatableWord.objects.create(english_word=word)
        
            # Add this Book to the TranslatableWord, if not already added
            if book not in translatable_word.books.all():
                translatable_word.books.add(book)
            
        return JsonResponse({'success': True})

    else:
        return HttpResponseBadRequest('Invalid request method')


@login_required
@staff_member_required
def words_translate(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    context = {
        'book': book,
        'foreign_languages': ForeignLanguage.objects.all(),
        'translatable_words': book.translatable_words.all(),
    }
    return render(request, 'read/words-translate.html', context)


@login_required
def read(request, book_id):
    context = {
        'book': get_object_or_404(Book, pk=book_id)
    }
    return render(request, 'read/read.html', context)


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
