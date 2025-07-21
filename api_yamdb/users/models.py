# users/models.py
"""
Модель кастомного пользователя для YaMDb.
Авторизация идёт по email; username остаётся обязательным полем.
Роли: user / moderator / admin.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'


ROLE_CHOICES = [
    (USER, 'user'),
    (MODERATOR, 'moderator'),
    (ADMIN, 'admin'),
]


class User(AbstractUser):
    # Авторизация по email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    email = models.EmailField('Электронная почта', unique=True)
    bio = models.CharField('Биография', max_length=100, blank=True)
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=64,
        blank=True,
        editable=False,
    )

    # ─── удобные свойства ──────────────────────────────────────────────
    @property
    def is_admin(self) -> bool:
        return self.role == ADMIN or self.is_staff or self.is_superuser

    @property
    def is_moderator(self) -> bool:
        return self.role == MODERATOR

    # ─── методы ────────────────────────────────────────────────────────
    def set_confirmation_code(self) -> None:
        """Сгенерировать новый confirmation_code и сохранить."""
        self.confirmation_code = uuid.uuid4().hex
        self.save(update_fields=('confirmation_code',))

    class Meta(AbstractUser.Meta):
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username