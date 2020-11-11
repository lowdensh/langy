from . import views
from django.urls import path


app_name = 'read'
urlpatterns = [
    path('my-books', views.my_books, name='my_books'),
    path('book-details/<int:book_id>', views.book_details, name='book_details'),
    # wip read functionality. change this in views.py too
    path('1', views.read_wip, name='read_wip'),
    path('<int:book_id>', views.read, name='read'),
]
