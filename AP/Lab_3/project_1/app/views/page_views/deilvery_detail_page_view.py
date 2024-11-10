from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from app.repository_factory import RepositoryFactory
from django.http import Http404

class DeliveryDetailPageView(TemplateView):
    
    template_name = 'delivery_detail.html'

    def __init__(self):
        self.repo = RepositoryFactory.delivery_repo()

    def get(self, request, id):
        repo = RepositoryFactory.delivery_repo()
        delivery = repo.get_by_id(id)
        if not delivery:
            raise Http404("Error: Delivery not found.")
        return render(request, self.template_name, {'delivery': delivery})
    
    def post(self, request, id):
        delivery = self.repo.get_by_id(id)
        if not delivery:
            raise Http404("Error: Delivery not found.")
        
        if '_method' in request.POST and request.POST['_method'] == 'DELETE':
            return self.delete(request, delivery)
        
        return self.edit(request, delivery)

    def edit(self, request, delivery):
        order_id = request.POST.get('order_id')
        country = request.POST.get('country')
        city = request.POST.get('city')
        street = request.POST.get('street')

        if order_id:
            delivery.order_id = order_id
        if country:
            delivery.country = country
        if city:
            delivery.city = city
        if street:
            delivery.street = street

        self.repo.update(delivery, country=country, city=city, street=street)
        return redirect(reverse('Delivery', args=[delivery.id]))

    def delete(self, request, delivery):
        delivery.delete()
        return redirect(reverse('Deliveries list'))
