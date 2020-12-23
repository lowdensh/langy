from django.shortcuts import redirect


def empty_redirect(request):
    if request.user.is_authenticated:
        return redirect('read:my_books')
    else:
        return redirect('login')
