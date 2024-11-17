from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth 
from app.error_messages import ErrorMessages
import pandas as pd

class DelivsDueOrderPView(TemplateView):
    template_name = 'aggreg/deliv_due_to_ord.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/deliveries_due_to_order_api/"
        self.username = 'Volodymyr'  
        self.password = 'volodymyr'

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                infos = pd.DataFrame(response.json())
                print("-" * 20)
                print(infos)
                print("-" * 20)
                stats = {
                    "max": infos['order__total_price'].max(),
                    "min": infos['order__total_price'].min(),
                    "avg": infos['order__total_price'].mean(),
                    "median": infos['order__total_price'].median()
                }
                avg_expenses = infos.groupby('country')['order__total_price'].mean().reset_index()
                avg_expenses.columns = ['country', 'average_total_price']
                print("-" * 20)
                print(avg_expenses)
                print("-" * 20)
                return render(request, self.template_name, {'infos': infos.reset_index().to_dict(orient="records"), 'stats': stats, 'avg_expenses': avg_expenses.to_dict(orient="records")})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}') 
      

    