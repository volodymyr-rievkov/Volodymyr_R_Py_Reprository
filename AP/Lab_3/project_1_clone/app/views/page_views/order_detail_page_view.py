from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from app.repository_factory import RepositoryFactory
from django.http import Http404

class OrderDetailPageView(TemplateView):

    template_name = 'order_detail.html'

    def __init__(self):
        self.repo = RepositoryFactory.order_repo() 

    def get(self, request, id):
        order = self.repo.get_by_id(id)  
        if not order:
            raise Http404("Error: Order not found.")
        return render(request, self.template_name, {'order': order})

    def post(self, request, id):
        order = self.repo.get_by_id(id)
        if not order:
            raise Http404("Error: Order not found.")
        
        if '_method' in request.POST and request.POST['_method'] == 'DELETE':
            return self.delete(request, order)
        
        return self.edit(request, order)

    def edit(self, request, order):
        user_id = request.POST.get('user_id')
        product_id = request.POST.get('product_id')
        amount = request.POST.get('amount')
        comment = request.POST.get('comment')

        if user_id:
            order.user_id = user_id
        if product_id:
            order.product_id = product_id
        if amount:
            order.amount = amount
        if comment:
            order.comment = comment

        self.repo.update(order, user_id=user_id, product_id=product_id, amount=amount, comment=comment)
        return redirect(reverse('Order', args=[order.id]))  

    def delete(self, request, order):
        order.delete() 
        return redirect(reverse('Orders list'))  
