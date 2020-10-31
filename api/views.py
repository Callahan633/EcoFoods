from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegistrationSerializer, ProductSerializer


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

        return Response(
            {
                'product': product_serializer.data.get('name'),
                'price': product_serializer.data.get('price')
            },
            status=status.HTTP_201_CREATED,
        )
