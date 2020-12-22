from . import views
from django.urls import path


app_name = 'read'
urlpatterns = [
    path('my-books', views.my_books, name='my_books'),
    path('<int:book_id>/details', views.details, name='details'),
    path('<int:book_id>/pages/manage', views.pages_manage, name='pages_manage'),
    path('<int:book_id>/pages/upload-pdf', views.pages_upload_pdf, name='pages_upload_pdf'),
    path('<int:book_id>/pages/generate', views.pages_generate, name='pages_generate'),
    path('<int:book_id>/pages/save', views.pages_save, name='pages_save'),

    # wip read functionality. change this in views.py too
    path('1', views.read_wip, name='read_wip'),
    path('<int:book_id>', views.read, name='read'),
]
