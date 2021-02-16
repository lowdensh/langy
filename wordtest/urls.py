from . import views
from django.urls import path


app_name = 'wordtest'
urlpatterns = [
    path('info', views.info, name='info'),
    path('test', views.test, name='test'),
]
