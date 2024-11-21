import plotly.express as px
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth 
from app.error_messages import ErrorMessages
import pandas as pd

class UserDashboardV1View(TemplateView):
    template_name = 'dashboard/user/dashboard_v1.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/user_with_discount_api/"
        self.username = 'Volodymyr'  
        self.password = 'volodymyr'

    def calc_avg_discounts(self, info):
        avg_discounts = (info.groupby(["user__first_name", "user__last_name"])["product__discount_id__value"].mean().reset_index())
        avg_discounts.columns = ["first_name", "last_name", "average_discount"]
        avg_discounts["full_name"] = avg_discounts["first_name"] + " " + avg_discounts["last_name"]
        return avg_discounts

    def get_min_value(self, info):
        return info["average_discount"].min()

    def get_max_values(self, info):
        return info["average_discount"].max()

    def filter_info(self, info, min_value):
        return info[info['average_discount'] >= min_value]

    def get_min_discount(self, request, min_discount_value):
        return float(request.GET.get('min_discount', min_discount_value))

    def build_bar(self, info):
        return px.bar(info, x='full_name', y='average_discount', title='User Avg Discounts')

    def build_pie(self, info):
        return px.pie(info, names='full_name', values='average_discount', title='User Avg Discounts')

    def build_line(self, info):
        return px.line(info.sort_values(by='average_discount', ascending=False), x='full_name', y='average_discount', title='User Avg Discounts')

    def convert_to_html(self, plot):
        return plot.to_html(full_html=False)

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                orders = pd.read_json(response.json(), orient="split")
                avg_discounts = self.calc_avg_discounts(orders)
                min_discount_value = self.get_min_value(avg_discounts)
                max_discount_value = self.get_max_values(avg_discounts)
                min_discount = self.get_min_discount(request, min_discount_value)

                filtered_discounts = self.filter_info(avg_discounts, min_discount)
                bar_fig = self.build_bar(filtered_discounts)
                pie_fig = self.build_pie(filtered_discounts)
                line_fig = self.build_line(filtered_discounts)

                bar_graph_html = self.convert_to_html(bar_fig)
                pie_graph_html = self.convert_to_html(pie_fig)
                line_graph_html = self.convert_to_html(line_fig)

                return render(request, self.template_name, {
                    'bar_graph': bar_graph_html,
                    'pie_graph': pie_graph_html,
                    'line_graph': line_graph_html,
                    'min_discount_value': min_discount_value,
                    'max_discount_value': max_discount_value,
                })
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}') 
   