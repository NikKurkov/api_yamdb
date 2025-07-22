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
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignupSerializer, TokenObtainSerializer, UserSerializer
from api.permissions import IsAdmin

User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)          # ← остаётся для остальных методов
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'email')
    lookup_field = 'username'

    # ─────────  /users/me/  ─────────
    @action(
        detail=False,                # /users/me/ (без PK)
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """
        GET  /users/me/    – вернуть свой профиль
        PATCH /users/me/   – частично изменить (кроме role)
        """
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        # PATCH
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        # запрещаем менять роль обычным пользователям
        if not user.is_admin and 'role' in serializer.validated_data:
            serializer.validated_data.pop('role')

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignupView(APIView):
    """POST /auth/signup/ – регистрация или повторная выдача confirmation_code."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        # создаём или получаем пользователя
        user, _ = User.objects.get_or_create(email=email, username=username)

        # генерируем новый код (если каждый раз нужен новый)
        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save(update_fields=('confirmation_code',))

        # «Отправляем» письмо – у нас backend выводит в консоль
        send_mail(
            subject='YaMDb confirmation code',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    """POST /auth/token/ – выдаёт JWT, если confirmation_code верный."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        code = serializer.validated_data['confirmation_code']

        user = get_object_or_404(User, username=username)

        if user.confirmation_code != code:
            # код не совпал – 400
            return Response(
                {'confirmation_code': 'Неверный код подтверждения.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # генерируем access‑токен (refresh не требуется по ТЗ)
        access = RefreshToken.for_user(user).access_token
        return Response({'token': str(access)}, status=status.HTTP_200_OK)
