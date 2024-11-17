from django.shortcuts import render
from django.views.generic import TemplateView

class ErrorPageView(TemplateView):

    template_name = 'general/error_page.html'

    def get(self, request):

        error_message = request.GET.get('error_message', 'AN UNKNOWN ERROR.')
        return render(request, self.template_name, {'error_message': error_message})
