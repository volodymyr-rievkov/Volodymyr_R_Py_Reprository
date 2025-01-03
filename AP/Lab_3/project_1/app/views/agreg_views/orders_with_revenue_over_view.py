from rest_framework.response import Response
from rest_framework.views import APIView
from app.repository_factory import RepositoryFactory
import pandas as pd

class OrdersWithRevenueOverView(APIView):
    def __init__(self):
        self.repo = RepositoryFactory.order_repo()

    def get(self, request):
        value = request.GET.get('value')
        value = int(value)
        orders = self.repo.get_orders_with_revenue_over(value)
        df = pd.DataFrame(orders)
        return Response(df.to_json(orient="split"))
    