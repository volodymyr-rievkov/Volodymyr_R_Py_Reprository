from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.repository_factory import RepositoryFactory
from django.db import OperationalError

class DeliveryPageView(TemplateView):

    template_name = 'deliveries.html'

    def __init__(self):
        self.repo = RepositoryFactory.delivery_repo()

    def get(self, request):
        deliveries = self.repo.get_all()
        return render(request, self.template_name, {'deliveries': deliveries})
    
    def post(self, request):

        order_id = request.POST.get('order_id')
        country = request.POST.get('country')
        city = request.POST.get('city')
        street = request.POST.get('street')

        if(order_id and country and city and street):
            try:
                self.repo.create(order_id=order_id, country=country, city=city, street=street)
                return redirect('Deliveries list')
            except OperationalError as e:
                return redirect('Deliveries list')
        return redirect('Deliveries list')