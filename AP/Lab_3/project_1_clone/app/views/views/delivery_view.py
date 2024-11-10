from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from app.views.views.view_interface import IView
from app.repository_factory import RepositoryFactory
from app.serializers.delivery_serializer import DeliverySerializer

class DeliveryView(APIView, IView):
    
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.delivery_repo()

    def get(self, request):
        deliveries = self.repo.get_all()
        serializer = DeliverySerializer(deliveries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = DeliverySerializer(data=request.data)
        if (serializer.is_valid()):
            self.repo.create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 