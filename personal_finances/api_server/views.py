from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from personal_finances.api_server.models import (Account, Category, CreditCard,
    Subcategory, Transaction)

from personal_finances.serializers import (AccountSerializer,
    CategorySerializer, CategoryUpdateSerializer, CreditCardSerializer, SubcategorySerializer,
    SubcategoryUpdateSerializer, TransactionSerializer,
    TransactionUpdateSerializer, UserSerializer,
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

class CategoryView(APIView):
    def get(self, request, id=None):
        if id:
            try:
                category = Category.objects.get(id=id, user=request.user)
            except Category.DoesNotExist:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            return Response(
                CategorySerializer(category).data, status=status.HTTP_200_OK)
        categories = Category.objects.filter(user=request.user)
        of_type = request.query_params.get('of_type')
        if of_type:
            categories = categories.filter(of_type=of_type)
        category_srz = CategorySerializer(categories, many=True)
        if category_srz.data:
            return Response(category_srz.data, status=status.HTTP_200_OK)
        return Response(category_srz.data, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        category_srz = CategorySerializer(data=request.data)
        if not category_srz.is_valid():
            return Response(
                category_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        category = category_srz.save(user=request.user)
        category_srz = CategorySerializer(category)
        return Response(category_srz.data, status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        try:
            category = Category.objects.get(id=id, user=request.user)
        except Category.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        category_srz = CategoryUpdateSerializer(category, data=request.data)
        if not category_srz.is_valid():
            return Response(
                category_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        new_category = category_srz.save()
        category_srz = CategorySerializer(new_category)
        return Response(category_srz.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        try:
            category = Category.objects.get(id=id, user=request.user)
        except Category.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

class SubcategoryView(APIView):
    def get(self, request, id=None):
        if id:
            try:
                subcategory = Subcategory.objects.get(
                    id=id,
                    category__user=request.user
                )
            except Subcategory.DoesNotExist:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            return Response(
                SubcategorySerializer(
                    subcategory).data, status=status.HTTP_200_OK)
        subcategories = Subcategory.objects.filter(category__user=request.user)
        category_id = request.query_params.get('category')
        if category_id:
            subcategories = subcategories.filter(category=category_id)
        subcategory_srz = SubcategorySerializer(subcategories, many=True)
        if subcategory_srz.data:
            return Response(subcategory_srz.data, status=status.HTTP_200_OK)
        return Response(subcategory_srz.data, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        subcategory_srz = SubcategorySerializer(data=request.data)
        if not subcategory_srz.is_valid():
            return Response(
                subcategory_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        subcategory = subcategory_srz.save()
        subcategory_srz = SubcategorySerializer(subcategory)
        return Response(subcategory_srz.data, status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        try:
            subcategory = Subcategory.objects.get(
                id=id, category__user=request.user)
        except Subcategory.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        subcategory_srz = SubcategoryUpdateSerializer(
            subcategory, data=request.data)
        if not subcategory_srz.is_valid():
            return Response(
                subcategory_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        new_subcategory = subcategory_srz.save()
        subcategory_srz = SubcategorySerializer(new_subcategory)
        return Response(subcategory_srz.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        try:
            subcategory = Subcategory.objects.get(
                id=id, category__user=request.user)
        except Subcategory.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        subcategory.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

class TransactionView(APIView):
    def get(self, request, id=None):
        if id:
            try:
                transaction = Transaction.objects.get(
                    id=id, account__user=request.user)
            except Transaction.DoesNotExist:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            return Response(
                TransactionSerializer(transaction).data,
                status=status.HTTP_200_OK
            )
        transactions = Transaction.objects.filter(
            account__user=request.user)
        transaction_type = request.query_params.get('type')
        if transaction_type == Transaction.INCOME:
            transactions = Transaction.incomes.all()
        if transaction_type == Transaction.EXPENSE:
            transactions = Transaction.expenses.all()
        return Response(
            TransactionSerializer(transactions, many=True).data,
            status=status.HTTP_200_OK
        )
    
    def post(self, request):
        transaction_srz = TransactionSerializer(data=request.data)
        if not transaction_srz.is_valid():
            return Response(
                transaction_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        transaction = transaction_srz.save()
        transaction_srz = TransactionSerializer(transaction)
        return Response(transaction_srz.data, status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        try:
            transaction = Transaction.objects.get(
                id=id, account__user=request.user)
        except Transaction.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        transaction_srz = TransactionUpdateSerializer(
            transaction, data=request.data, partial=True)
        if not transaction_srz.is_valid():
            return Response(
                transaction_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        new_transaction = transaction_srz.save()
        transaction_srz = TransactionSerializer(new_transaction)
        return Response(transaction_srz.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        try:
            transaction = Transaction.objects.get(
                id=id, account__user=request.user)
        except Transaction.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        transaction.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

class CreditCardView(APIView):
    def get(self, request, id=None):
        if id:
            try:
                card = CreditCard.objects.get(
                    id=id, account__user=request.user)
            except CreditCard.DoesNotExist:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            return Response(
                CreditCardSerializer(card).data, status=status.HTTP_200_OK)
        cards = CreditCard.objects.filter(account__user=request.user)
        return Response(
            CreditCardSerializer(cards, many=True).data,
            status=status.HTTP_200_OK
        )
    
    def post(self, request):
        card_srz = CreditCardSerializer(data=request.data)
        if not card_srz.is_valid():
            return Response(
                card_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            Account.objects.get(
                id=request.data['account'], user=request.user)
        except Account.DoesNotExist:
            return Response(
                {'message': 'account not found'},
                status=status.HTTP_404_NOT_FOUND)
        card = card_srz.save()
        card_srz = CreditCardSerializer(card)
        return Response(card_srz.data, status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        try:
            card = CreditCard.objects.get(id=id, account__user=request.user)
        except CreditCard.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        card_srz = CreditCardSerializer(card, data=request.data, partial=True)
        if not card_srz.is_valid():
            return Response(
                card_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('account'):
            try:
                Account.objects.get(
                    id=request.data['account'], user=request.user)
            except Account.DoesNotExist:
                return Response(
                    {'message': 'account not found'},
                    status=status.HTTP_404_NOT_FOUND)
        new_card = card_srz.save()
        card_srz = CreditCardSerializer(new_card)
        return Response(card_srz.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        try:
            card = CreditCard.objects.get(id=id, account__user=request.user)
        except Account.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        card.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
