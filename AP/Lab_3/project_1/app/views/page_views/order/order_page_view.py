from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth 
from django.utils import timezone
from app.error_messages import ErrorMessages

class OrderPageView(TemplateView):
    
    template_name = 'order/orders.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/orders_api/"
        self.username = 'Volodymyr'
        self.password = 'volodymyr'

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                orders = response.json()
                return render(request, self.template_name, {'orders': orders})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')
    
    def post(self, request):
        order_data = {
            'user': request.POST.get('user_id'),
            'product': request.POST.get('product_id'),
            'amount': request.POST.get('amount'),
            'comment': request.POST.get('comment'),
            'date_time': timezone.now(),
            'total_price': 0
        }

        if (order_data['user'] and order_data['product'] and order_data['amount']):  
            try:
                response = requests.post(self.api_url, data=order_data, auth=HTTPBasicAuth(self.username, self.password))                
                if response.status_code == 201:  
                    return redirect('Orders list')
                else:
                    return redirect(f'{reverse("Error")}?error_message={response.text}')
            except requests.exceptions.RequestException as e:
                return redirect(f'{reverse("Error")}?error_message={e}')
        else:
            return redirect(f'{reverse("Error")}?error_message={ErrorMessages.NOT_ENOUGH_ARGUMENTS}')
