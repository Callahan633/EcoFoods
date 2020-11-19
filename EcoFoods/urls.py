from django.contrib import admin
from django.urls import path, include, re_path

from api.views import RegistrationAPIView, LoginAPIView, ProductAPIView, UpdateUserAPIView, HomePageAPIView, \
    MerchantProductsAPIView, CreateOrderAPIView, OrdersListAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    re_path(r'^api/registration/?$', RegistrationAPIView.as_view(), name='user_registration'),
    re_path(r'^api/login/?$', LoginAPIView.as_view(), name='user_login'),
    re_path(r'^api/merchant/add_product/?$', ProductAPIView.as_view(), name='merchant_add_product'),
    re_path(r'^api/update/?$', UpdateUserAPIView.as_view(), name='update_user'),
    re_path(r'^api/home/?$', HomePageAPIView.as_view({'get': 'retrieve'}), name='homepage'),
    re_path(r'^api/merchant/get_products', MerchantProductsAPIView.as_view({'get': 'retrieve'}),
            name='merchant_products'),
    re_path(r'^api/merchant/create_order', CreateOrderAPIView.as_view(), name='create_order'),
    re_path(r'^api/customer/get_orders', OrdersListAPIView.as_view(), name='customer_get_order_list'),
    
]
