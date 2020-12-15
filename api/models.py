import uuid
from datetime import datetime, timedelta

from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings

import jwt

from .utils import UUIDEncoder


class ImageManager(models.Manager):

    def create_image(self, url):
        image = self.model(
            url=url,
        )
        image.save(using=self._db)

        return image


class Image(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()

    objects = ImageManager()


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

    def set_status(self, is_merchant):
        user = self.model(
            is_merchant=is_merchant,
        )

        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # avatar = models.ForeignKey(Image, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_merchant = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=255, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    delivery_is_possible = models.BooleanField(default=False)

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


class ProductManager(models.Manager):

    def _create_product(self, user: User, **extra_fields):
        if not user:
            raise ValueError('User must be provided')

        product = self.model(
            merchant=user,
            **extra_fields,
        )

        product.save(using=self._db)

        return product

    def create_product_from_merchant(self, user: User, **extra_fields):
        return self._create_product(user, **extra_fields)


class ProductImageManager(models.Manager):

    def _create_image_product_link(self, image, product):
        product_image = self.model(
            product=product,
            image=image,
        )
        product_image.save(using=self._db)

        return product_image

    def create_link(self, image, product):
        return self._create_image_product_link(image, product)


class OrderManager(models.Manager):

    def create_order(self, user, status):
        order = self.model(
            user=user,
            status=status,
        )
        order.save(using=self._db)

        return order


class OrderItemManager(models.Manager):

    def create_order_product_link(self, order, product, quantity):
        order_item = self.model(
            order=order,
            product=product,
            quantity=quantity
        )
        order_item.save(using=self._db)

        return order_item


class DeliveryManager(models.Manager):

    def create_delivery(self, order, **extra_fields):
        delivery = self.model(
            order=order,
            **extra_fields,
        )
        delivery.save(using=self._db)

        return delivery


class Chat(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')
    merchant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor')


class Message(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
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
    is_featured = models.BooleanField(default=False)
    merchant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='merchant')
    price = models.DecimalField(max_digits=9, decimal_places=2)
    description = models.TextField()
    units = models.CharField(max_length=255, blank=False)  # TODO: Make as ENUM, not CharField()

    objects = ProductManager()


class Review(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rating = models.DecimalField(default=0, decimal_places=1, max_digits=2)
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    merchant = models.ForeignKey(User, on_delete=models.CASCADE)
    review_text = models.TextField()


class Order(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, blank=False)  # TODO: Make as ENUM, not CharField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OrderManager()


class ReviewImage(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)


class ProductImage(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_from_image')
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='image')

    objects = ProductImageManager()


class OrderItem(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_from_order')
    quantity = models.IntegerField(default=0)

    objects = OrderItemManager()


class ProductCategory(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


def set_offset():
    return datetime.now() + timedelta(hours=4)


class Delivery(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    time_start = models.DateTimeField(default=datetime.now)
    time_end = models.DateTimeField(default=set_offset)
    district = models.CharField(max_length=255, blank=True)
    delivery_type = models.CharField(max_length=255, blank=False)  # TODO: Make as ENUM, not CharField()

    objects = DeliveryManager()
