from django.urls import path

from . import views


app_name = 'read'
urlpatterns = [
    path('', views.view_books, name='view-books'),
    path('<int:book_id>/details', views.details, name='details'),
    path('<int:book_id>', views.read, name='read'),
]
