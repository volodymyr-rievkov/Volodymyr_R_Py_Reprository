from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth 
from app.error_messages import ErrorMessages
import pandas as pd

class UsersWithDscntAbovePView(TemplateView):
    template_name = 'aggreg/user_with_disc.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/user_with_discount_api/"
        self.username = 'Volodymyr'  
        self.password = 'volodymyr'

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                orders = pd.DataFrame(response.json())
                print("-" * 20)
                print(orders)
                print("-" * 20)
                stats = {
                    "max": orders['product__discount_id__value'].max(),
                    "min": orders['product__discount_id__value'].min(),
                    "avg": orders['product__discount_id__value'].mean(),
                    "median": orders['product__discount_id__value'].median()
                }
                avg_discounts = (orders.groupby(["user__first_name", "user__last_name"])["product__discount_id__value"].mean().reset_index())
                avg_discounts.columns = ["first_name", "last_name", "average_discount"]
                print("-" * 20)
                print(avg_discounts)
                print("-" * 20)
                return render(request, self.template_name, {'orders': orders.reset_index().to_dict(orient="records"), 'stats': stats, 'avg_discounts': avg_discounts.to_dict(orient="records")})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}') 
    