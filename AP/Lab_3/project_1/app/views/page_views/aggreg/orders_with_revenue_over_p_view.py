from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth 
from app.error_messages import ErrorMessages

class OrdersWithRevenueOverPView(TemplateView):
    template_name = 'aggreg/ord_rev_over.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/orders_revenue_over_api/"
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
    