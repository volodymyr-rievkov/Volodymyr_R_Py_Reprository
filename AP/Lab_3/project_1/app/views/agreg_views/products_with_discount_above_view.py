from rest_framework.response import Response
from rest_framework.views import APIView
from app.repositories.product_repository import ProductRepository
from app.serializers.product_serializer import ProductSerializer

class ProdsWithDscntsView(APIView):
    def get(self, request):
        products = ProductRepository.get_products_with_discount_above()
        return Response(ProductSerializer(products, many=True).data)