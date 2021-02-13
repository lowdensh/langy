from .models import ForeignLanguage, TranslatableWord, Translation
from read.models import Book
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, render
from googletrans import Translator
import json


@login_required
@staff_member_required
def translation_page(request):
    context = {
        'foreign_languages': ForeignLanguage.objects.all(),
        'translatable_words': TranslatableWord.objects.all(),
    }
    return render(request, 'language/translate.html', context)


@login_required
@staff_member_required
def translation_page_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    context = {
        'foreign_languages': ForeignLanguage.objects.all(),
        'translatable_words': book.translatable_words.all(),
    }
    return render(request, 'language/translate.html', context)


@login_required
@staff_member_required
def translate_english_words(request, key):
    if request.method == 'POST':
        # Check the translation key for the destination language is supported by Langy
        valid_keys = [foreign_language.key for foreign_language in ForeignLanguage.objects.all()]
        if (key not in valid_keys):
            return HttpResponseBadRequest('Invalid translation key')

        # Get English words to translate from the request
        json_data = json.loads(request.body)
        english_words = json_data['english_words']
        if (len(english_words)==0):
            return HttpResponseBadRequest('No English words received')

        # Translate words
        try:
            translator = Translator()
            translations = translator.translate(
                english_words,
                src='en',
                dest=key
            )
        
        # Check for translation request and response issues
        except AttributeError:
            return HttpResponseBadRequest('Translation failure: attribute error')
        if (len(translations)==0):
            return HttpResponseServerError('Translation failure: no translations received')
        status_code = translations[0]._response.status_code
        if (status_code==429):
            return HttpResponseBadRequest('Translation failure: too many requests')
        elif (status_code!=200):
            print(f'Translation response status code not 200: received {status_code}')

        # Prepare response
        foreign_words = []
        pronunciations = []
        for translation in translations:
            foreign_words.append(translation.text.lower())
            pronunciations.append(translation.pronunciation.lower())

        # For ForeignLanguages not using Latin script, pronunciations should be enabled and stored
        foreign_language = ForeignLanguage.objects.get(key=key)
        enable_pronunciations = not foreign_language.uses_latin_script
        
        return JsonResponse({
            'foreign_words': foreign_words,
            'pronunciations': pronunciations,
            'enable_pronunciations': enable_pronunciations
        })

    else:
        return HttpResponseBadRequest('Invalid request method')

@login_required
@staff_member_required
def save_translations(request, key):
    if request.method == 'POST':
        # Check the translation key is supported by Langy
        valid_keys = [foreign_language.key for foreign_language in ForeignLanguage.objects.all()]
        if (key not in valid_keys):
            return HttpResponseBadRequest('Invalid translation key')
        foreign_language = get_object_or_404(ForeignLanguage, key=key)

        # Get data from the request
        json_data = json.loads(request.body)
        translations = json_data['translations']
        if (len(translations)==0):
            return HttpResponseBadRequest('No translations received in request')

        for translation in translations:
            # Prepare Translation object attributes
            translatable_word = get_object_or_404(TranslatableWord, pk=translation['translatable_word_id'])
            foreign_language = get_object_or_404(ForeignLanguage, key=key)
            foreign_word = translation['foreign_word']

            # Check whether to store pronunciation
            if foreign_language.uses_latin_script:
                pronunciation = ''
            else:
                pronunciation = translation['pronunciation']

            # Don't accept empty foreign words
            # TODO front end validation
            if foreign_word is None or foreign_word.strip() == '':
                print(f'Skipping creation: invalid foreign word for tw-id {translation["translatable_word_id"]}')

            # Update or create Translation object
            else:
                # Check if a Translation already exists
                t = Translation.objects.filter(
                    translatable_word = translatable_word,   
                    foreign_language = foreign_language
                ).first()
                if t:
                    # Translation exists: update it
                    t.foreign_word = foreign_word
                    t.pronunciation = pronunciation
                    t.save()
                else:
                    # Translation does not exist: create it
                    Translation.objects.create(
                        translatable_word = translatable_word,
                        foreign_language = foreign_language,
                        foreign_word = foreign_word,
                        pronunciation = pronunciation
                    )

        return JsonResponse({"success": True})

    else:
        return HttpResponseBadRequest('Invalid request method')
