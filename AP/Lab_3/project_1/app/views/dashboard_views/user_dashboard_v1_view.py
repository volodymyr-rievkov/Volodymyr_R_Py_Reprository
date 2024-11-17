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

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                orders = pd.DataFrame(response.json())
                avg_discounts = (orders.groupby(["user__first_name", "user__last_name"])["product__discount_id__value"].mean().reset_index())
                avg_discounts.columns = ["first_name", "last_name", "average_discount"]
                avg_discounts["full_name"] = avg_discounts["first_name"] + " " + avg_discounts["last_name"]

                bar_fig = px.bar(avg_discounts, x='full_name', y='average_discount', title='User Avg Discounts')
                pie_fig = px.pie(avg_discounts, names='full_name', values='average_discount', title='User Avg Discounts')
                line_fig = px.line(avg_discounts.sort_values(by='average_discount', ascending=False), x='full_name', y='average_discount', title='User Avg Discounts')

                bar_graph_html = bar_fig.to_html(full_html=False)
                pie_graph_html = pie_fig.to_html(full_html=False)
                line_graph_html = line_fig.to_html(full_html=False)

                return render(request, self.template_name, {
                    'bar_graph': bar_graph_html,
                    'pie_graph': pie_graph_html,
                    'line_graph': line_graph_html,
                })
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}') 
   