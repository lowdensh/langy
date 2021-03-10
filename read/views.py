from .forms import BookPDFForm
from .models import Book, Page
from language.models import ForeignLanguage, TranslatableWord, Translation
from tracking.models import LangySession, LearningTrace
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from googletrans import Translator
import json, nltk, pdfplumber, re
nltk.download('stopwords')


@login_required
def books(request):
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
    return render(request, 'read/books.html', context)


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
    # List of tuples of the form ('word', frequency), ordered by most frequent words first
    common_words = fdist.most_common(unique_word_count)

    # Keep a maximum amount of tuples for words which meet a minimum frequency
    MIN_FREQUENCY = 3
    MAX_COMMON_WORDS = 50
    common_words = list(
        filter(lambda cw: cw[1] >= MIN_FREQUENCY, common_words)
    )[:MAX_COMMON_WORDS]

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
def start_read(request, book_id):
    # User must have an active LearningLanguage to read a Book
    if request.user.active_language is None:
        return redirect('users:select_a_language')

    book = get_object_or_404(Book, pk=book_id)
    langy_session_id = LangySession.objects.create(
        user = request.user,
        foreign_language = request.user.active_language.foreign_language,
        session_type = 'READ',
        book = book,
    ).id

    return redirect(reverse('read:read', args=[book_id, langy_session_id]))


@login_required
def read(request, book_id, langy_session_id):
    book = get_object_or_404(Book, pk=book_id)
    langy_session = get_object_or_404(LangySession, pk=langy_session_id)

    # Get the user's active LearningLanguage and appropriate Translations
    foreign_language = request.user.active_language.foreign_language
    translations = book.available_translations(foreign_language)

    # Build a list of Page text to be manipulated
    page_text_html = [page.text for page in book.pages.all()]

    # Find and replace whole English words with interactable HTML
    for t in translations:
        pattern = rf'\b{t.translatable_word.english_word}\b'

        if foreign_language.uses_latin_script:
            # Visible word    : t.foreign_word
            # Popover content : t.foreign_word
            replacement = ('<span data-toggle="popover" data-placement="top" data-trigger="focus" data-html="true"'
                                f'data-translation-id="{t.id}"'
                                f'title="{t.translatable_word.english_word}"'
                                f'data-content="{t.foreign_word}">'
                                f'<a tabindex="0" class="btn btn-success btn-word" role="button">{t.foreign_word}</a>'
                            '</span>')
        else:
            # Visible word    : t.pronunciation
            # Popover content : t.pronunciation AND t.foreign_word
            replacement = ('<span data-toggle="popover" data-placement="top" data-trigger="focus" data-html="true"'
                                f'data-translation-id="{t.id}"'
                                f'title="{t.translatable_word.english_word}"'
                                f'data-content="{t.pronunciation} <br> {t.foreign_word}">'
                                f'<a tabindex="0" class="btn btn-success btn-word" role="button">{t.pronunciation}</a>'
                            '</span>')
        
        # Perform replacement for each Page
        for i, pt in enumerate(page_text_html): 
            page_text_html[i] = re.sub(pattern, replacement, pt, flags=re.IGNORECASE)

    # Build Page-like dicts for use in the template
    pages = []
    for i, pt in enumerate(page_text_html):
        page = {
            'number': i+1,
            'sentences': nltk.tokenize.sent_tokenize(page_text_html[i]),
            'image': book.pages.get(number=i+1).image
        }
        pages.append(page)

    context = {
        'book': book,
        'langy_session': langy_session,
        'pages': pages
    }
    return render(request, 'read/read.html', context)


@login_required
def close_book(request, book_id, langy_session_id):
    # Get, update and save LangySession
    langy_session = get_object_or_404(LangySession, pk=langy_session_id)
    langy_session.end_time = timezone.now()
    langy_session.save()

    return redirect(reverse('read:details', args=[book_id]))
