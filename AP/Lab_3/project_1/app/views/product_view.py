from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from app.views.view_interface import IView
from app.repository_factory import RepositoryFactory
from app.serializers.product_serializer import ProductSerializer

class ProductView(APIView, IView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.product_repo()

    def get(self, request, p_id=None):
        if (p_id):
            product = self.repo.get_by_id(p_id)
            if (product):
                serializer = ProductSerializer(product)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"Error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        products = self.repo.show_all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if (serializer.is_valid()):
            self.repo.create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, p_id):
        product = self.repo.get_by_id(p_id)
        if (not product):
            return Response({"Error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data)
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, p_id):
        product = self.repo.get_by_id(p_id)
        if (not product):
            return Response({"Error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
   