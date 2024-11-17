from rest_framework.response import Response
from rest_framework.views import APIView
from app.repositories.order_repository import OrderRepository

class TopProdsView(APIView):
    def get(self, request):
        products = OrderRepository.get_top_products()
        return Response(products)