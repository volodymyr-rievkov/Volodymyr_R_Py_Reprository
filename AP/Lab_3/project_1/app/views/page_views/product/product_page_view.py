from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth
from app.error_messages import ErrorMessages

class ProductPageView(TemplateView):

    template_name = 'product/products.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/products_api/"  
        self.username = 'Volodymyr'
        self.password = 'volodymyr'

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                products = response.json()
                return render(request, self.template_name, {'products': products})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')
        
    def post(self, request):
        product_data = {
            'name': request.POST.get('name'),
            'info': request.POST.get('info'),
            'price': request.POST.get('price'),
            'amount': request.POST.get('amount'),
            'discount_id': request.POST.get('discount')
        }
        if (product_data['amount'] and product_data['name'] and product_data['price']):
            try:
                product_data['price'] = float(product_data['price'])
                product_data["amount"] = int(product_data["amount"])
            except ValueError as v_e:
                return redirect(f'{reverse("Error")}?error_message={v_e}') 
            if product_data['discount_id']:
                try:
                    product_data['discount_id'] = int(product_data['discount_id'])
                except ValueError as v_e:
                    return redirect(f'{reverse("Error")}?error_message={v_e}')  
            else:
                product_data['discount_id'] = None  
            try:
                response = requests.post(self.api_url, data=product_data, auth=HTTPBasicAuth(self.username, self.password))
                if response.status_code == 201:  
                    return redirect('Products list')
                else:
                    return redirect(f'{reverse("Error")}?error_message={ErrorMessages.CREATE_FAILED}')
            except requests.exceptions.RequestException as e:
                return redirect(f'{reverse("Error")}?error_message={e}') 
        else:
            return redirect(f'{reverse("Error")}?error_message={ErrorMessages.NOT_ENOUGH_ARGUMENTS}')
    
