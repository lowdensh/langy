from . import views
from django.urls import include, path


app_name = 'users'
urlpatterns = [
    path('sign-up', views.sign_up, name='sign_up'),
    path('profile/<int:id>', views.profile, name='profile'),
]
