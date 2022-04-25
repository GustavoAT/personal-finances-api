from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction as dbtnsac
from django.db.models import Sum as dbsum
from django.forms import ValidationError
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from personal_finances.api_server.models import (Account, Category, CreditCard,
    CreditCardExpense, CreditCardInvoice, Subcategory, Transaction,
    Transference)
from personal_finances.api_server.pagination import PageNumberCustomPagination
from personal_finances.serializers import (AccountSerializer,
    CategorySerializer, CategoryUpdateSerializer, CreditCardExpenseSerializer,
    CreditCardSerializer, PasswordChangeSerializer, PeriodSerializer,
    SubcategorySerializer, SubcategoryUpdateSerializer, TransactionSerializer,
    TransactionUpdateSerializer, TransferenceSerializer, UserExtrasSerializer,
    UserSerializer, UserUpdateAsAdminSerializer, UserUpdateSerializer)


@api_view(['GET'])
def home(request):
    return Response(
        {'message': 'Personal finances API.'\
            f' Welcome {request.user.get_full_name()}'},
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
def delete_token(request):
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

@api_view(['POST'])
def change_password(request):
    user = request.user
    pass_srz = PasswordChangeSerializer(data=request.data)
    if not pass_srz.is_valid():
        return Response(pass_srz.errors, status=status.HTTP_400_BAD_REQUEST)
    oldvalid = user.check_password(
            pass_srz.validated_data['old_password'])
    if not oldvalid:
        return Response(
            {'message': 'invalid old password'},
            status=status.HTTP_401_UNAUTHORIZED)
    try:
        validate_password(pass_srz.validated_data['new_password'], user)
    except ValidationError as e:
        return Response(
            e.messages,
            status=status.HTTP_400_BAD_REQUEST)
    user.set_password(pass_srz.validated_data['new_password'])
    user.save()
    Token.objects.filter(user=request.user).delete()
    return Response(
            {'message': 'change successful'},
            status=status.HTTP_200_OK)
    
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
        if account.initial_value != account.balance:
            account.balance = account.initial_value
            account.save()
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
            transactions = Transaction.incomes.filter(
                account__user=request.user)
        if transaction_type == Transaction.EXPENSE:
            transactions = Transaction.expenses.filter(
                account__user=request.user)
        account_id = request.query_params.get('account_id')
        if account_id:
            transactions = transactions.filter(account__id=account_id)
        if (request.query_params.get('begin_at')
                or request.query_params.get('end_at')):
            period_srz = PeriodSerializer(data=request.query_params)
            if not period_srz.is_valid():
                return Response(
                    period_srz.errors, status=status.HTTP_400_BAD_REQUEST)
            transactions = transactions.filter(
                date_time__gte=period_srz.validated_data['begin_at'],
                date_time__lte=period_srz.validated_data['end_at']
            )
        pagination = PageNumberCustomPagination()
        return pagination.get_paginated_response(
                TransactionSerializer(
                    pagination.paginate_queryset(
                        transactions, request, self)
                    , many=True
                ).data
            )
    
    def post(self, request):
        transaction_srz = TransactionSerializer(data=request.data)
        if not transaction_srz.is_valid():
            return Response(
                transaction_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        with dbtnsac.atomic():
            transaction = transaction_srz.save()
            account = transaction.account
            if transaction.status == Transaction.EXECUTED:
                if transaction.type == Transaction.INCOME:
                    account.balance += transaction.value
                elif transaction.type == Transaction.EXPENSE:
                    account.balance -= transaction.value
                account.save()
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
        with dbtnsac.atomic():
            last_value = transaction.value
            new_transaction = transaction_srz.save()
            account = new_transaction.account
            if transaction.status == Transaction.EXECUTED:
                if new_transaction.type == Transaction.INCOME:
                    account.balance += new_transaction.value - last_value
                elif new_transaction.type == Transaction.EXPENSE:
                    account.balance += last_value - new_transaction.value
                account.save()
            if (
                    new_transaction.value != last_value
                    and new_transaction.is_transference):
                if new_transaction.type == Transaction.EXPENSE:
                    to_transaction = (
                        new_transaction.transference_to.to_transaction)
                    to_transaction.value = new_transaction.value
                    to_transaction.save()
                elif new_transaction.type == Transaction.INCOME:
                    from_transaction = (
                        new_transaction.transference_from.from_transaction)
                    from_transaction.value = new_transaction.value
                    from_transaction.save()
        transaction_srz = TransactionSerializer(new_transaction)
        return Response(transaction_srz.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        try:
            transaction = Transaction.objects.get(
                id=id, account__user=request.user)
        except Transaction.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        account = transaction.account
        with dbtnsac.atomic():
            if transaction.status == Transaction.EXECUTED:
                if transaction.type == Transaction.INCOME:
                    account.balance -= transaction.value
                elif transaction.type == Transaction.EXPENSE:
                    account.balance += transaction.value
                account.save()
            if  transaction.is_transference:
                if transaction.type == Transaction.EXPENSE:
                    transference = transaction.transference_to
                    to_transaction = transference.to_transaction
                    transference.delete()
                    to_transaction.delete()
                elif transaction.type == Transaction.INCOME:
                    transference = transaction.transference_from
                    from_transaction = transference.from_transaction
                    transference.delete()
                    from_transaction.delete()
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

class CreditCardExpenseView(APIView):
    def get(self, request, credit_card_id, id=None):
        if id:
            try:
                expense = CreditCardExpense.objects.get(
                    id=id,
                    invoice__credit_card__id=credit_card_id,
                    invoice__expense__account__user=request.user
                )
            except CreditCardExpense.DoesNotExist:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            return Response(
                CreditCardExpenseSerializer(
                    expense).data, status=status.HTTP_200_OK)
        expense = CreditCardExpense.objects.filter(
            invoice__credit_card__id=credit_card_id,
            invoice__expense__account__user=request.user
        )
        if (request.query_params.get('begin_at')
                or request.query_params.get('end_at')):
            period_srz = PeriodSerializer(data=request.query_params)
            if not period_srz.is_valid():
                return Response(
                    period_srz.errors, status=status.HTTP_400_BAD_REQUEST)
            expense = expense.filter(
                date_time__gte=period_srz.validated_data['begin_at'],
                date_time__lte=period_srz.validated_data['end_at']
            )
        pagination = PageNumberCustomPagination()
        return pagination.get_paginated_response(
                CreditCardExpenseSerializer(
                    pagination.paginate_queryset(
                        expense, request, self)
                    , many=True
                ).data
            )
    
    def post(self, request, credit_card_id):
        expense_srz = CreditCardExpenseSerializer(data=request.data)
        if not expense_srz.is_valid():
            return Response(
                expense_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            card = CreditCard.objects.get(
                id=credit_card_id,
                account__user=request.user
            )
        except CreditCard.DoesNotExist:
            return Response(
                {'message': 'credit card not found'},
                status=status.HTTP_404_NOT_FOUND)
        with dbtnsac.atomic():
            try:
                card_invoice = CreditCardInvoice.objects.get(
                    credit_card=card,
                    period_begin__lte=(
                        expense_srz.validated_data['date_time'].date()),
                    period_end__gt=(
                        expense_srz.validated_data['date_time'].date())
                )
                card_invoice_expense = card_invoice.expense
                card_invoice_expense.value += Decimal(
                    expense_srz.validated_data['value'])
                card_invoice_expense.save()
            except CreditCardInvoice.DoesNotExist:
                invoice_date = (
                        expense_srz.validated_data['date_time'])
                invoice_date = invoice_date + relativedelta(
                    day=card.invoice_day,
                    hour=0,
                    minute=0,
                    second=0
                )
                if (
                        invoice_date
                        <= expense_srz.validated_data['date_time']):
                    invoice_date = invoice_date + relativedelta(months=1)
                due_date = invoice_date + relativedelta(day=card.due_day)
                if due_date <= invoice_date:
                    due_date = due_date + relativedelta(months=1)
                card_invoice_expense = Transaction(
                    account=card.account,
                    name=f'{card.name} invoice',
                    date_time=due_date,
                    value=Decimal(expense_srz.validated_data['value']),
                    type=Transaction.EXPENSE,
                    status=Transaction.PENDING,
                    repeat=Transaction.ONE_TIME
                )
                card_invoice_expense.save()
                date_begin = (
                        expense_srz.validated_data['date_time'].date())
                date_begin = date_begin + relativedelta(
                    day=card.invoice_day)
                date_end = date_begin + relativedelta(
                    months=1, days=-1)
                card_invoice = CreditCardInvoice(
                    credit_card=card,
                    expense=card_invoice_expense,
                    period_begin=date_begin,
                    period_end=date_end
                )
                card_invoice.save()
            expense = expense_srz.save(invoice=card_invoice)
        expense_srz = CreditCardExpenseSerializer(expense)
        return Response(expense_srz.data, status=status.HTTP_200_OK)
    
    def patch(self, request, credit_card_id, id):
        try:
            card_expense = CreditCardExpense.objects.get(
                id=id,
                invoice__credit_card__id=credit_card_id,
                invoice__credit_card__account__user=request.user
            )
        except CreditCardExpense.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        card_expense_srz = CreditCardExpenseSerializer(
            card_expense, data=request.data, partial=True)
        if not card_expense_srz.is_valid():
            return Response(
                card_expense_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        with dbtnsac.atomic():
            prev_value = card_expense.value
            new_expense = card_expense_srz.save()
            diff_value = new_expense.value - prev_value
            card_invoice_expense = card_expense.invoice.expense
            card_invoice_expense.value += diff_value 
            card_invoice_expense.save()
        card_expense_srz = CreditCardExpenseSerializer(new_expense)
        return Response(card_expense_srz.data, status=status.HTTP_200_OK)
    
    def delete(self, request, credit_card_id, id):
        try:
            card_expense = CreditCardExpense.objects.get(
                id=id,
                invoice__credit_card__id=credit_card_id,
                invoice__credit_card__account__user=request.user
            )
        except CreditCardExpense.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        with dbtnsac.atomic():
            card_invoice_expense = card_expense.invoice.expense
            card_invoice_expense.value -= card_expense.value
            if card_invoice_expense.value == Decimal(0):
                card_invoice_expense.delete()
            else:
                card_invoice_expense.save()
            card_expense.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def create_transference(request):
    transf_srz = TransferenceSerializer(data=request.data)
    if not transf_srz.is_valid():
            return Response(
                transf_srz.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        from_account = Account.objects.get(
            id=transf_srz.validated_data['from_account'],
            user=request.user
        )
    except Account.DoesNotExist:
        return Response(
            {'message': 'account from where to transfer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        to_account = Account.objects.get(
            id=transf_srz.validated_data['to_account'],
            user=request.user
        )
    except Account.DoesNotExist:
        return Response(
            {'message': 'account to receive transfer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    exp_transaction = Transaction(
        account = from_account,
        name = transf_srz.validated_data['name'],
        date_time = transf_srz.validated_data['date_time'],
        value = transf_srz.validated_data['value'],
        type = Transaction.EXPENSE,
        is_transference = True
    )
    inc_transaction = Transaction(
        account = to_account,
        name = transf_srz.validated_data['name'],
        date_time = transf_srz.validated_data['date_time'],
        value = transf_srz.validated_data['value'],
        type = Transaction.INCOME,
        is_transference = True
    )
    from_account.balance -= exp_transaction.value
    to_account.balance += inc_transaction.value
    if (exp_transaction.status == Transaction.EXECUTED
            and from_account.balance < exp_transaction.value):
        return Response(
            {'message': 'account from where to transfer have not'\
                ' enought money'},
            status=status.HTTP_400_BAD_REQUEST
        )
    with dbtnsac.atomic():
        if not transf_srz.validated_data['executed']:
            exp_transaction.status = Transaction.PENDING
            inc_transaction.status = Transaction.PENDING
        else:
            from_account.save()
            to_account.save()
        exp_transaction.save()
        inc_transaction.save()
        transference = Transference(
            from_transaction=exp_transaction,
            to_transaction=inc_transaction
        )
        transference.save()
    return Response({'message': 'transfered'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_total_balance(request):
    accounts = Account.objects.filter(
        user=request.user
    ).aggregate(dbsum('balance'))
    return Response(
        {'total_balance': accounts['balance__sum']},
        status=status.HTTP_200_OK
    )

class UserExtrasView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        userextras_srz = UserExtrasSerializer(data=request.data)
        if not userextras_srz.is_valid():
            return Response(
                userextras_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        uextras = userextras_srz.save()
        userextras_srz = UserExtrasSerializer(uextras)
        return Response(userextras_srz.data, status=status.HTTP_200_OK)
    
    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        userextras_srz = UserExtrasSerializer(
            user.userextras, data=request.data, partial=True)
        if not userextras_srz.is_valid():
            return Response(
                userextras_srz.errors, status=status.HTTP_400_BAD_REQUEST)
        new_uextras = userextras_srz.save()
        userextras_srz = UserExtrasSerializer(new_uextras)
        return Response(userextras_srz.data, status=status.HTTP_200_OK)
    
