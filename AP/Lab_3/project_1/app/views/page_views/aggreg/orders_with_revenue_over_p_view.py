from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth 
from app.error_messages import ErrorMessages
import pandas as pd

class OrdersWithRevenueOverPView(TemplateView):
    template_name = 'aggreg/ord_rev_over.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/orders_revenue_over_api/"
        self.username = 'Volodymyr'  
        self.password = 'volodymyr'
        self.DEFAULT_VALUE = 500

    def calc_stats(self, df):
        return {
                    "max": df['total_spent'].max(),
                    "min": df['total_spent'].min(),
                    "avg": df['total_spent'].mean(),
                    "median": df['total_spent'].median()
                }

    def get(self, request):
        try:
            value = request.GET.get('value', self.DEFAULT_VALUE)
            params = {"value": value}
            response = requests.get(self.api_url, params=params, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                df = pd.read_json(response.json(), orient="split")
                stats = self.calc_stats(df)
                return render(request, self.template_name, {'orders': df.reset_index().to_dict(orient="records"), 'stats': stats, "value": value})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}') 
    