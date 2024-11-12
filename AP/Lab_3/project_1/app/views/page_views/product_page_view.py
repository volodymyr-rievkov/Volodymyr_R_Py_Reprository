from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.repository_factory import RepositoryFactory
from django.db import OperationalError

class ProductPageView(TemplateView):

    template_name = 'products.html'

    def __init__(self):
        self.repo = RepositoryFactory.product_repo()

    def get(self, request):
        products = self.repo.get_all()
        return render(request, self.template_name, {'products': products})
    
    def post(self, request):

        name = request.POST.get('name')
        info = request.POST.get('info')
        price = request.POST.get('price')
        amount = request.POST.get('amount')
        discount_id = request.POST.get('discount')
        if (name and price and amount):
            try:
                price = float(price)
            except ValueError:
                return redirect('Products list')  
            try:
                amount = int(amount)
            except ValueError:
                return redirect('Products list')  
            if discount_id:
                try:
                    discount_id = int(discount_id)
                except ValueError:
                    return redirect('Products list') 
            else:
                discount_id = None  
            try:
                self.repo.create(name=name, price=price, amount=amount, info=info, discount_id=discount_id)
                return redirect('Products list')
            except OperationalError as e:
                return redirect('Products list')  
        return redirect('Products list')
