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
from math import pi
from bokeh.transform import cumsum
from bokeh.palettes import Viridis256
from bokeh.models import ColumnDataSource

class DelivDashboardV2View(TemplateView):
    template_name = 'dashboard\delivery\dashboard_v2.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/deliveries_due_to_order_api/"
        self.username = 'Volodymyr'
        self.password = 'volodymyr'
        self.DEFAULT_VALUE = 500

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
        bar_fig = figure(x_range=filtered_info['country'].tolist(), title="Country Expenses", toolbar_location=None, tools="hover")
        bar_fig.vbar(x=filtered_info['country'], top=filtered_info['expenses'], width=0.9, color=Category10[10][0])
        bar_fig.xaxis.axis_label = "Country"
        bar_fig.yaxis.axis_label = "Expenses"
        bar_fig.xaxis.major_label_orientation = "vertical"
        return bar_fig

    def build_line(self, filtered_info):
        line_fig = figure(title="Country Expenses", x_axis_label="Country", y_axis_label="Expenses", x_range=filtered_info['country'].tolist())
        line_fig.line(filtered_info['country'], filtered_info['expenses'], line_width=2, line_color="blue")
        line_fig.xaxis.major_label_orientation = "vertical"
        return line_fig

    def build_pie(self, filtered_info):
        filtered_info['angle'] = filtered_info['expenses'] / filtered_info['expenses'].sum() * 2 * pi
        filtered_info['color'] = Viridis256[:len(filtered_info)]
        source = ColumnDataSource(data=dict(
            country=filtered_info['country'],
            angle=filtered_info['angle'],
            color=filtered_info['color'],
            expenses=filtered_info['expenses']
        ))
        pie_fig = figure(
            height=350,
            title="Country Expenses",
            toolbar_location=None,
            tools="hover",
            tooltips="@country: @expenses",
            x_range=(-0.5, 1.0)
        )

        pie_fig.wedge(
            x=0, y=1,
            radius=0.4,
            start_angle=cumsum('angle', include_zero=True),
            end_angle=cumsum('angle'),
            line_color="white",
            fill_color='color',
            legend_field='country',
            source=source
        )

        pie_fig.axis.axis_label = None
        pie_fig.axis.visible = False
        pie_fig.grid.grid_line_color = None

        return pie_fig

    def get(self, request):
        try:
            value = request.GET.get('value')
            if value:
                value = int(value)
                request.session['value'] = value
            else:
                value = request.session.get('value', self.DEFAULT_VALUE)
            params = {'value': value}
            response = requests.get(self.api_url, params=params, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                infos = pd.read_json(response.json(), orient="split")
                grouped_infos = self.group_info(infos)
                countries = self.get_countries(grouped_infos)
                selected_countries = self.get_selected_countries(request, countries)
                filtered_info = self.get_filtered_info(grouped_infos, selected_countries)

                bar_fig = self.build_bar(filtered_info)
                line_fig = self.build_line(filtered_info)
                pie_fig = self.build_pie(filtered_info)

                bar_script, bar_div = components(bar_fig)
                line_script, line_div = components(line_fig)
                pie_script, pie_div = components(pie_fig)

                return render(request, self.template_name, {
                    'countries': countries,
                    'selected_countries': selected_countries,
                    'bar_script': bar_script,
                    'bar_div': bar_div,
                    'line_script': line_script,
                    'line_div': line_div,
                    'pie_script': pie_script,
                    'pie_div': pie_div,
                })
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

