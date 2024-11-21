from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth 
from app.error_messages import ErrorMessages
import pandas as pd

class UsersWithTotalPView(TemplateView):
    template_name = 'aggreg/user_with_tot.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/users_with_total_api/"
        self.username = 'Volodymyr'  
        self.password = 'volodymyr'

    def calc_stats(self, df):
        return {
                    "max": df['total_spent'].max(),
                    "min": df['total_spent'].min(),
                    "avg": df['total_spent'].mean(),
                    "median": df['total_spent'].median()
                }   

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                df = pd.read_json(response.json(), orient="split")
                stats = self.calc_stats(df)      
                return render(request, self.template_name, {'users': df.reset_index().to_dict(orient="records"), 'stats': stats})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}') 
