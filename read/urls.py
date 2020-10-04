from django.urls import path

from . import views


app_name = 'read'
urlpatterns = [
    path('', views.view_books, name='view-books'),
    path('<int:book_id>/details', views.details, name='details'),

    # wip read functionality
    # change this in views.py too
    path('1', views.read_wip, name='read-wip'),

    path('<int:book_id>', views.read, name='read'),
]
