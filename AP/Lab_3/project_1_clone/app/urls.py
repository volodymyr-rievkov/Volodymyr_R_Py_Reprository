from django.urls import path

from app.views.page_views.home_page_view import HomePageView
from app.views.page_views.user_page_view import UserPageView
from app.views.page_views.user_detail_page_view import UserDetailPageView
from app.views.page_views.product_page_view import ProductPageView
from app.views.page_views.product_detail_page_view import ProductDetailPageView
from app.views.page_views.order_page_view import OrderPageView
from app.views.page_views.order_detail_page_view import OrderDetailPageView
from app.views.page_views.discount_page_view import DiscountPageView
from app.views.page_views.discount_detail_page_view import DiscountDetailPageView
from app.views.page_views.delivery_page_view import DeliveryPageView
from app.views.page_views.deilvery_detail_page_view import DeliveryDetailPageView



urlpatterns = [

    path('', HomePageView.as_view(), name='Home'),

    path('users/', UserPageView.as_view(), name='Users list'),
    path('users/<int:id>/', UserDetailPageView.as_view(), name='User'),

    path('products/', ProductPageView.as_view(), name='Products list'),  
    path('products/<int:id>/', ProductDetailPageView.as_view(), name='Product'),


    path('orders/', OrderPageView.as_view(), name='Orders list'),  
    path('orders/<int:id>/', OrderDetailPageView.as_view(), name='Order'),

    path('discounts/', DiscountPageView.as_view(), name='Discounts list'),
    path('discounts/<int:id>/', DiscountDetailPageView.as_view(), name='Discount'),

    path('deliveries/', DeliveryPageView.as_view(), name='Deliveries list'),
    path('deliveries/<int:id>/', DeliveryDetailPageView.as_view(), name='Delivery'),
]
