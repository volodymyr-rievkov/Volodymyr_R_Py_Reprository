from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth
from app.error_messages import ErrorMessages

class DiscountDetailPageView(TemplateView):
    
    template_name = 'discount/discount_detail.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/discounts_api/"
        self.username = "Volodymyr"
        self.password = "volodymyr"

    def get(self, request, id):
        try:
            response = requests.get(f"{self.api_url}{id}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                discount = response.json()
                return render(request, self.template_name, {'discount': discount})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECT_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

    def post(self, request, id):
        try:
            response = requests.get(f"{self.api_url}{id}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code != 200:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECT_NOT_FOUND}')
            
            discount = response.json()

            if '_method' in request.POST and request.POST['_method'] == 'DELETE':
                return self.delete(request, discount)

            return self.edit(request, discount)

        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

    def edit(self, request, discount):
        discount_data = {
            'value': request.POST.get('value'),
        }

        try:
            response = requests.put(f"{self.api_url}{discount['id']}/", data=discount_data, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                return redirect(reverse('Discount', args=[discount['id']]))
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.UPDATE_FAILED}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

    def delete(self, request, discount):
        try:
            response = requests.delete(f"{self.api_url}{discount['id']}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 204:
                return redirect('Discounts list')
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.DELETE_FAILED}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')
