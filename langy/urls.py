"""langy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


app_name = 'langy'
urlpatterns = [
    # Django
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Empty URL redirect
    path('', views.empty_redirect, name='empty_redirect'),

    # My apps
    path('users/', include('users.urls')),
    path('read/', include('read.urls')),
    path('test/', include('wordtest.urls')),
    path('language/', include('language.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
