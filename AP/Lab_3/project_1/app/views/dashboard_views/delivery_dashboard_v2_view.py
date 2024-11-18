from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.palettes import Category10
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from app.error_messages import ErrorMessages

class DelivDashboardV2View(TemplateView):
    template_name = 'dashboard\delivery\dashboard_v2.html'

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

                bar_fig = figure(x_range=filtered_data['country'].tolist(), title="Country Expenses", toolbar_location=None, tools="hover")
                bar_fig.vbar(x=filtered_data['country'], top=filtered_data['expenses'], width=0.9, color=Category10[10][0])
                bar_fig.xaxis.axis_label = "Country"
                bar_fig.yaxis.axis_label = "Expenses"

                line_fig = figure(title="Country Expenses", x_axis_label="Country", y_axis_label="Expenses", x_range=filtered_data['country'].tolist())
                line_fig.line(filtered_data['country'], filtered_data['expenses'], line_width=2, line_color="blue")

                scatter_fig = figure(title="Country Expenses", x_axis_label="Country", y_axis_label="Expenses", x_range=filtered_data['country'].tolist())
                scatter_fig.scatter(filtered_data['country'], filtered_data['expenses'], size=8, color=Category10[10][1])

                bar_script, bar_div = components(bar_fig)
                line_script, line_div = components(line_fig)
                scatter_script, scatter_div = components(scatter_fig)

                return render(request, self.template_name, {
                    'countries': countries,
                    'selected_countries': selected_countries,
                    'bar_script': bar_script,
                    'bar_div': bar_div,
                    'line_script': line_script,
                    'line_div': line_div,
                    'scatter_script': scatter_script,
                    'scatter_div': scatter_div,
                })
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

