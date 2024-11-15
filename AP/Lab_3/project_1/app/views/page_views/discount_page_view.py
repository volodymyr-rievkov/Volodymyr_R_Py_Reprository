from django.shortcuts import render, redirect
from django.urls import reverse
from app.error_messages import ErrorMessages
from requests.auth import HTTPBasicAuth
from django.views.generic import TemplateView
import requests

class DiscountPageView(TemplateView):

    template_name = 'discounts.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/discounts_api/"
        self.username = 'Volodymyr'
        self.password = 'volodymyr'

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                discounts = response.json()
                return render(request, self.template_name, {'discounts': discounts})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')
    
    def post(self, request):
        discounts_data = {
            'value': request.POST.get('value')
        } 

        if discounts_data['value']:
            try:
                response = requests.post(self.api_url, data=discounts_data, auth=HTTPBasicAuth(self.username, self.password))                
                if response.status_code == 201:  
                    return redirect('Discounts list')
                else:
                    return redirect(f'{reverse("Error")}?error_message={ErrorMessages.CREATE_FAILED}')
            except requests.exceptions.RequestException as e:
                return redirect(f'{reverse("Error")}?error_message={e}') 
        else:
            return redirect(f'{reverse("Error")}?error_message={ErrorMessages.NOT_ENOUGH_ARGUMENTS}')
