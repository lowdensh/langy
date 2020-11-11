from users.admin import CustomUserCreationForm
from .models import CustomUser
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render


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
            return redirect('langy:empty_redirect')
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
    context = {
        'user': get_object_or_404(CustomUser, pk=id)
    }
    return render(request, template, context)

# def learning_language(request):
#     pass

# def my_account(request):
#     pass
