from . import views
from django.urls import path


app_name = 'language'
urlpatterns = [
    path('translate', views.translate_all_words, name='translate_all_words'),
    path('translate-english-words/<str:key>', views.translate_english_words, name='translate_english_words'),
    path('save-translations/<str:key>', views.save_translations, name='save_translations'),
]