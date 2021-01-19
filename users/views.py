from users.admin import CustomUserCreationForm
from .models import CustomUser
from language.models import ForeignLanguage, LearningLanguage
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse


def sign_up(request):
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
        
    return render(request, 'users/sign-up.html', context)


@login_required
def profile(request, id):
    profile_user = get_object_or_404(CustomUser, pk=id)
    # The PROFILE user's active LearningLanguage
    active_language = next(
        (learning_language for learning_language in profile_user.learning.all() if learning_language.is_active==True),
        None
    )

    context = {
        'profile_user': profile_user,
        'learning_languages': profile_user.learning.all(),
        'active_language': active_language
    }
    return render(request, 'users/profile.html', context)


@login_required
def select_a_language(request):
    # The REQUEST user's active LearningLanguage
    active_language = next(
        (learning_language for learning_language in request.user.learning.all() if learning_language.is_active==True),
        None
    )

    context = {
        'foreign_languages': ForeignLanguage.objects.all(),
        'active_language': active_language
    }
    return render(request, 'users/select-a-language.html', context)


@login_required
def set_active_language(request, english_name):
    # The REQUEST user's active LearningLanguage
    active_language = next(
        (learning_language for learning_language in request.user.learning.all() if learning_language.is_active==True),
        None
    )

    # Deactivate the LearningLanguage, if there was one
    if active_language:
        active_language.is_active = False
        active_language.save()

    # Check for the requested language among the user's existing LearningLanguages
    new_language = next(
        (learning_language for learning_language in request.user.learning.all() if learning_language.foreign_language.english_name==english_name),
        None
    )

    if new_language:
        # Activate this LearningLanguage, if it existed
        new_language.is_active = True
    else:
        # Otherwise, create it
        new_language = LearningLanguage.objects.create(
            user = request.user,
            foreign_language = get_object_or_404(ForeignLanguage, english_name=english_name)
        )
    new_language.save()

    return redirect(reverse('users:profile', args=[request.user.id]))
