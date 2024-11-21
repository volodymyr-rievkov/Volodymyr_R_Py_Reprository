from rest_framework.response import Response
from rest_framework.views import APIView
from app.repository_factory import RepositoryFactory
import pandas as pd

class TopProdsView(APIView):
    def __init__(self):
        self.repo = RepositoryFactory.order_repo()

    def get(self, request):
        products = self.repo.get_top_products()
        df = pd.DataFrame(products)
        return Response(df.to_json(orient="split"))