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
            return redirect('read:books')

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
    context = {
        'profile_user': profile_user,
        'learning_languages': profile_user.learning_languages.all(),
        'active_language': profile_user.active_language
    }
    return render(request, 'users/profile.html', context)


@login_required
def select_a_language(request):
    context = {
        'foreign_languages': ForeignLanguage.objects.all(),
        'active_language': request.user.active_language
    }
    return render(request, 'users/select-a-language.html', context)


@login_required
def set_active_language(request, english_name):
    active_language = request.user.active_language

    # Deactivate the user's active LearningLanguage, if they had one
    if active_language:
        active_language.is_active = False
        active_language.save()

    # Check for the requested language among the user's existing LearningLanguages
    new_language = request.user.learning_language(english_name)

    if new_language:
        # If this LearningLanguage exists, activate it
        new_language.is_active = True
    else:
        # Otherwise, create it
        new_language = LearningLanguage.objects.create(
            user = request.user,
            foreign_language = get_object_or_404(ForeignLanguage, english_name=english_name)
        )
    new_language.save()

    # Take the user to their profile
    return redirect(reverse('users:profile', args=[request.user.id]))


@login_required
def delete_learning_language(request, english_name):
    # Check for the requested language among the user's existing LearningLanguages
    delete_language = request.user.learning_language(english_name)

    # If this LearningLanguage exists, check active status and delete it
    was_active = False
    if delete_language:
        if delete_language.is_active:
            was_active = True
        delete_language.delete()
    
    # If an active LearningLanguage was deleted, activate another existing one if possible
    if was_active:
        learning_language = request.user.learning_languages.all().first()
        if learning_language:
            learning_language.is_active = True
            learning_language.save()

    # Take the user to their profile
    return redirect(reverse('users:profile', args=[request.user.id]))
