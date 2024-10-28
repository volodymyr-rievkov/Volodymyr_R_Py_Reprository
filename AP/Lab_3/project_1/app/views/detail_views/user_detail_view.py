from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from app.views.detail_views.detail_view_interface import IDetailView
from app.repository_factory import RepositoryFactory
from app.serializers.user_serializer import UserSerializer

class UserDetailView(APIView, IDetailView):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryFactory.user_repo()

    def get(self, request, id):
        user = self.repo.get_by_id(id)
        if(not user):
            return Response(
                {"Error": "User not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        user = self.repo.get_by_id(id)
        if (not user):
            return Response(
                {"Error": "User not found."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserSerializer(user, data=request.data)
        if (serializer.is_valid()):
            updated_user = self.repo.update(
                user,
                first_name=serializer.validated_data.get('first_name'),
                last_name=serializer.validated_data.get('last_name'),
                phone_number=serializer.validated_data.get('phone_number'),
                email=serializer.validated_data.get('email'),
                password=serializer.validated_data.get('password')
            )
            return Response(
                UserSerializer(updated_user).data, 
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    def delete(self, request, id):
        user = self.repo.get_by_id(id)
        if (not user):
            return Response(
                {"Error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
