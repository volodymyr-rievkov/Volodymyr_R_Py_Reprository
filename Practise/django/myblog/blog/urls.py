from django.urls import path
from blog.views.post_api_view import PostAPIView, PostDetailAPIView
from blog.views.post_view import post_list_view, post_detail_view

urlpatterns = [
    path('posts_api/', PostAPIView.as_view(), name="Posts Api"),
    path('post_detail_api/<int:id>/', PostDetailAPIView.as_view(), name="Post Detail Api"),
    path('posts/', post_list_view, name="post_list"),
    path('posts/<int:id>/', post_detail_view, name="post_detail"),
]