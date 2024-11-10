from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from app.views.detail_views.detail_view_interface import IDetailView
from app.repository_factory import RepositoryFactory
from app.serializers.discount_serializer import DiscountSerializer

class DiscountDetailView(APIView, IDetailView):
    
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.discount_repo()

    def get(self, request, id):
        discount = self.repo.get_by_id(id)
        if(not discount):
            return Response(
                {"Error": "Discount not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = DiscountSerializer(discount)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        discount = self.repo.get_by_id(id)
        if (not discount):
            return Response(
                {"Error": "Discount not found."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = DiscountSerializer(discount, data=request.data)
        if (serializer.is_valid()):
            updated_discount = self.repo.update(
                discount,
                value=serializer.validated_data.get('value')
            )
            return Response(
                DiscountSerializer(updated_discount).data, 
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    def delete(self, request, u_id):
        discount = self.repo.get_by_id(u_id)
        if (not discount):
            return Response(
                {"Error": "Discount not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        discount.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
