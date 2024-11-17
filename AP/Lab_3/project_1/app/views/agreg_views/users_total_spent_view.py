from rest_framework.response import Response
from rest_framework.views import APIView
from app.repositories.order_repository import OrderRepository

class UsersWithTotalView(APIView):
    def get(self, request):
        users = OrderRepository.get_users_total_spent()
        return Response(users)