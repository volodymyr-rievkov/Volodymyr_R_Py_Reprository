from django.shortcuts import render
from django.views.generic import TemplateView
from app.network_helper import NetworkHelper

class UserPageViewNH(TemplateView):

    template_name = 'users_nh.html'
    __ITEMS_NAME = 'users'

    def get(self, request):
        
        users = NetworkHelper.get_items(self.__ITEMS_NAME)
        return render(request, self.template_name, {'users': users})
    