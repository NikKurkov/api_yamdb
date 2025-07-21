# users/serializers.py
"""
Приложение api.
Сериализаторы для модели пользователя.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    """Принимает email и username, проверяет валидность."""
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(
        regex=r'^[\w.@+-]{1,150}$',
        max_length=150,
        required=True,
        error_messages={
            'invalid': 'Недопустимые символы в username.'
        },
    )

    def validate(self, attrs):
        """Разрешаем повторный запрос только если пара email/username совпадает."""
        email = attrs['email']
        username = attrs['username']

        user_qs = User.objects.filter(email=email) | User.objects.filter(username=username)
        if user_qs.exists():
            user = user_qs.first()
            if user.email != email or user.username != username:
                raise serializers.ValidationError(
                    'Пользователь с таким email или username уже существует.'
                )
        return attrs
