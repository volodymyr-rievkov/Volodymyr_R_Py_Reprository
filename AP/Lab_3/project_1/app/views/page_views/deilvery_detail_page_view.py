from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth
from app.error_messages import ErrorMessages

class DeliveryDetailPageView(TemplateView):
    
    template_name = 'delivery_detail.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/deliveries_api/"
        self.order_api_url = "http://127.0.0.1:8000/orders_api/"
        self.users_api_url = "http://127.0.0.1:8000/users_api/"
        self.products_api_url = "http://127.0.0.1:8000/products_api/"
        self.username = "Volodymyr"
        self.password = "volodymyr"

    def get(self, request, id):
        try:
            response = requests.get(f"{self.api_url}{id}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                delivery = response.json()
                order_response = requests.get(f"{self.order_api_url}{delivery['order']}/", auth=HTTPBasicAuth(self.username, self.password))
                order = order_response.json()
                product_response = requests.get(f"{self.products_api_url}{order['product']}/", auth=HTTPBasicAuth(self.username, self.password))
                product = product_response.json()
                user_response = requests.get(f"{self.users_api_url}{order['user']}/", auth=HTTPBasicAuth(self.username, self.password))
                user = user_response.json()
                return render(request, self.template_name, {'delivery': delivery, 'user': user, 'product': product, 'order': order})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECT_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')
    
    def post(self, request, id):
        try:
            response = requests.get(f"{self.api_url}{id}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code != 200:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECT_NOT_FOUND}')
            
            delivery = response.json()

            if '_method' in request.POST and request.POST['_method'] == 'DELETE':
                return self.delete(request, delivery)

            return self.edit(request, delivery)

        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

    def edit(self, request, delivery):
        delivery_data = {
            'order': request.POST.get('order'),
            'country': request.POST.get('country'),
            'city': request.POST.get('city'),
            'street': request.POST.get('street'),
        }
        try:
            response = requests.put(f"{self.api_url}{delivery['id']}/", data=delivery_data, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                return redirect(reverse('Delivery', args=[delivery['id']]))
            else:
                response.json()
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.UPDATE_FAILED}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

    def delete(self, request, delivery):
        try:
            response = requests.delete(f"{self.api_url}{delivery['id']}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 204:
                return redirect('Deliveries list')
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.DELETE_FAILED}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

