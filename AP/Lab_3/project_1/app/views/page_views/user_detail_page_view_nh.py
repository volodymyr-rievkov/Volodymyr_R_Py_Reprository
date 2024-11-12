from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from app.network_helper import NetworkHelper

class UserDetailPageViewNH(TemplateView):

    template_name = 'user_detail_nh.html'
    __ITEMS_NAME = 'users'

    def get(self, request, id):

        user = NetworkHelper.get_item_by_id(self.__ITEMS_NAME, id)  
        return render(request, self.template_name, {'user': user})
    
    def post(self, request, id):

        if '_method' in request.POST and request.POST['_method'] == 'DELETE':
            return self.delete(request, id)

    def delete(self, request, id):
        
        NetworkHelper.delete_item(self.__ITEMS_NAME, id)  
        return redirect(reverse('Users list nh'))
    