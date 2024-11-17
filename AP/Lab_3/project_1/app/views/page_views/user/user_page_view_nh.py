from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from app.network_helper import NetworkHelper
from app.error_messages import ErrorMessages


class UserPageViewNH(TemplateView):

    template_name = 'user/users_nh.html'
    __ITEMS_NAME = 'users'

    def get(self, request):
        try:
            users = NetworkHelper.get_items(self.__ITEMS_NAME)
            return render(request, self.template_name, {'users': users})
        except: 
            return redirect(f'{reverse("Error")}?error_message={ErrorMessages.OBJECTS_NOT_FOUND}')
