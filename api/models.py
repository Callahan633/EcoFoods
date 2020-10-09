import uuid
from datetime import datetime, timedelta

from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings

import jwt

from .utils import UUIDEncoder


class UserManager(BaseUserManager):

    def _create_user(self, first_name, last_name, email, password, **extra_fields):
        if not (first_name or last_name or password):
            raise ValueError('User must have first name and last name and password')
        if not email:
            raise ValueError('User must provide an email')

        email = self.normalize_email(email)
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, first_name, last_name, email, password, **extra_fields):
        return self._create_user(first_name, last_name, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    email = models.EmailField(
        db_index=True,
        validators=[validators.validate_email],
        unique=True,
        blank=False
    )

    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ('username', )

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def token(self):
        return self._generate_jwt_token()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=30)

        token = jwt.encode({
            'id': self.uuid,
            'exp': int(dt.strftime('%s'))
        },
            settings.SECRET_KEY, algorithm='HS256',
            json_encoder=UUIDEncoder
        )

        return token.decode('utf-8')
