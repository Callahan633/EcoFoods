from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from .serializers import LoginSerializer, RegistrationSerializer, ProductSerializer,\
    UpdateUserSerializer, HomeViewSerializer, ProductSerializerForMerchant, OrderOverallSerializer, OrderSerializer
from .models import Product, Order


class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'token': serializer.data.get('token', None),
            },
            status=status.HTTP_201_CREATED,
        )


class UpdateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer

    def patch(self, request):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def post(self, request):
        order_serializer = self.serializer_class(context={'request': request}, data=request.data)
        order_serializer.is_valid(raise_exception=True)
        order_serializer.save()

        return Response(
            {
                'order_id': order_serializer.data.get('uuid'),
                'order_date': order_serializer.data.get('created_at')
            },
            status=status.HTTP_201_CREATED
        )


class OrdersListAPIView(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderOverallSerializer
    order_queryset = Order.objects.all()

    def retrieve(self, request):
        user_orders = self.order_queryset.filter(user=self.request.user)
        order_serializer = self.serializer_class(context={'request': request}, data=user_orders, many=True)
        # order_serializer.is_valid(raise_exception=True)
        return Response(
            order_serializer.data,
            status=status.HTTP_200_OK
        )


class MerchantProductsAPIView(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializerForMerchant

    def retrieve(self, request):
        products = Product.objects.all().filter(merchant=self.request.user)
        product_serializer = self.serializer_class(products, many=True)
        return Response(
            product_serializer.data,
            status=status.HTTP_200_OK
        )


class HomePageAPIView(ViewSet):
    product_queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = HomeViewSerializer

    def retrieve(self, request):
        res_dict = {}
        announcements = self.product_queryset
        announcements_serializer = self.serializer_class(announcements, many=True)
        advertisings = self.product_queryset.filter(is_featured=True)
        advertisings_serializer = self.serializer_class(advertisings, many=True)
        res_dict['announcements'] = announcements_serializer.data
        res_dict['advertisings'] = advertisings_serializer.data
        return Response(
            res_dict,
            status=status.HTTP_200_OK
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def post(self, request):
        product_serializer = self.serializer_class(context={'request': request}, data=request.data)
        product_serializer.is_valid(raise_exception=True)
        product_serializer.save()

        return Response(
            {
                'product': product_serializer.data.get('name'),
                'price': product_serializer.data.get('price')
            },
            status=status.HTTP_201_CREATED,
        )
