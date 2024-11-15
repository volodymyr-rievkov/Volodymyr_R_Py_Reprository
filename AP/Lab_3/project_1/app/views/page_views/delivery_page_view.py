from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.urls import reverse
from app.error_messages import ErrorMessages
from requests.auth import HTTPBasicAuth
import requests

class DeliveryPageView(TemplateView):

    template_name = 'deliveries.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/deliveries_api/"
        self.username = 'Volodymyr'
        self.password = 'volodymyr'

    def get(self, request):
        try:    
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                deliveries = response.json()
                return render(request, self.template_name, {'deliveries': deliveries})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')
          
    def post(self, request):
        deliveries_data = {   
            "order": request.POST.get('order_id'),
            "country": request.POST.get('country'),
            "city": request.POST.get('city'),
            "street": request.POST.get('street')
        }
        if(deliveries_data['order'] and deliveries_data['country'] and deliveries_data['city'] and deliveries_data['street']):
            try:
                response = requests.post(self.api_url, data=deliveries_data, auth=HTTPBasicAuth(self.username, self.password))
                if response.status_code == 201:
                    return redirect('Deliveries list')
                else:
                    return redirect(f'{reverse("Error")}?error_message={ErrorMessages.CREATE_FAILED}')
            except requests.exceptions.RequestException as e:
                return redirect(f'{reverse("Error")}?error_message={e}')
        else:
            return redirect(f'{reverse("Error")}?error_message={ErrorMessages.NOT_ENOUGH_ARGUMENTS}')
