from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth 
from app.error_messages import ErrorMessages
import pandas as pd

class ProdsWithDscntsPView(TemplateView):
    template_name = 'aggreg/prod_disc_above.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/products_discount_above_api/"
        self.username = 'Volodymyr'  
        self.password = 'volodymyr'

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                products = pd.DataFrame(response.json())
                print("-" * 20)
                print(products)
                print("-" * 20)
                products['price'] = pd.to_numeric(products['price'])
                stats = {
                    "max": products['price'].max(),
                    "min": products['price'].min(),
                    "avg": products['price'].mean(),
                    "median": products['price'].median()
                }
                return render(request, self.template_name, {'products': products.reset_index().to_dict(orient="records"), 'stats': stats})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}') 
