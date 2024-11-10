from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.repository_factory import RepositoryFactory
from django.db import OperationalError

class UserPageView(TemplateView):

    template_name = 'users.html'

    def get(self, request):
        repo = RepositoryFactory.user_repo()
        users = repo.get_all()
        return render(request, self.template_name, {'users': users})
    
    def post(self, request):

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if(first_name and last_name and phone_number and email and password):
            repo = RepositoryFactory.user_repo()
            try:
                repo.create(first_name=first_name, last_name=last_name, phone_number=phone_number, email=email, password=password)
                return redirect('Users list')
            except OperationalError as e:
                return redirect('Users list')
        return redirect('Users list')
