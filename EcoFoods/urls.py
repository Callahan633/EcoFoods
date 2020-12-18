from django.contrib import admin
from django.urls import path, include, re_path

from api.views import RegistrationAPIView, LoginAPIView, ProductAPIView, UpdateUserAPIView, HomePageAPIView, \
    MerchantProductsAPIView, CreateOrderAPIView, OrdersListAPIView, CreateDeliveryAPIView, UpdateOrderStatusAPIView,\
    UpdateDeliveryStatusAPIView, AddProductToOrderAPIView, GetUserInfoAPIView, SearchProductAPIView, GetDeliveryAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    re_path(r'^api/registration/?$', RegistrationAPIView.as_view(), name='user_registration'),
    re_path(r'^api/login/?$', LoginAPIView.as_view(), name='user_login'),
    re_path(r'^api/merchant/add_product/?$', ProductAPIView.as_view(), name='merchant_add_product'),
    re_path(r'^api/update_user_info/?$', UpdateUserAPIView.as_view(), name='update_user'),
    re_path(r'^api/get_user_info/?$', GetUserInfoAPIView.as_view(), name='get_current_user_info'),
    re_path(r'^api/home/?$', HomePageAPIView.as_view({'get': 'retrieve'}), name='homepage'),
    re_path(r'^api/merchant/get_products/?$', MerchantProductsAPIView.as_view({'get': 'retrieve'}),
            name='merchant_products'),
    re_path(r'^api/create_order/?$', CreateOrderAPIView.as_view(), name='create_order'),
    re_path(r'^api/get_orders/?$', OrdersListAPIView.as_view({'get': 'retrieve'}), name='customer_get_order_list'),
    re_path(r'^api/create_delivery/?$', CreateDeliveryAPIView.as_view(), name='create_delivery'),
    re_path(r'^api/update_delivery/?$', UpdateDeliveryStatusAPIView.as_view(), name='update_delivery_status'),
    re_path(r'^api/update_order_status/?$', UpdateOrderStatusAPIView.as_view(), name='update_order_status'),
    re_path(r'^api/add_product_to_order/?$', AddProductToOrderAPIView.as_view(), name='update_cart'),
    re_path(r'^api/search_product/?$', SearchProductAPIView.as_view(), name='search_by_product_name'),
    re_path(r'^api/get_delivery/?$', GetDeliveryAPIView.as_view({'get': 'retrieve'}), name='get_delivery_by_order_uuid'),
]
