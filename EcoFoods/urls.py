from django.contrib import admin
from django.urls import path, include, re_path

from api.views import RegistrationAPIView, LoginAPIView, ProductAPIView, SetUserAsMerchantAPIView, HomePageAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    re_path(r'^registration/?$', RegistrationAPIView.as_view(), name='user_registration'),
    re_path(r'^login/?$', LoginAPIView.as_view(), name='user_login'),
    re_path(r'^merchant/add_product/?$', ProductAPIView.as_view(), name='merchant_add_product'),
    re_path(r'^api/set_status/?$', SetUserAsMerchantAPIView.as_view(), name='set_user_as_merchant'),
    re_path(r'^home/?$', HomePageAPIView.as_view({'get': 'retrieve'}), name='homepage'),
]
