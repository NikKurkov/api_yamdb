# users/views.py
"""
Приложение users отвечает за работу с пользователем:
регистрация, авторизация.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SignupSerializer

User = get_user_model()


class SignupView(APIView):
    """Создание (или повторный запрос) пользователя + отправка confirmation_code."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        # получаем или создаём пользователя
        user, _ = User.objects.get_or_create(email=email, username=username)

        # генерируем / обновляем код
        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save(update_fields=('confirmation_code',))

        # отправляем письмо (в консоль, если EMAIL_BACKEND так настроен)
        send_mail(
            subject='YaMDb confirmation code',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
