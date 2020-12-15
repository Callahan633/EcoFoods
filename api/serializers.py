from django.contrib.auth import authenticate
from rest_framework import serializers


from .models import User, Product, Image, ProductImage, Order, OrderItem, Delivery


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('address', 'first_name', 'last_name')


class ProductFromOrderSerializer(serializers.ModelSerializer):
    merchant = AddressSerializer()

    class Meta:
        model = Product
        fields = ('uuid', 'name', 'is_featured', 'price', 'units', 'description', 'merchant')


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('uuid', 'name', 'is_featured', 'price', 'units', 'description')

    def create(self, validated_data):
        user = self.context['request'].user
        image_url = self.context['request'].data['img']
        image = Image.objects.create_image(image_url)
        product = Product.objects.create_product_from_merchant(user, **validated_data)
        ProductImage.objects.create_link(image, product)
        return product


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductFromOrderSerializer()

    class Meta:
        model = OrderItem
        fields = ('quantity', 'product')


class UpdateOrderStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('uuid', 'status')


# class AddProductToOrderSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Order
#         fields = ('uuid', 'created_at')
#
#

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('uuid', 'created_at')

    def create(self, validated_data):
        user = self.context['request'].user
        status = "opened"
        product_uuid = self.context['request'].data['product_uuid']
        quantity = self.context['request'].data['quantity']
        product = Product.objects.get(uuid=product_uuid)
        order = Order.objects.create_order(user, status)
        OrderItem.objects.create_order_product_link(order, product, quantity)
        return order


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('uuid', 'url')


class ProductImageSerializer(serializers.ModelSerializer):
    image = ImageSerializer()

    class Meta:
        model = ProductImage
        fields = ('image', )


class ProductSerializerForMerchant(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    @staticmethod
    def get_images(obj):
        image = ProductImage.objects.filter(product=obj)
        return ProductImageSerializer(image, many=True).data

    class Meta:
        model = Product
        fields = ('uuid', 'name', 'is_featured', 'price', 'units', 'description', 'images')


class HomeViewSerializer(serializers.ModelSerializer):
    merchant = AddressSerializer()

    class Meta:
        model = Product
        fields = ('uuid', 'name', 'is_featured', 'price', 'units', 'merchant')


class UpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('uuid', 'is_merchant', 'first_name', 'last_name', 'address', 'phone_number')


class OrderOverallSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    @staticmethod
    def get_products(obj):
        product = OrderItem.objects.filter(order=obj)
        return OrderItemSerializer(product, many=True).data

    class Meta:
        model = Order
        fields = ('uuid', 'status', 'created_at', 'products')


class AddDeliverySerializer(serializers.ModelSerializer):

    # order = OrderSerializer()

    class Meta:
        model = Delivery
        fields = ('uuid', 'order', 'time_start', 'time_end', 'district', 'delivery_type')

    def create(self, validated_data):
        delivery = Delivery.objects.create_delivery(**validated_data)
        return delivery


class ChangeDeliverySerializer(serializers.ModelSerializer):

    class Meta:
        model = Delivery
        fields = ('uuid', 'time_start', 'time_end', 'delivery_type', 'district')


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
    )

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'token')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    username = serializers.CharField(max_length=255, read_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'token': user.token,
        }
