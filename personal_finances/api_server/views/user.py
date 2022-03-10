from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User

from personal_finances.serializers import UserSerializer

@api_view(['POST'])
def delete_token(request):
    delete_result = Token.objects.filter(user=request.user).delete()
    return Response(
        {'deleted': delete_result[0]},
        status=status.HTTP_200_OK
    )

class UserManagement(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['list', 'destroy']:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
