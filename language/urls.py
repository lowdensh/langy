from . import views
from django.urls import path


app_name = 'language'
urlpatterns = [
    path('select', views.select, name='select'),
    path('set-active-language/<str:english_name>', views.set_active_language, name='set_active_language'),
    path('delete-learning-language/<str:english_name>', views.delete_learning_language, name='delete_learning_language'),
    path('translate', views.translation_page, name='translation_page'),
    path('translate/<int:book_id>', views.translation_page_book, name='translation_page_book'),
    path('translate-english-words/<str:key>', views.translate_english_words, name='translate_english_words'),
    path('save-translations/<str:key>', views.save_translations, name='save_translations'),
]
