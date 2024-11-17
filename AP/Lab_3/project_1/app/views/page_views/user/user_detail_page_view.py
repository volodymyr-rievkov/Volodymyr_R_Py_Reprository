from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
import requests
from requests.auth import HTTPBasicAuth
from app.error_messages import ErrorMessages

class UserDetailPageView(TemplateView):

    template_name = 'user/user_detail.html'

    def __init__(self):
        self.api_url = "http://127.0.0.1:8000/users_api/"
        self.username = "Volodymyr"
        self.password = "volodymyr"

    def get(self, request, id):
        try:
            response = requests.get(f"{self.api_url}{id}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                user = response.json()
                return render(request, self.template_name, {'user': user})
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECT_NOT_FOUND}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')

    def post(self, request, id):
        response = requests.get(f"{self.api_url}{id}/", auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code != 200:
            return redirect(f'{reverse("error")}?error_message={ErrorMessages.OBJECT_NOT_FOUND}')
        
        user = response.json()

        if '_method' in request.POST and request.POST['_method'] == 'DELETE':
            return self.delete(request, user)

        return self.edit(request, user)

    def edit(self, request, user):
        user_data = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'phone_number': request.POST.get('phone_number'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
        }
        if user_data['phone_number'] and len(user_data['phone_number']) != 13:
            return redirect(f'{reverse("Error")}?error_message={ErrorMessages.INVALID_PHONE_NUMBER_LENGTH}')
        try:
            response = requests.put(f"{self.api_url}{user['id']}/", data=user_data, auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 200:
                return redirect(reverse('User', args=[user['id']]))
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.UPDATE_FAILED}')

        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')
        
    def delete(self, request, user):
        try:
            response = requests.delete(f"{self.api_url}{user['id']}/", auth=HTTPBasicAuth(self.username, self.password))
            if response.status_code == 204:
                return redirect('Users list')
            else:
                return redirect(f'{reverse("Error")}?error_message={ErrorMessages.DELETE_FAILED}')
        except requests.exceptions.RequestException as e:
            return redirect(f'{reverse("Error")}?error_message={e}')
