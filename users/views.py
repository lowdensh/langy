from users.admin import CustomUserCreationForm
from .models import CustomUser
from language.models import ForeignLanguage, LearningLanguage
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render


def sign_up(request):
    template = 'users/sign-up.html'

    # If the form has data, validate and submit
    # Display the same page with error messages if there are problems
    if request.POST:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            login(request, user)
            return redirect('read:my_books')
    # Otherwise, just display the form
    # This prevents error messages displaying on first form load where the user hasn't submitted anything yet
    else:
        form = CustomUserCreationForm()
        
    context = {
        'form': form
    }
        
    return render(request, template, context)


@login_required
def profile(request, id):
    template = 'users/profile.html'

    profile_user = get_object_or_404(CustomUser, pk=id)
    # The English name of the user's active learning language, if any
    active_language = next(
        (llang.foreign_language.english_name for llang in profile_user.learning.all() if llang.is_active==True),
        None
    )

    context = {
        'profile_user': profile_user,
        'learning_languages': profile_user.learning.all(),
        'active_language': active_language
    }
    return render(request, template, context)


@login_required
def select_a_language(request):
    template = 'users/select-a-language.html'

    # List of English names of languages the user is learning
    learning_languages = [
        llang.foreign_language.english_name for llang in request.user.learning.all()
    ]
    # The English name of the user's active learning language, if any
    active_language = next(
        (llang.foreign_language.english_name for llang in request.user.learning.all() if llang.is_active==True),
        None
    )

    context = {
        'foreign_languages': ForeignLanguage.objects.all(),
        'learning_languages': learning_languages,
        'active_language': active_language
    }
    return render(request, template, context)
