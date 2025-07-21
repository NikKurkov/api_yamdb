# users/urls.py
"""
Приложение users отвечает за работу с пользователем:
регистрация, авторизация.
В urls.py прописаны url-адреса страниц, реализованных во views.py
и стандартных функций.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SignupView

app_name = 'users'


urlpatterns = [
    path('v1/auth/signup/', SignupView.as_view(), name='signup'),
]
