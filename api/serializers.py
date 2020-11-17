from django.contrib.auth import authenticate
from rest_framework import serializers


from .models import User, Product, Image, ProductImage


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('uuid', 'name', 'is_featured', 'price', 'units')

    def create(self, validated_data):
        user = self.context['request'].user
        image_url = self.context['request'].data['img']
        image = Image.objects.create_image(image_url)
        product = Product.objects.create_product_from_merchant(user, **validated_data)
        ProductImage.objects.create_link(image, product)
        return product


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('uuid', 'url')


class ProductImageSerializer(serializers.ModelSerializer):
    image = ImageSerializer()

    class Meta:
        model = ProductImage
        fields = ('image',)


class ProductSerializerForMerchant(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    @staticmethod
    def get_images(obj):
        image = ProductImage.objects.filter(product=obj)
        return ProductImageSerializer(image, many=True).data

    class Meta:
        model = Product
        fields = ('uuid', 'name', 'is_featured', 'price', 'units', 'description', 'images')


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('address', )


class HomeViewSerializer(serializers.ModelSerializer):
    merchant = AddressSerializer()

    class Meta:
        model = Product
        fields = ('uuid', 'name', 'is_featured', 'price', 'units', 'merchant')


class UpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('uuid', 'is_merchant', 'first_name', 'last_name', 'address', 'phone_number')


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
