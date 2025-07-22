# users/serializers.py
"""
Приложение api.
Сериализаторы для модели пользователя.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


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
        """
        • Если username или email занят чужим пользователем — возвращаем
          поле-ошибку в формате, который ждёт автотест.
        • Если пара принадлежит тому же пользователю — считаем корректным.
        """
        if attrs['username'] == 'me':
            raise serializers.ValidationError(
                {'Выберите другой username'})
    
        email = attrs['email']
        username = attrs['username']

        errors = {}

        # username занят другим email-ом
        if User.objects.filter(username=username).exclude(email=email).exists():
            errors['username'] = ['Пользователь с таким username уже существует.']

        # email занят другим username-ом
        if User.objects.filter(email=email).exclude(username=username).exists():
            errors['email'] = ['Пользователь с таким email уже существует.']

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class TokenObtainSerializer(serializers.Serializer):
    """Принимает username и confirmation_code, просто валидирует наличие полей."""
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(max_length=64, required=True)
