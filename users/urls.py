from . import views
from django.urls import include, path


app_name = 'users'
urlpatterns = [
    path('sign-up', views.sign_up, name='sign_up'),
    path('profile/<int:id>', views.profile, name='profile'),
    path('set-active-language/<str:english_name>', views.set_active_language, name='set_active_language'),
    path('delete-learning-language/<str:english_name>', views.delete_learning_language, name='delete_learning_language'),
]
