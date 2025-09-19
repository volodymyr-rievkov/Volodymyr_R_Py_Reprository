from django.shortcuts import render

def post_list_view(request):
    return render(request, 'post_list.html')

def post_detail_view(request, id):
    return render(request, 'post_detail.html')