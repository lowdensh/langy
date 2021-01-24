from . import views
from django.urls import path


app_name = 'language'
urlpatterns = [
    path('translate', views.translation_page, name='translation_page'),
    path('translate/<int:book_id>', views.translation_page_book, name='translation_page_book'),
    path('translate-english-words/<str:key>', views.translate_english_words, name='translate_english_words'),
    path('save-translations/<str:key>', views.save_translations, name='save_translations'),
]
