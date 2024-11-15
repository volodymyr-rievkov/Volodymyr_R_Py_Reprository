from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from app.views.detail_views.detail_view_interface import IDetailView
from app.repository_factory import RepositoryFactory
from app.serializers.product_serializer import ProductSerializer

class ProductDetailView(APIView, IDetailView):
    
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.product_repo()

    def get(self, request, id):
        product = self.repo.get_by_id(id)
        if(not product):
            return Response(
                {"Error": "Product not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        product = self.repo.get_by_id(id)
        if (not product):
            return Response(
                {"Error": "Product not found."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ProductSerializer(product, data=request.data)
        if (serializer.is_valid()):
            updated_product = self.repo.update(
                product,
                name=serializer.validated_data.get('name'),
                price=serializer.validated_data.get('price'),
                amount=serializer.validated_data.get('amount'),
                info=serializer.validated_data.get('info'),
                discount_id=serializer.validated_data.get('discount_id')
            )
            return Response(
                ProductSerializer(updated_product).data, 
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    def delete(self, request, id):
        product = self.repo.get_by_id(id)
        if (not product):
            return Response(
                {"Error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
