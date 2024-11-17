from rest_framework.response import Response
from rest_framework.views import APIView
from app.repositories.order_repository import OrderRepository

class OrdersWithRevenueOverView(APIView):
    def get(self, request):
        orders = OrderRepository.get_orders_with_revenue_over()
        return Response(orders)
    