import plotly.express as px
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth 
from app.error_messages import ErrorMessages
import pandas as pd

class DelivDashboardV1View(TemplateView):
    template_name = 'dashboard/delivery/dashboard_v1.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/deliveries_due_to_order_api/"
        self.username = 'Volodymyr'  
        self.password = 'volodymyr'

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                infos = pd.DataFrame(response.json())
                grouped_infos = infos.groupby("country")["order__total_price"].sum().reset_index()
                grouped_infos.columns = ["country", "expenses"]

                countries = grouped_infos["country"].tolist()
                selected_countries = request.GET.getlist('countries') or countries
                filtered_data = grouped_infos[grouped_infos["country"].isin(selected_countries)]
                
                bar_fig = px.bar(filtered_data, x='country', y='expenses', title='Country Expenses')
                pie_fig = px.pie(filtered_data, names='country', values='expenses', title='Country Expenses')
                line_fig = px.line(filtered_data.sort_values(by='expenses', ascending=False), x='country', y='expenses', title='Country Expenses')

                bar_graph_html = bar_fig.to_html(full_html=False)
                pie_graph_html = pie_fig.to_html(full_html=False)
                line_graph_html = line_fig.to_html(full_html=False)

                return render(request, self.template_name, {
                    'bar_graph': bar_graph_html,
                    'pie_graph': pie_graph_html,
                    'line_graph': line_graph_html,
                    'countries': countries,
                    'selected_countries': selected_countries,
                })
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}') 
        