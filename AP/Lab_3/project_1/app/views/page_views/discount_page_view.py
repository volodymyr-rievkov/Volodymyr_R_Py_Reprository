from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.repository_factory import RepositoryFactory
from django.db import OperationalError

class DiscountPageView(TemplateView):

    template_name = 'discounts.html'

    def __init__(self):
        self.repo = RepositoryFactory.discount_repo()

    def get(self, request):
        discounts = self.repo.get_all()
        return render(request, self.template_name, {'discounts': discounts})
    
    def post(self, request):
        value = request.POST.get('value')

        if value:
            try:
                value_int = int(value)
                self.repo.create(value=value_int)
                return redirect('Discounts list')
            except OperationalError as e:
                return redirect('Discounts list')
        else:
            return redirect('Discounts list')
