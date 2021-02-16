from django.shortcuts import redirect


def empty_redirect(request):

    # User is logged in
    if request.user.is_authenticated:

        # No active LearningLanguage
        if request.user.active_language is None:
            return redirect('users:select_a_language')

        # Does have an active language :)
        return redirect('read:books')

    # Not yet logged in
    else:
        return redirect('login')
