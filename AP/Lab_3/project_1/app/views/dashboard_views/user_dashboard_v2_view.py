from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.palettes import Category10
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth 
from app.error_messages import ErrorMessages
import pandas as pd
from math import pi
from bokeh.transform import cumsum
from bokeh.palettes import Viridis256
from bokeh.models import ColumnDataSource

class UserDashboardV2View(TemplateView):
    template_name = 'dashboard/user/dashboard_v2.html'

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
        bar_fig = figure(x_range=info['full_name'].tolist(), title="User Avg discounts", toolbar_location=None, tools="hover")
        bar_fig.vbar(x=info['full_name'], top=info['average_discount'], width=0.9, color=Category10[10][0])
        bar_fig.xaxis.major_label_orientation = "vertical"
        bar_fig.xaxis.axis_label = "User"
        bar_fig.yaxis.axis_label = "Avg Discount"
        return bar_fig
    
    def build_line(self, info):
        line_fig = figure(title="User Avg discounts", x_axis_label="User", y_axis_label="Avg Discount", x_range=info['full_name'].tolist())
        line_fig.line(info['full_name'], info['average_discount'], line_width=2, line_color="blue")
        line_fig.xaxis.major_label_orientation = "vertical"
        return line_fig

    def build_pie(self, info):
        info['angle'] = info['average_discount'] / info['average_discount'].sum() * 2 * pi  
        info['color'] = Viridis256[:len(info)]
        source = ColumnDataSource(data=dict(
            user=info['full_name'],  
            angle=info['angle'],
            color=info['color'],
            discount=info['average_discount'] 
        ))
        pie_fig = figure(
            height=350,
            title="User Avg Discounts",
            toolbar_location=None,
            tools="hover",
            tooltips="@user: @discount", 
            x_range=(-0.5, 1.0) 
        )
        pie_fig.wedge(
            x=0, y=1,
            radius=0.4,
            start_angle=cumsum('angle', include_zero=True),
            end_angle=cumsum('angle'),
            line_color="white",  
            fill_color='color',  
            legend_field='user',  
            source=source
        )
        pie_fig.axis.axis_label = None
        pie_fig.axis.visible = False
        pie_fig.grid.grid_line_color = None

        return pie_fig

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
                line_fig = self.build_line(filtered_discounts)
                pie_fig = self.build_pie(filtered_discounts)

                bar_script, bar_div = components(bar_fig)
                line_script, line_div = components(line_fig)
                pie_script, pie_div = components(pie_fig)

                return render(request, self.template_name, {
                    'bar_script': bar_script,
                    'bar_div': bar_div,
                    'line_script': line_script,
                    'line_div': line_div,
                    'pie_script': pie_script, 
                    'pie_div': pie_div, 
                    'min_discount_value': min_discount_value,
                    'max_discount_value': max_discount_value,
                })
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}') 
   