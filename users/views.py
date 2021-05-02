from users.admin import CustomUserCreationForm
from .models import CustomUser
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render


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
    # This prevents error messages displaying on first form load where the
    # user hasn't submitted anything yet
    else: form = CustomUserCreationForm()
        
    return render(request, 'users/sign-up.html', {'form': form})


@login_required
def profile(request, id):
    profile_user = get_object_or_404(CustomUser, pk=id) 
    context = {
        'profile_user': profile_user,
        'learning_languages': profile_user.learning_languages.all(),
        'active_language': profile_user.active_language
    }
    return render(request, 'users/profile.html', context)
