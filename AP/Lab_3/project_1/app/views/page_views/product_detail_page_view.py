from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth
from app.error_messages  import ErrorMessages


class ProductDetailPageView(TemplateView):
    
    template_name = 'product_detail.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/products_api/"
        self.discount_api_url = "http://127.0.0.1:8000/discounts_api/"
        self.username = "Volodymyr"
        self.password = "volodymyr"

    def get(self, request, id):

        try:
            response = requests.get(f"{self.api_url}{id}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                product = response.json()

                discount_response = requests.get(f"{self.discount_api_url}{product['discount_id']}/", auth=HTTPBasicAuth(self.username, self.password))
                if discount_response.status_code == 200:
                    try:
                        discount = discount_response.json()  
                    except ValueError:
                        discount = None
                else:
                    discount = None
        
                return render(request, self.template_name, {'product': product, 'discount': discount})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECT_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

    def post(self, request, id):
        try:
            response = requests.get(f"{self.api_url}{id}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code != 200:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECT_NOT_FOUND}')
            
            product = response.json()

            if '_method' in request.POST and request.POST['_method'] == 'DELETE':
                return self.delete(request, product)

            return self.edit(request, product)
        
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

    def edit(self, request, product):
        product_data = {
            "name": request.POST.get('name'),
            "info": request.POST.get('info'),
            "price": request.POST.get('price'),
            "amount": request.POST.get('amount'),
            "discount_id": request.POST.get('discount')
        }
        
        if(product_data["price"]):
            try:
                product_data['price'] = float(product_data['price'])
            except ValueError as v_e:
                return redirect(f'{reverse("Error")}?error_message={v_e}')
            
        if(product_data["amount"]):
            try:
                product_data["amount"] = int(product_data["amount"])
            except ValueError as v_e:
                return redirect(f'{reverse("Error")}?error_message={v_e}')
        if(product_data["discount_id"]):
            try:
                product_data["discount_id"] = int(product_data["discount_id"])
            except ValueError as v_e:
                return redirect(f'{reverse("Error")}?error_message={v_e}')  
        try:
            response = requests.put(f"{self.api_url}{product['id']}/", data=product_data, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                return redirect(reverse('Product', args=[product['id']]))
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.UPDATE_FAILED}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

    def delete(self, request, product):
        try:
            response = requests.delete(f"{self.api_url}{product['id']}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 204:
                return redirect('Products list')
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.DELETE_FAILED}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')
