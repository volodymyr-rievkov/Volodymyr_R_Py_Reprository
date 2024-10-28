from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from app.views.view_interface import IView
from app.repository_factory import RepositoryFactory
from app.serializers.order_serializer import OrderSerializer

class OrderView(APIView, IView):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.order_repo()

    def get(self, request):
        orders = self.repo.get_all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if (serializer.is_valid()):
            self.repo.create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
