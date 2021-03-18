from language.models import Translation
from tracking.models import LangySession, LearningTrace
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
import jellyfish, json


NUM_WORDS = 7


@login_required
def info(request):
    # Prepare error message based on user eligibility for test
    error_message = None

    if request.user.active_language is None:
        error_message = 'You have no active language!'
        
    else:
        foreign_language = request.user.active_language.foreign_language
        words_seen = len(request.user.words_seen(foreign_language))

        if words_seen == 0:
            error_message = (
                f'You haven\'t seen any words in {foreign_language.english_name} yet!<br>'
                f'You need to see at least {NUM_WORDS} words to take a test.')

        elif words_seen < NUM_WORDS:
            plural = 's' if words_seen!=1 else ''
            error_message = (
                f'You have seen {words_seen} word{plural} in {foreign_language.english_name} so far.<br>'
                f'You need to see at least {words_seen} words to take a test. {NUM_WORDS-words_seen} more to go!')

    context = {
        'num_words': NUM_WORDS,
        'error_message': error_message,
    }
    return render(request, 'wordtest/info.html', context)


@login_required
def start_test(request):
    # User must have an active LearningLanguage to take a test
    if request.user.active_language is None:
        return redirect('language:select')

    # User must have seen at least NUM_WORDS to take a test
    foreign_language = request.user.active_language.foreign_language
    if len(request.user.words_seen(foreign_language)) < NUM_WORDS:
        return redirect('wordtest:info')

    # End any other active LangySessions for Testing
    active = LangySession.objects.filter(
        user = request.user,
        end_time = None,
        session_type = 'TEST')
    for s in active:
        s.end_time = timezone.now()
        s.save()

    # Start new LangySession
    langy_session_id = LangySession.objects.create(
        user = request.user,
        foreign_language = foreign_language,
        session_type = 'TEST',
    ).id

    return redirect(reverse('wordtest:test', args=[langy_session_id]))


@login_required
def test(request, langy_session_id):
    langy_session = get_object_or_404(LangySession, pk=langy_session_id)
    if langy_session.end_time is not None:
        context = {
            'num_words': NUM_WORDS,
            'error_message': 'This test has already been finished.',
        }
        return render(request, 'wordtest/info.html', context)

    # Get user's active ForeignLanguage
    foreign_language = request.user.active_language.foreign_language

    # Use LearningTrace data to determine which words (Translation objects) to include in a test
    candidate_traces = request.user.traces_unique(foreign_language, ordering='oldest')

    # Prepare a total of NUM_WORDS Translations to test the user on
    # TODO intelligent selection. simple selection here: just take the 7 oldest
    translations = [trace.translation for trace in candidate_traces]
    translations = translations[:NUM_WORDS]

    context = {
        'langy_session': langy_session,
        'translations': translations,
    }
    return render(request, 'wordtest/test.html', context)


@login_required
def submit_answers(request, langy_session_id):
    if request.method == 'POST':
        # Get, update and save LangySession
        langy_session = get_object_or_404(LangySession, pk=langy_session_id)
        langy_session.end_time = timezone.now()
        langy_session.save()

        # Get data from the request
        json_data = json.loads(request.body)
        answers = json_data['answers']
        if (len(answers)==0):
            return HttpResponseBadRequest('No answers received in request')
        
        # Prepare to create a response with results and create new LearningTraces
        response_results = []
        for answer in answers:
            translation = get_object_or_404(Translation, pk=answer['translation_id'])

            # Get user answer, ignore capitalisation
            user_english = answer['user_english'].lower()

            # Get correct answer(s)
            true_english = translation.translatable_word.english_word.lower()
            synonyms = [syn.english_word for syn in translation.translatable_word.synonyms.all()]
            if len(synonyms) != 0:
                # Find the closest word to the user's input
                max_sim = jellyfish.jaro_winkler_similarity(user_english, true_english)
                for syn in synonyms:
                    sim = jellyfish.jaro_winkler_similarity(user_english, syn)
                    if sim > max_sim:
                        max_sim = sim
                        true_english = syn

            # Evaluate user answer
            correct = user_english == true_english
            typo = False

            # Typos: plurals
            # Allow missing or additional 's'
            # Some foreign words e.g. Swedish "djur" (animal/animals) are the same for singular/plural
            if (user_english == true_english+'s' or user_english+'s' == true_english):
                correct = True
                typo = True
            
            # Typos: typing error tolerance
            # Allow one accidental character insertion, deletion, substitution or transposition
            if jellyfish.damerau_levenshtein_distance(user_english, true_english) == 1:
                correct = True
                typo = True

            # Add result to list for response
            response_results.append({
                'translation_id': answer['translation_id'],
                'true_english': true_english,
                'correct': correct,
                'typo': typo,
            })

            # Prepare to create a new LearningTrace
            # Find previous LearningTrace object for this Translation
            prev = (request.user.traces
                .filter(translation=translation)
                .filter(translation__foreign_language = request.user.active_language.foreign_language)
                .last())
            if prev is None:
                continue  # next answer

            LearningTrace.objects.create(
                session = langy_session,
                user = request.user,
                # Tracing
                translation = translation,
                prev = prev,
                # Statistics
                seen = prev.seen + 1,
                interacted = prev.interacted,
                tested = prev.tested + 1,
                tested_correct = prev.tested_correct + 1 if correct else prev.tested_correct,
            )

        return JsonResponse({
            'results': response_results
        })

    else:
        return HttpResponseBadRequest('Invalid request method')


@login_required
def quit_test(request, langy_session_id):
    # Get, update and save LangySession
    langy_session = get_object_or_404(LangySession, pk=langy_session_id)
    if langy_session.end_time is None:
        langy_session.end_time = timezone.now()
        langy_session.save()

    return redirect(reverse('wordtest:info'))
