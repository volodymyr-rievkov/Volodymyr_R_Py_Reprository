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
        self.DEFAULT_VALUE = 500

    def calc_stats(self, df):
        return {
            "max": df['order__total_price'].max(),
            "min": df['order__total_price'].min(),
            "avg": df['order__total_price'].mean(),
            "median": df['order__total_price'].median()
        }

    def calc_avg_country_total(self, df):
        avg_expenses = df.groupby('country')['order__total_price'].mean().reset_index()
        avg_expenses.columns = ['country', 'average_total_price']
        return avg_expenses

    def get(self, request):
        try:
            value = request.GET.get('value')
            if value:
                value = int(value)
                request.session['value'] = value
            else:
                value = request.session.get('value', self.DEFAULT_VALUE)
            params = {"value": value}
            response = requests.get(self.api_url, params=params, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                df = pd.read_json(response.json() , orient="split") 
                stats = self.calc_stats(df)
                avg_expenses = self.calc_avg_country_total(df)
                return render(request, self.template_name, {
                    'infos': df.reset_index().to_dict(orient="records"),  
                    'stats': stats,
                    'avg_expenses': avg_expenses.to_dict(orient="records"),
                    'value': value
                })
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')
