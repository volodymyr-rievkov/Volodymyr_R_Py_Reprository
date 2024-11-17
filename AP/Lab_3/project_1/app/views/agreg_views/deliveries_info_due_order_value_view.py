from rest_framework.response import Response
from rest_framework.views import APIView
from app.repositories.delivery_repository import DeliveryRepository

class DelivsDueOrderView(APIView):
    def get(self, request):
        deliveries = DeliveryRepository.get_delivery_info_by_order_value_above()
        return Response(deliveries)
    