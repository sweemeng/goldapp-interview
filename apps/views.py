from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework import status
from .models import Transaction
from .models import Balance
from .serializers import TransactionSerializer


class BalanceListView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    def get(self, request, format=None):
        balances = Balance.objects.filter(owner=request.user.id)
        data = {}
        for balance in balances:
            data[balance.asset.display_name] = balance.amount
        return Response(data)


class TransactionListView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(owner__id=self.request.user.id)


class GenericTransactionView(CreateAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    asset              = None
    transaction_type   = None
    serializer_class = TransactionSerializer



    def create(self, request, *args, **kwargs):
        assert self.asset, "Please init asset when inherit class" 
        assert self.transaction_type, "Please init transaction when inherit class" 

        data                = request.data
        transaction_allowed = False
        error_msg           = "only allow {transaction_type} for {asset}".format(
            transaction_type = self.transaction_type,
            asset            = self.asset
        )
        if data['type'] == self.transaction_type and data['asset'] == self.asset :
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save(owner=self.request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)


class TransactionBuyView(GenericTransactionView):
    asset            = "gold"
    transaction_type = "buy"


class TransactionSellView(GenericTransactionView):
    asset            = "gold"
    transaction_type = "sell"


class TransactionWithdrawView(GenericTransactionView):
    asset            = "cash"
    transaction_type = "withdraw"


class TransactionTopUpView(GenericTransactionView):
    asset            = "cash"
    transaction_type = "top_up"


class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(owner__id=self.request.user.id)

    @action(detail=False, methods=['post'])
    def top_up(self, request):
        data = request.data
        if data["type"] == 'top_up':
            serializer = self.serializer_class(data)
            if serializer.is_valid():
                serializer.save(owner=self.request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "only topup cash"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def buy(self, request):
        data = request.data
        if data['type'] == 'buy':
            serializer = self.serializer_class(data)
            if serializer.is_valid():
                serializer.save(owner=self.request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "only buy request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def sell(self, request):
        data = request.data
        if data['type'] == 'sell':
            serializer = self.serializer_class(data)
            if serializer.is_valid():
                serializer.save(owner=self.request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "only sell request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        data = request.data
        if data['type'] == 'withdraw':
            serializer = self.serializer_class(data)
            if serializer.is_valid():
                serializer.save(owner=self.request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "only withdraw request"}, status=status.HTTP_400_BAD_REQUEST)
