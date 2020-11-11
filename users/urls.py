from . import views
from django.urls import include, path


app_name = 'users'
urlpatterns = [
    path('sign-up', views.sign_up, name='sign_up'),
    path('profile/<int:id>', views.profile, name='profile'),
    # path('settings', include([
    #     path('learning-language', views.learning_language, name='learning_language'),
    #     path('my-account', views.my_account, name='my_account'),
    # ])),
]
