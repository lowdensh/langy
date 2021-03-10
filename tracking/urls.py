from . import views
from django.urls import path


app_name = 'tracking'
urlpatterns = [
    path('add-learning-traces', views.add_learning_traces, name='add_learning_traces'),
]
