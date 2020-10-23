import uuid
from datetime import datetime, timedelta

from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings

import jwt

from .utils import UUIDEncoder


class Image(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        if not email or not password:
            raise ValueError('User must provide an email and password')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar = models.ForeignKey(Image, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_merchant = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=255, blank=True)
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


class Chat(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    merchant = models.ForeignKey(User, on_delete=models.CASCADE)


class Message(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField
    send_date = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)


class Category(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)


class Product(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False)
    merchant = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2)


class Review(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rating = models.DecimalField(default=0, decimal_places=1, max_digits=2)
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    merchant = models.ForeignKey(User, on_delete=models.CASCADE)
    review_text = models.TextField


class Order(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, blank=False)  # @TODO: Make as ENUM, not CharField()
    created_at = models.DateTimeField(auto_now_add=True)


class ReviewImage(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)


class ProductImage(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)


class OrderItem(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    units = models.CharField(max_length=255, blank=False)  # @TODO: Make as ENUM, not CharField()


class ProductCategory(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)