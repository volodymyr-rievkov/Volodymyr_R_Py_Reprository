from rest_framework.response import Response
from rest_framework.views import APIView
from app.repository_factory import RepositoryFactory
import pandas as pd

class UsersWithTotalView(APIView):
    def __init__(self):
        self.repo = RepositoryFactory.order_repo()

    def get(self, request):
        users = self.repo.get_users_total_spent()
        df = pd.DataFrame(users)
        return Response(df.to_json(orient="split"))