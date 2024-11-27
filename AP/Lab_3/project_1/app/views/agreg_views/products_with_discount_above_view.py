from rest_framework.response import Response
from rest_framework.views import APIView
from app.repository_factory import RepositoryFactory
import pandas as pd

class ProdsWithDscntsView(APIView):
    def __init__(self):
        self.repo = RepositoryFactory.product_repo()


    def get(self, request):
        value = request.GET.get('value')
        value = int(value)
        products = self.repo.get_products_with_discount_above(value)
        df = pd.DataFrame(products)
        return Response(df.to_json(orient="split"))