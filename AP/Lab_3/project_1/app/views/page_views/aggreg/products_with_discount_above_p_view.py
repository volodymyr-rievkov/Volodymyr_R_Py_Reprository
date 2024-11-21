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

    def calc_stats(self, df):
        return {
                    "max": df['price'].max(),
                    "min": df['price'].min(),
                    "avg": df['price'].mean(),
                    "median": df['price'].median()
                }
    
    def convert_price_to_numeric(self, df):
        df['price'] = pd.to_numeric(df['price'])

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                print("Received data:", response.json()) 
                df = pd.read_json(response.json(), orient="split")
                print("DataFrame preview:", df)
                self.convert_price_to_numeric(df)
                stats = self.calc_stats(df)
                return render(request, self.template_name, {'products': df.reset_index().to_dict(orient="records"), 'stats': stats})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}') 
