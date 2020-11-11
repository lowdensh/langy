from django.shortcuts import redirect


def empty_redirect(request):
    return redirect('read:my_books')
