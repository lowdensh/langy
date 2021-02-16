from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required


NUM_WORDS = 7


@login_required
def info(request):
    # Prepare error message based on user eligibility for test
    error_message = None

    if request.user.active_language is None:
        error_message = 'You have no active language!'
        
    else:
        foreign_language = request.user.active_language.foreign_language
        learn_count = len(request.user.traces_unique_tid(foreign_language))

        if learn_count == 0:
            error_message = (
                f'You haven\'t learnt any words in {foreign_language.english_name} yet!<br>'
                f'You need to learn at least {NUM_WORDS} words to take a test.')

        elif learn_count < NUM_WORDS:
            plural = 's' if learn_count!=1 else ''
            error_message = (
                f'You have learnt {learn_count} word{plural} in {foreign_language.english_name} so far.<br>'
                f'You need to learn at least {NUM_WORDS} words to take a test. {NUM_WORDS-learn_count} more to go!')

    context = {
        'num_words': NUM_WORDS,
        'error_message': error_message,
    }
    return render(request, 'wordtest/info.html', context)


@login_required
def test(request):
    # User must have an active LearningLanguage to be able to take a test
    if request.user.active_language is None:
        return redirect('users:select_a_language')

    context = {}
    return render(request, 'wordtest/test.html', context)
