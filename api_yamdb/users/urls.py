# users/urls.py
"""
Приложение users отвечает за работу с пользователем:
регистрация, авторизация.
В urls.py прописаны url-адреса страниц, реализованных во views.py
и стандартных функций.
"""
from django.urls import path
from users.views import SignupView, TokenView

app_name = 'users'


urlpatterns = [
    path('v1/auth/signup/', SignupView.as_view(), name='signup'),
    path('v1/auth/token/',  TokenView.as_view(),  name='token'),
]
