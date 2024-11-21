from rest_framework.response import Response
from rest_framework.views import APIView
from app.repository_factory import RepositoryFactory
import pandas as pd

class DelivsDueOrderView(APIView):

    def __init__(self):
        self.repo = RepositoryFactory.delivery_repo()

    def get(self, request):
        deliveries = self.repo.get_delivery_info_by_order_value_above()
        df = pd.DataFrame(deliveries)
        return Response(df.to_json(orient="split"))
    