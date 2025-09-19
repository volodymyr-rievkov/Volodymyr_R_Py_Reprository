from blog.models.post import Post
from blog.repositories.post_repository import PostRepository
from blog.serializers.post_serializer import PostSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class PostAPIView(APIView):

    def get(self, request):
        posts = PostRepository.get_all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = PostRepository.create(serializer.validated_data)
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)       

class PostDetailAPIView(APIView):

    def get(self, request, id):
        post = PostRepository.get_by_id(id)
        if (post is None):
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, id):
        post = PostRepository.get_by_id(id)
        if (post is None):
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if(serializer.is_valid()):
            PostRepository.update(post, serializer.validated_data)
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        post = PostRepository.get_by_id(id)
        if(post is None):
            return Response(status=status.HTTP_404_NOT_FOUND)
        PostRepository.delete(post)
        return Response(status=status.HTTP_204_NO_CONTENT)
