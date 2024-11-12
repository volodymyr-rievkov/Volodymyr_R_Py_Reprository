from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from app.repository_factory import RepositoryFactory
from django.http import Http404

class DiscountDetailPageView(TemplateView):
    
    template_name = 'discount_detail.html'

    def __init__(self):
        self.repo = RepositoryFactory.discount_repo()

    def get(self, request, id):
        discount = self.repo.get_by_id(id)
        if not discount:
            raise Http404("Error: Discount not found.")
        return render(request, self.template_name, {'discount': discount})

    def post(self, request, id):
        discount = self.repo.get_by_id(id)
        if not discount:
            raise Http404("Error: Discount not found.")
        
        if '_method' in request.POST and request.POST['_method'] == 'DELETE':
            return self.delete(request, discount)
        
        return self.edit(request, discount)

    def edit(self, request, discount):
        value = request.POST.get('value')

        self.repo.update(discount, value=value)
        return redirect(reverse('Discount', args=[discount.id]))

    def delete(self, request, discount):
        discount.delete()
        return redirect('Discounts list')
