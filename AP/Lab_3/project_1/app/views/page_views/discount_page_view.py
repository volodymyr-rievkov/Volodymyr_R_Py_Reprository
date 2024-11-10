from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.repository_factory import RepositoryFactory
from django.db import OperationalError

class DiscountPageView(TemplateView):

    template_name = 'discounts.html'

    def get(self, request):
        repo = RepositoryFactory.discount_repo()
        discounts = repo.get_all()
        return render(request, self.template_name, {'discounts': discounts})
    
    def post(self, request):
        value = request.POST.get('value')

        if value:
            repo = RepositoryFactory.discount_repo()
            try:
                value_int = int(value)
                repo.create(value=value_int)
                return redirect('Discounts list')
            except OperationalError as e:
                return redirect('Discounts list')
        else:
            return redirect('Discounts list')
