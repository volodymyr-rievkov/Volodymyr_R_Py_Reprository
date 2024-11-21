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

    def group_info(self, infos):
        grouped_infos = infos.groupby("country")["order__total_price"].sum().reset_index()
        grouped_infos.columns = ["country", "expenses"]
        return grouped_infos

    def get_countries(self, infos):
        return infos["country"].tolist()

    def get_selected_countries(self, request, countries):
        return request.GET.getlist('countries') or countries

    def get_filtered_info(self, grouped_infos, selected_countries):
        return grouped_infos[grouped_infos["country"].isin(selected_countries)]

    def build_bar(self, filtered_info):
        return px.bar(filtered_info, x='country', y='expenses', title='Country Expenses')

    def build_pie(self, filtered_info):
        return px.pie(filtered_info, names='country', values='expenses', title='Country Expenses')

    def build_line(self, filtered_info):
        return px.line(filtered_info.sort_values(by='expenses', ascending=False), x='country', y='expenses', title='Country Expenses')

    def convert_to_html(self, plot):
        return plot.to_html(full_html=False)

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                infos = pd.read_json(response.json(), orient="split")
                grouped_infos = self.group_info(infos)
                countries = self.get_countries(grouped_infos)
                selected_countries = self.get_selected_countries(request, countries)
                filtered_info = self.get_filtered_info(grouped_infos, selected_countries)
                
                bar_fig = self.build_bar(filtered_info)
                pie_fig = self.build_pie(filtered_info)
                line_fig = self.build_line(filtered_info)

                bar_graph_html = self.convert_to_html(bar_fig)
                pie_graph_html = self.convert_to_html(pie_fig)
                line_graph_html = self.convert_to_html(line_fig)

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
        