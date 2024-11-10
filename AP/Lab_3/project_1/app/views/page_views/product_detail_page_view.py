from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from app.repository_factory import RepositoryFactory
from django.http import Http404

class ProductDetailPageView(TemplateView):
    
    template_name = 'product_detail.html'

    def __init__(self):
        self.repo = RepositoryFactory.product_repo()

    def get(self, request, id):
        product = self.repo.get_by_id(id)
        if (not product):
            raise Http404("Error: Product not found.")
        return render(request, self.template_name, {'product': product})
    
    def post(self, request, id):
        product = self.repo.get_by_id(id)
        if not product:
            raise Http404("Error: Product not found.")
        
        if ('_method' in request.POST and request.POST['_method'] == 'DELETE'):
            return self.delete(request, product)
        
        return self.edit(request, product)

    def edit(self, request, product):
        name = request.POST.get('name')
        info = request.POST.get('info')
        price = request.POST.get('price')
        amount = request.POST.get('amount')
        discount_id = request.POST.get('discount')

        self.repo.update(product, name=name, info=info, price=price, amount=amount, discount_id=discount_id)
        return redirect(reverse('Product', args=[product.id]))

    def delete(self, request, product):
        product.delete()
        return redirect(reverse('Products list'))
