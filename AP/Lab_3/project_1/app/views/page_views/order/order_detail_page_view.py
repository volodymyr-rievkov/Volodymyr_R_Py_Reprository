from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from django.utils import timezone
from requests.auth import HTTPBasicAuth
from app.error_messages import ErrorMessages

class OrderDetailPageView(TemplateView):

    template_name = 'order/order_detail.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/orders_api/"
        self.users_api_url = "http://127.0.0.1:8000/users_api/"
        self.products_api_url = "http://127.0.0.1:8000/products_api/"
        self.username = "Volodymyr"
        self.password = "volodymyr"

    def get(self, request, id):
        try:
            response = requests.get(f"{self.api_url}{id}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                order = response.json()
                user_responde = requests.get(f"{self.users_api_url}{order['user']}/", auth=HTTPBasicAuth(self.username, self.password))
                user = user_responde.json()
                product_responde = requests.get(f"{self.products_api_url}{order['product']}/", auth=HTTPBasicAuth(self.username, self.password))
                product = product_responde.json()
                return render(request, self.template_name, {'order': order, 'product': product, 'user': user})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECT_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

    def post(self, request, id):
        try:
            response = requests.get(f"{self.api_url}{id}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code != 200:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECT_NOT_FOUND}')
            
            order = response.json()

            if '_method' in request.POST and request.POST['_method'] == 'DELETE':
                return self.delete(request, order)

            return self.edit(request, order)

        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

    def edit(self, request, order):
        order_data = {
            "user": request.POST.get('user_id'),
            "product": request.POST.get('product_id'),
            "amount": request.POST.get('amount'),
            "comment": request.POST.get('comment'),
            "date_time": timezone.now(),
            "total_price": 0.0
        }

        try:
            response = requests.put(f"{self.api_url}{order['id']}/", data=order_data, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                return redirect(reverse('Order', args=[order['id']]))
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.UPDATE_FAILED}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

    def delete(self, request, order):
        try:
            response = requests.delete(f"{self.api_url}{order['id']}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 204:
                return redirect('Orders list')
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.DELETE_FAILED}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')
