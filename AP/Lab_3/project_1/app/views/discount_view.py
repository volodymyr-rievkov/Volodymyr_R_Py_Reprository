from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from app.views.view_interface import IView
from app.repository_factory import RepositoryFactory
from app.serializers.discount_serializer import DiscountSerializer

class DiscountView(APIView, IView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.discount_repo()

    def get(self, request, d_id=None):
        if (d_id):
            discount = self.repo.get_by_id(d_id)
            if (discount):
                serializer = DiscountSerializer(discount)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"Error": "Discount not found"}, status=status.HTTP_404_NOT_FOUND)
        discounts = self.repo.show_all()
        serializer = DiscountSerializer(discounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = DiscountSerializer(data=request.data)
        if (serializer.is_valid()):
            self.repo.create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, d_id):
        discount = self.repo.get_by_id(d_id)
        if (not discount):
            return Response({"Error": "Discount not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = DiscountSerializer(discount, data=request.data)
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, d_id):
        discount = self.repo.get_by_id(d_id)
        if (not discount):
            return Response({"Error": "Discount not found"}, status=status.HTTP_404_NOT_FOUND)
        discount.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
   