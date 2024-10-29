from app.repository_factory import RepositoryFactory
from app.views.report_view.report_view_interface import IReportView
from django.db.models import Avg, Max, Min, Count
from django.http import JsonResponse
from rest_framework.views import APIView

class ProductReportView(APIView, IReportView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.product_repo()

    def get(self, request):
        report = self.repo.get_all().aggregate(
            products_amount=Count('id'),
            average_price=Avg('price'),
            max_price=Max('price'),
            min_price=Min('price')
        )
        return JsonResponse(report, safe=False)
    