from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from app.views.view_interface import IView
from app.repository_factory import RepositoryFactory
from app.serializers.delivery_serializer import DeliverySerializer

class DeliveryView(APIView, IView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.delivery_repo()

    def get(self, request, d_id=None):
        if (d_id):
            delivery = self.repo.get_by_id(d_id)
            if (delivery):
                serializer = DeliverySerializer(delivery)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"Error": "Delivery not found"}, status=status.HTTP_404_NOT_FOUND)
        deliveries = self.repo.show_all()
        serializer = DeliverySerializer(deliveries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = DeliverySerializer(data=request.data)
        if (serializer.is_valid()):
            self.repo.create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, d_id):
        delivery = self.repo.get_by_id(d_id)
        if (not delivery):
            return Response({"Error": "Delivery not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = DeliverySerializer(delivery, data=request.data)
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, d_id):
        delivery = self.repo.get_by_id(d_id)
        if (not delivery):
            return Response({"Error": "Delivery not found"}, status=status.HTTP_404_NOT_FOUND)
        delivery.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
   