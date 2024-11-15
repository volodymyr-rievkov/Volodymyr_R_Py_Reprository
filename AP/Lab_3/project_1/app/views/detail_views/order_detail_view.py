from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from app.views.detail_views.detail_view_interface import IDetailView
from app.repository_factory import RepositoryFactory
from app.serializers.order_serializer import OrderSerializer

class OrderDetailView(APIView, IDetailView):
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.order_repo()

    def get(self, request, id):
        order = self.repo.get_by_id(id)
        if(not order):
            return Response(
                {"Error": "Order not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        order = self.repo.get_by_id(id)
        if (not order):
            return Response(
                {"Error": "Order not found."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = OrderSerializer(order, data=request.data)
        if (serializer.is_valid()):
            updated_order = self.repo.update(
                order,
                user=serializer.validated_data.get('user_id'),
                product=serializer.validated_data.get('product_id'),
                amount=serializer.validated_data.get('amount'),
                comment=serializer.validated_data.get('comment')
            )
            return Response(
                OrderSerializer(updated_order).data, 
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    def delete(self, request, id):
        order = self.repo.get_by_id(id)
        if (not order):
            return Response(
                {"Error": "Order not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
