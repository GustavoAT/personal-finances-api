from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User

from personal_finances.serializers import UserSerializer, UserUpdateAsAdminSerializer, UserUpdateSerializer

class DeleteToken(APIView):
    def delete(self, request):
        delete_result = Token.objects.filter(user=request.user).delete()
        return Response(
            {'deleted': delete_result[0]},
            status=status.HTTP_204_NO_CONTENT
        )

class UserManagement(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['create', 'list', 'destroy']:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    def get_serializer_class(self):
        if self.request.user.is_superuser:
            if self.action in ['update', 'partial_update']:
                return UserUpdateAsAdminSerializer
            return UserSerializer
        return self.serializer_class
