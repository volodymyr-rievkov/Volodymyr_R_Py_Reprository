from app.repository_factory import RepositoryFactory
from app.views.report_view.report_view_interface import IReportView
from django.db.models import Avg, Max, Min, Count
from django.http import JsonResponse
from rest_framework.views import APIView

class DiscountReportView(APIView, IReportView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.discount_repo()

    def get(self, request):
        report = self.repo.get_all().aggregate(
            discounts_amount=Count('id'),
            average_discount=Avg('value'),
            max_discount=Max('value'),
            min_discount=Min('value')
        )
        return JsonResponse(report, safe=False)
    