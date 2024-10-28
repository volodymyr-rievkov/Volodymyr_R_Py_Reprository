from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from app.views.detail_views.detail_view_interface import IDetailView
from app.repository_factory import RepositoryFactory
from app.serializers.delivery_serializer import DeliverySerializer

class DeliveryDetailView(APIView, IDetailView):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.delivery_repo()

    def get(self, request, id):
        delivery = self.repo.get_by_id(id)
        if(not delivery):
            return Response(
                {"Error": "Delivery not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = DeliverySerializer(delivery)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        deilvery = self.repo.get_by_id(id)
        if (not deilvery):
            return Response(
                {"Error": "Delivery not found."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = DeliverySerializer(deilvery, data=request.data)
        if (serializer.is_valid()):
            updated_delivery = self.repo.update(
                deilvery,
                order_id=serializer.validated_data.get('order_id'),
                country=serializer.validated_data.get('country'),
                city=serializer.validated_data.get('city'),
                street=serializer.validated_data.get('street')
            )
            return Response(
                DeliverySerializer(updated_delivery).data, 
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    def delete(self, request, u_id):
        delivery = self.repo.get_by_id(u_id)
        if (not delivery):
            return Response(
                {"Error": "Delivery not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        delivery.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
