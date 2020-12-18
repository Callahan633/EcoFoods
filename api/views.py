from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView

from .serializers import LoginSerializer, RegistrationSerializer, ProductSerializer,\
    UpdateUserSerializer, HomeViewSerializer, ProductSerializerForMerchant, OrderOverallSerializer, OrderSerializer,\
    AddDeliverySerializer, ChangeDeliverySerializer, UpdateOrderStatusSerializer, UserInfoSerializer, SearchProductSerializer
from .models import Product, Order, Delivery, OrderItem


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


class GetUserInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserInfoSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class GetDeliveryAPIView(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddDeliverySerializer
    delivery_queryset = Delivery.objects.all()

    # def post(self, request):
    #     delivery_object = self.delivery_queryset.get(order=request.data['order_uuid'])
    #     print(delivery_object)
    #     delivery_serializer = self.serializer_class(delivery_object)
    #     delivery_serializer.is_valid(raise_exception=True)
    #
    #     return Response(
    #         delivery_serializer.data,
    #         status=status.HTTP_200_OK
    #     )

    def retrieve(self, request):
        delivery_object = self.delivery_queryset.filter(order=request.data['order_uuid'])
        print(delivery_object)
        # product_serializer = self.serializer_class(products, context={'request': request}, many=True)
        delivery_serializer = self.serializer_class(delivery_object, many=True)
        delivery_serializer.is_valid(raise_exception=True)

        return Response(
            delivery_serializer.data,
            status=status.HTTP_200_OK
        )


class CreateDeliveryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddDeliverySerializer

    def post(self, request):
        delivery_serializer = self.serializer_class(context={'request': request}, data=request.data)
        delivery_serializer.is_valid(raise_exception=True)
        delivery_serializer.save()

        return Response(
            delivery_serializer.data,
            status=status.HTTP_201_CREATED
        )


class UpdateOrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateOrderStatusSerializer
    order_queryset = Order.objects.all()

    def patch(self, request):
        order_object = self.order_queryset.get(uuid=request.data['uuid'])
        serializer = self.serializer_class(order_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK
        )


class AddProductToOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    order_queryset = Order.objects.all()

    def patch(self, request):
        orders = self.order_queryset.filter(user=self.request.user)
        order_item = orders.get(uuid=self.request.data['order_uuid'])
        product_uuid = self.request.data['product_uuid']
        quantity = self.request.data['quantity']
        product = Product.objects.get(uuid=product_uuid)
        OrderItem.objects.create_order_product_link(order_item, product, quantity)
        updated_order = orders.get(uuid=self.request.data['order_uuid'])
        order = self.serializer_class(updated_order, data=request.data, partial=True)
        order.is_valid(raise_exception=True)

        return Response(
            order.validated_data,
            status=status.HTTP_200_OK
        )


class UpdateDeliveryStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeDeliverySerializer
    delivery_queryset = Delivery.objects.all()

    def patch(self, request):
        delivery_object = self.delivery_queryset.get(uuid=request.data['uuid'])
        serializer = self.serializer_class(delivery_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.validated_data,
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
        if self.request.user.is_merchant:
            user_orders = self.order_queryset\
                .filter(uuid__in=OrderItem.objects
                        .select_related('product')
                        .filter(product__merchant=self.request.user)
                        .values_list('order', flat=True)
                        .distinct())
        else:
            user_orders = self.order_queryset.filter(user=self.request.user)
        order_serializer = self.serializer_class(user_orders, many=True)
        return Response(
            order_serializer.data,
            status=status.HTTP_200_OK
        )


class MerchantProductsAPIView(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializerForMerchant

    def retrieve(self, request):
        products = Product.objects.all().filter(merchant=self.request.user)
        # product_serializer = self.serializer_class(products, context={'request': request}, many=True)
        product_serializer = self.serializer_class(products, many=True)

        return Response(
            product_serializer.data,
            status=status.HTTP_200_OK
        )


class SearchProductAPIView(ListCreateAPIView):
    search_fields = ['name']
    filter_backends = (SearchFilter,)
    serializer_class = SearchProductSerializer
    queryset = Product.objects.all()


class HomePageAPIView(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HomeViewSerializer

    def retrieve(self, request):
        product_queryset = Product.objects.all()
        res_dict = {}
        announcements = product_queryset
        announcements_serializer = self.serializer_class(announcements, many=True)
        advertisings = product_queryset.filter(is_featured=True)
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
