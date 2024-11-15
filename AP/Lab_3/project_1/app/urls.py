from django.urls import path

from app.views.page_views.home_page_view import HomePageView
from app.views.page_views.error_page_view import ErrorPageView

from app.views.views.user_view import UserView
from app.views.detail_views.user_detail_view import UserDetailView
from app.views.page_views.user_page_view import UserPageView
from app.views.page_views.user_detail_page_view import UserDetailPageView

from app.views.views.product_view import ProductView
from app.views.detail_views.product_detail_view import ProductDetailView
from app.views.page_views.product_page_view import ProductPageView
from app.views.page_views.product_detail_page_view import ProductDetailPageView

from app.views.views.order_view import OrderView
from app.views.detail_views.order_detail_view import OrderDetailView
from app.views.page_views.order_page_view import OrderPageView
from app.views.page_views.order_detail_page_view import OrderDetailPageView

from app.views.views.discount_view import DiscountView
from app.views.detail_views.discount_detail_view import DiscountDetailView
from app.views.page_views.discount_page_view import DiscountPageView
from app.views.page_views.discount_detail_page_view import DiscountDetailPageView

from app.views.views.delivery_view import DeliveryView
from app.views.detail_views.delivery_detail_view import DeliveryDetailView
from app.views.page_views.delivery_page_view import DeliveryPageView
from app.views.page_views.deilvery_detail_page_view import DeliveryDetailPageView

from app.views.page_views.user_page_view_nh import UserPageViewNH
from app.views.page_views.user_detail_page_view_nh import UserDetailPageViewNH

urlpatterns = [

    path('', HomePageView.as_view(), name='Home'),
    path('error/', ErrorPageView.as_view(), name="Error"),

    path('users_api/', UserView.as_view(), name='User api'),
    path('users_api/<int:id>/', UserDetailView.as_view(), name='User detail api'),

    path('users/', UserPageView.as_view(), name='Users list'),
    path('users/<int:id>/', UserDetailPageView.as_view(), name='User'),


    path('products_api/', ProductView.as_view(), name='Product api'),
    path('products_api/<int:id>/', ProductDetailView.as_view(), name='Product detail api'),
 
    path('products/', ProductPageView.as_view(), name='Products list'),  
    path('products/<int:id>/', ProductDetailPageView.as_view(), name='Product'),


    path('orders_api/', OrderView.as_view(), name='Order api'),
    path('orders_api/<int:id>/', OrderDetailView.as_view(), name='Order detail api'),
 
    path('orders/', OrderPageView.as_view(), name='Orders list'),  
    path('orders/<int:id>/', OrderDetailPageView.as_view(), name='Order'),


    path('discounts_api/', DiscountView.as_view(), name='Discount api'),
    path('discounts_api/<int:id>/', DiscountDetailView.as_view(), name='Discount detail api'), 

    path('discounts/', DiscountPageView.as_view(), name='Discounts list'),
    path('discounts/<int:id>/', DiscountDetailPageView.as_view(), name='Discount'),

    path('deliveries_api/', DeliveryView.as_view(), name='Deliveries api'),
    path('deliveries_api/<int:id>/', DeliveryDetailView.as_view(), name='Deliveries detail api'), 

    path('deliveries/', DeliveryPageView.as_view(), name='Deliveries list'),
    path('deliveries/<int:id>/', DeliveryDetailPageView.as_view(), name='Delivery'),

    path('users_nh/', UserPageViewNH.as_view(), name='Users list nh'),
    path('users_nh/<int:id>/', UserDetailPageViewNH.as_view(), name='User nh')
]


