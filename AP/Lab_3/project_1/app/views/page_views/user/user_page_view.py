from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth
from app.error_messages import ErrorMessages

class UserPageView(TemplateView):

    template_name = 'user/users.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/users_api/"
        self.username = 'Volodymyr'  
        self.password = 'volodymyr'

    def get(self, request):
        try:
            response = requests.get(self.api_url, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                users = response.json()
                return render(request, self.template_name, {'users': users})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}') 
        
    def post(self, request):
        user_data = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'phone_number': request.POST.get('phone_number'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
        }
        if(user_data['email'] and user_data['first_name'] and user_data['last_name'] and user_data['password'] and user_data['phone_number']):
            if len(user_data['phone_number']) != 13:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.INVALID_PHONE_NUMBER_LENGTH}')
            try:
                response = requests.post(self.api_url, data=user_data, auth=HTTPBasicAuth(self.username, self.password))
                if response.status_code == 201:  
                    return redirect('Users list')
                else:
                    return redirect(f'{reverse("Error")}?error_message={ErrorMessages.CREATE_FAILED}')

            except requests.exceptions.RequestException as e:
                return redirect(f'{reverse("Error")}?error_message={e}')
        else:
            return redirect(f'{reverse("Error")}?error_message={ErrorMessages.NOT_ENOUGH_ARGUMENTS}')
