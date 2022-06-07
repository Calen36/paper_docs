"""ewnc_docs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.shortcuts import HttpResponse, redirect
from django.urls import path
from django.conf.urls.static import static
from letters.views import get_extended_letter_url, myscript
from ewnc_docs import settings


urlpatterns = [
    path('exec', myscript),
    path('admin/letters/baseletter/<path:tail>', get_extended_letter_url),
    path('admin/', admin.site.urls),
    path('', lambda _: redirect("admin/"))
]


if settings.DEBUG:
    urlpatterns = [
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns