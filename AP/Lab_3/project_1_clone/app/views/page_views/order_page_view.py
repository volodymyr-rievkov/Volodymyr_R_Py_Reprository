from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.repository_factory import RepositoryFactory
from django.db import OperationalError

class OrderPageView(TemplateView):
    
    template_name = 'orders.html'

    def get(self, request):
        repo = RepositoryFactory.order_repo()  
        orders = repo.get_all()  
        return render(request, self.template_name, {'orders': orders})

    def post(self, request):
        user_id = request.POST.get('user_id')
        product_id = request.POST.get('product_id')
        amount = request.POST.get('amount')
        comment = request.POST.get('comment')

        if (user_id and product_id and amount):
            try:
                user_id = int(user_id)
                product_id = int(product_id)
                amount = int(amount)
            except ValueError:
                return redirect('Orders list')
            repo = RepositoryFactory.order_repo()
            try:
                repo.create(user_id=user_id, product_id=product_id, amount=amount, comment=comment)
                return redirect('Orders list')
            except OperationalError:
                return redirect('Orders list')
        return redirect('Orders list')
