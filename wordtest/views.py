from language.models import Translation
from tracking.models import LangySession, LearningTrace
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
import json


NUM_WORDS = 7


@login_required
def info(request):
    # Prepare error message based on user eligibility for test
    error_message = None

    if request.user.active_language is None:
        error_message = 'You have no active language!'
        
    else:
        foreign_language = request.user.active_language.foreign_language
        words_learnt = len(request.user.words_learnt(foreign_language))

        if words_learnt == 0:
            error_message = (
                f'You haven\'t learnt any words in {foreign_language.english_name} yet!<br>'
                f'You need to learn at least {NUM_WORDS} words to take a test.')

        elif words_learnt < NUM_WORDS:
            plural = 's' if words_learnt!=1 else ''
            error_message = (
                f'You have learnt {words_learnt} word{plural} in {foreign_language.english_name} so far.<br>'
                f'You need to learn at least {NUM_WORDS} words to take a test. {NUM_WORDS-words_learnt} more to go!')

    context = {
        'num_words': NUM_WORDS,
        'error_message': error_message,
    }
    return render(request, 'wordtest/info.html', context)


@login_required
def start_test(request):
    # User must have an active LearningLanguage to take a test
    if request.user.active_language is None:
        return redirect('users:select_a_language')

    # User must have learnt at least NUM_WORDS to take a test
    foreign_language = request.user.active_language.foreign_language
    if len(request.user.words_learnt(foreign_language)) < NUM_WORDS:
        return redirect('wordtest:info')

    langy_session_id = LangySession.objects.create(
        user = request.user,
        foreign_language = foreign_language,
        session_type = 'TEST',
    ).id

    return redirect(reverse('wordtest:test', args=[langy_session_id]))


@login_required
def test(request, langy_session_id):
    langy_session = get_object_or_404(LangySession, pk=langy_session_id)
    foreign_language = request.user.active_language.foreign_language

    # Use LearningTrace data to determine which words (Translation objects) to include in a test
    candidate_traces = request.user.traces_unique(foreign_language, ordering='oldest')

    # Prepare a total of NUM_WORDS Translations to test the user on
    # TODO intelligent selection... NAIVE selection here: just take the 7 oldest
    translations = [trace.translation for trace in candidate_traces]
    translations = translations[:NUM_WORDS]

    context = {
        'langy_session': langy_session,
        'translations': translations,
    }
    return render(request, 'wordtest/test.html', context)


@login_required
def quit_test(request, langy_session_id):
    # Get, update and save LangySession
    langy_session = get_object_or_404(LangySession, pk=langy_session_id)
    langy_session.end_time = timezone.now()
    langy_session.save()

    return redirect(reverse('wordtest:info'))
