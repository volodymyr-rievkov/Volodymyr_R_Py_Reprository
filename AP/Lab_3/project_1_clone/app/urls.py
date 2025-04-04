from django.urls import path

from app.views.views.delivery_view import DeliveryView
from app.views.views.discount_view import DiscountView
from app.views.views.order_view import OrderView
from app.views.views.product_view import ProductView
from app.views.views.user_view import UserView

from app.views.detail_views.delivery_detail_view import DeliveryDetailView
from app.views.detail_views.discount_detail_view import DiscountDetailView
from app.views.detail_views.order_detail_view import OrderDetailView
from app.views.detail_views.product_detail_view import ProductDetailView
from app.views.detail_views.user_detail_view import UserDetailView

urlpatterns = [

    path('users/', UserView.as_view(), name='Users list'),
    path('users/<int:id>/', UserDetailView.as_view(), name='User'),

    path('products/', ProductView.as_view(), name='Products list'),  
    path('products/<int:id>/', ProductDetailView.as_view(), name='Product'),


    path('orders/', OrderView.as_view(), name='Orders list'),  
    path('orders/<int:id>/', OrderDetailView.as_view(), name='Order'),

    path('discounts/', DiscountView.as_view(), name='Discounts list'),
    path('discounts/<int:id>/', DiscountDetailView.as_view(), name='Discount'),

    path('deliveries/', DeliveryView.as_view(), name='Deliveries list'),
    path('deliveries/<int:id>/', DeliveryDetailView.as_view(), name='Delivery'),
]
