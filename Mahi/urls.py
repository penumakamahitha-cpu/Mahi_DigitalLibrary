"""
URL configuration for Digital Library & E-Book Circulation Portal.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('library.urls')),
]
