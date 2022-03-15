from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from personal_finances.api_server.models import Account

from personal_finances.serializers import (AccountSerializer, UserSerializer,
    UserUpdateAsAdminSerializer, UserUpdateSerializer)

class Home(APIView):
    def get(self, request):
        return Response(
            {'message': 'Personal finances API.'\
                f' Welcome {request.user.get_full_name()}'},
            status=status.HTTP_200_OK
        )

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
        if self.request.user.is_staff:
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

class AccountView(APIView):
    def get(self, request, id=None):
        if id:
            try:
                account = Account.objects.get(id=id, user=request.user)
            except Account.DoesNotExist:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            return Response(
                AccountSerializer(account).data, status=status.HTTP_200_OK)
        accounts = Account.objects.filter(user=request.user)
        return Response(
            AccountSerializer(accounts, many=True).data,
            status=status.HTTP_200_OK
        )
    
    def post(self, request):
        account_srz = AccountSerializer(data=request.data)
        if not account_srz.is_valid():
            return Response(
                account_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        account = account_srz.save(user=request.user)
        account_srz = AccountSerializer(account)
        return Response(account_srz.data, status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        try:
            account = Account.objects.get(id=id, user=request.user)
        except Account.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        account_srz = AccountSerializer(account, data=request.data)
        if not account_srz.is_valid():
            return Response(
                account_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        new_account = account_srz.save()
        account_srz = AccountSerializer(new_account)
        return Response(account_srz.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        try:
            account = Account.objects.get(id=id, user=request.user)
        except Account.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        account.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
