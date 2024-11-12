from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from app.repository_factory import RepositoryFactory
from django.http import Http404

class UserDetailPageView(TemplateView):

    template_name = 'user_detail.html'

    def __init__(self):
        self.repo = RepositoryFactory.user_repo()

    def get(self, request, id):
        user = self.repo.get_by_id(id)
        if (not user):
            raise Http404("Error: User not found.")
        return render(request, self.template_name, {'user': user})
    
    def post(self, request, id):
        user = self.repo.get_by_id(id)
        if not user:
            raise Http404("Error: User not found.")
        
        if ('_method' in request.POST and request.POST['_method'] == 'DELETE'):
            return self.delete(request, user)
        
        return self.edit(request, user)

    def edit(self, request, user):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')

        self.repo.update(user, first_name=first_name, last_name=last_name, phone_number=phone_number, email=email, password=password)
        return redirect(reverse('User', args=[user.id]))

    def delete(self, request, user):
        user.delete()
        return redirect('Users list')
