from . import views
from django.urls import path


app_name = 'wordtest'
urlpatterns = [
    path('info', views.info, name='info'),
    path('start-test', views.start_test, name='start_test'),
    path('<int:langy_session_id>/submit-answers', views.submit_answers, name='submit_answers'),
    path('<int:langy_session_id>/quit-test', views.quit_test, name='quit_test'),
    path('<int:langy_session_id>', views.test, name='test'),
]
