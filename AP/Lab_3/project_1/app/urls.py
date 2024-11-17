from django.urls import path

from app.views.page_views.general.home_page_view import HomePageView
from app.views.page_views.general.error_page_view import ErrorPageView
from app.views.page_views.general.aggreg_requests_view import AggregRequestView

from app.views.views.user_view import UserView
from app.views.detail_views.user_detail_view import UserDetailView
from app.views.page_views.user.user_page_view import UserPageView
from app.views.page_views.user.user_detail_page_view import UserDetailPageView
from app.views.page_views.user.user_page_view_nh import UserPageViewNH
from app.views.page_views.user.user_detail_page_view_nh import UserDetailPageViewNH

from app.views.views.product_view import ProductView
from app.views.detail_views.product_detail_view import ProductDetailView
from app.views.page_views.product.product_page_view import ProductPageView
from app.views.page_views.product.product_detail_page_view import ProductDetailPageView

from app.views.views.order_view import OrderView
from app.views.detail_views.order_detail_view import OrderDetailView
from app.views.page_views.order.order_page_view import OrderPageView
from app.views.page_views.order.order_detail_page_view import OrderDetailPageView


from app.views.views.discount_view import DiscountView
from app.views.detail_views.discount_detail_view import DiscountDetailView
from app.views.page_views.discount.discount_page_view import DiscountPageView
from app.views.page_views.discount.discount_detail_page_view import DiscountDetailPageView

from app.views.views.delivery_view import DeliveryView
from app.views.detail_views.delivery_detail_view import DeliveryDetailView
from app.views.page_views.delivery.delivery_page_view import DeliveryPageView
from app.views.page_views.delivery.deilvery_detail_page_view import DeliveryDetailPageView


from app.views.agreg_views.orders_with_revenue_over_view import OrdersWithRevenueOverView
from app.views.page_views.aggreg.orders_with_revenue_over_p_view import OrdersWithRevenueOverPView

from app.views.agreg_views.deliveries_info_due_order_value_view import DelivsDueOrderView
from app.views.page_views.aggreg.deliveries_info_due_order_value_p_view import DelivsDueOrderPView

from app.views.agreg_views.products_with_discount_above_view import ProdsWithDscntsView
from app.views.page_views.aggreg.products_with_discount_above_p_view import ProdsWithDscntsPView

from app.views.agreg_views.top_products_view import TopProdsView
from app.views.page_views.aggreg.top_products_p_view import TopProdsPView

from app.views.agreg_views.users_total_spent_view import UsersWithTotalView
from app.views.page_views.aggreg.users_total_spent_p_view import UsersWithTotalPView

from app.views.agreg_views.users_with_discount_above_view import UsersWithDscntAboveView
from app.views.page_views.aggreg.users_with_discount_above_p_view import UsersWithDscntAbovePView

from app.views.dashboard_views.delivery_dashboard_v1_view import DelivDashboardV1View
from app.views.dashboard_views.user_dashboard_v1_view import UserDashboardV1View


urlpatterns = [

    path('', HomePageView.as_view(), name='Home'),
    path('error/', ErrorPageView.as_view(), name="Error"),


    path('users_api/', UserView.as_view(), name='User api'),
    path('users_api/<int:id>/', UserDetailView.as_view(), name='User detail api'),
    path('users/', UserPageView.as_view(), name='Users list'),
    path('users/<int:id>/', UserDetailPageView.as_view(), name='User'),
    path('users_nh/', UserPageViewNH.as_view(), name='Users list nh'),
    path('users_nh/<int:id>/', UserDetailPageViewNH.as_view(), name='User nh'),


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


    path('aggreg_requests/', AggregRequestView.as_view(), name="Aggreg requests"),

    path('orders_revenue_over_api/', OrdersWithRevenueOverView.as_view(), name="Orders revenue over Api"),
    path('orders_revenue_over/', OrdersWithRevenueOverPView.as_view(), name="Orders revenue over"),

    path('deliveries_due_to_order_api/', DelivsDueOrderView.as_view(), name="Deliveries due to order Api"),
    path('deliveries_due_to_order/', DelivsDueOrderPView.as_view(), name="Deliveries due to order"),
    path('delivery_dashboard_v1', DelivDashboardV1View.as_view(), name="Delivery dashboard v1"),

    path('products_discount_above_api/', ProdsWithDscntsView.as_view(), name="Products discount above Api"),
    path('products_discount_above/', ProdsWithDscntsPView.as_view(), name="Products discount above"),

    path('top_products_api/', TopProdsView.as_view(), name="Top products Api"),
    path('top_products/', TopProdsPView.as_view(), name="Top products"),

    path('users_with_total_api/', UsersWithTotalView.as_view(), name="Users with total Api"),
    path('users_with_total/', UsersWithTotalPView.as_view(), name="Users with total"),

    path('user_with_discount_api/', UsersWithDscntAboveView.as_view(), name="Users with discount Api"),
    path('user_with_discount/', UsersWithDscntAbovePView.as_view(), name="Users with discount"),
    path('user_dashboard_v1/', UserDashboardV1View.as_view(), name='User dashboard v1'),
]


