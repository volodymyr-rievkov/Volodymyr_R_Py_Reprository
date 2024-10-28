from django.urls import path, include

from app.views.user_view import UserView
from app.views.product_view import ProductView
from app.views.order_view import OrderView
from app.views.discount_view import DiscountView
from app.views.delivery_view import DeliveryView

from app.views.detail_views.user_detail_view import UserDetailView
from app.views.detail_views.product_detail_view import ProductDetailView
from app.views.detail_views.order_detail_view import OrderDetailView
from app.views.detail_views.discount_detail_view import DiscountDetailView
from app.views.detail_views.delivery_detail_view import DeliveryDetailView

urlpatterns = [

    path('users/', UserView.as_view(), name='User list'),
    path('users/<int:id>/', UserDetailView.as_view(), name='User'),

    path('products/', ProductView.as_view(), name='Product list'),  
    path('products/<int:id>/', ProductDetailView.as_view(), name='Product'),  

    path('orders/', OrderView.as_view(), name='Order list'),  
    path('orders/<int:id>/', OrderDetailView.as_view(), name='Order'),

    path('discounts/', DiscountView.as_view(), name='Discount list'),
    path('discounts/<int:id>/', DiscountDetailView.as_view(), name='Discount'),

    path('deliveries/', DeliveryView.as_view(), name='Delivery list'),
    path('deliveries/<int:id>/', DeliveryDetailView.as_view(), name='Delivery'),
]
