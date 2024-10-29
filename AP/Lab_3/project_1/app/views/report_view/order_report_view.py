from app.repository_factory import RepositoryFactory
from app.views.report_view.report_view_interface import IReportView
from django.db.models import Sum, Avg, Max, Min, Count
from django.http import JsonResponse
from rest_framework.views import APIView

class OrderReportView(APIView, IReportView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.order_repo()

    def get(self, request):
        report = self.repo.get_all().aggregate(
            orders_amount=Count('id'),
            overall_price=Sum('total_price'),
            average_price=Avg('total_price'),
            max_price=Max('total_price'),
            min_price=Min('total_price')
        )
        return JsonResponse(report, safe=False)
    