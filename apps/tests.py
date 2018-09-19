from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate
from .models import Transaction
from .models import Balance
from .models import Asset
from .factory import UserFactory
from .factory import GoldFactory
from .factory import CashFactory
from .factory import GoldBalanceFactory
from .factory import CashBalanceFactory
from .factory import UserFactory
from .views import TransactionViewSet
from .views import BalanceListView
from .views import TransactionListView
from .views import TransactionBuyView
from .views import TransactionSellView
from .views import TransactionTopUpView
from .views import TransactionWithdrawView



# Create your tests here.
class TransactionTestCase(TestCase):
    def setUp(self):
        self.gold         = GoldFactory()
        self.cash         = CashFactory()
        
        # When user is created, balance is created for each asset
        # When asset is created, balance is created for each user for said asset
        # All is done on asset on models.py
        self.owner        = UserFactory()
        self.gold_balance = Balance.objects.get(owner=self.owner, asset=self.gold)
        self.gold_balance.amount = 1000
        self.gold_balance.save()
        self.cash_balance = Balance.objects.get(owner=self.owner, asset=self.cash)
        self.cash_balance.amount = 1000
        self.cash_balance.save()

        self.owner_low_gold = UserFactory()
        self.low_gold_bal  = Balance.objects.get(owner=self.owner_low_gold, asset=self.gold)
        self.norm_cash_bal = Balance.objects.get(owner=self.owner_low_gold, asset=self.cash)
        self.norm_cash_bal.amount = 1000
        self.norm_cash_bal.save()

        self.owner_low_cash = UserFactory()
        self.low_cash_bal = Balance.objects.get(owner=self.owner_low_cash, asset=self.cash)
        self.norm_gold_bal = Balance.objects.get(owner=self.owner_low_cash, asset=self.gold)
        self.norm_gold_bal.amount = 1000
        self.norm_gold_bal.save()

    def test_buy_transaction(self):
        # this is to test buying gold
        gold_bal    = self.gold_balance.amount
        cash_bal    = self.cash_balance.amount
        
        transaction = Transaction(
                type   = "buy",
                amount = 10,
                asset  = "gold",
                owner  = self.owner
        )
        transaction.save()
        new_gold_bal = self.gold_balance.amount
        new_cash_bal = self.cash_balance.amount
        self.assertEqual(transaction.status, Transaction.PENDING)

    def test_buy_transaction_low_cash(self):
        transaction = Transaction(
                type   = "buy",
                amount = 10,
                asset  = "gold",
                owner  = self.owner_low_cash
        )

        transaction.save()
        self.assertEqual(transaction.status, Transaction.DENIED)

    def test_approve_buy_transaction(self):
        gold_bal     = self.gold_balance.amount
        cash_bal     = self.cash_balance.amount
        
        transaction = Transaction(
                type   = "buy",
                amount = 10,
                asset  = "gold",
                owner  = self.owner
        )
        transaction.save()
        transaction.status = Transaction.APPROVED
        transaction.save()
        gold_balance = Balance.objects.get(asset=self.gold, owner=self.owner)
        cash_balance = Balance.objects.get(asset=self.cash, owner=self.owner)
        new_gold_bal = gold_balance.amount
        new_cash_bal = cash_balance.amount
        
        gold_expected = gold_bal + 10
        cash_expected = cash_bal - (10 * 10)
        self.assertEqual(new_gold_bal, gold_expected)
        self.assertEqual(new_cash_bal, cash_expected)

    def test_reject_buy_transaction(self):
        gold_bal    = self.gold_balance.amount
        cash_bal    = self.cash_balance.amount
        
        transaction = Transaction(
                type   = "buy",
                amount = 10,
                asset  = "gold",
                owner  = self.owner
        )
        transaction.save()
        transaction.status = Transaction.DENIED
        transaction.save()
        new_gold_bal = self.gold_balance.amount
        new_cash_bal = self.cash_balance.amount
        
        self.assertEqual(new_gold_bal, gold_bal)
        self.assertEqual(new_cash_bal, cash_bal)

    def test_sell_transaction(self):
        
        transaction = Transaction(
                type   = "sell",
                amount = 10,
                asset  = "gold",
                owner  = self.owner
        )
        transaction.save()

        self.assertEqual(transaction.status, Transaction.PENDING)

    def test_sell_transaction_low_gold(self):
        transaction = Transaction(
                type   = "sell",
                amount = 10,
                asset  = "gold",
                owner  = self.owner_low_gold
        )
        transaction.save()

        self.assertEqual(transaction.status, Transaction.DENIED)

    def test_approve_sell_transaction(self):
        gold_bal    = self.gold_balance.amount
        cash_bal    = self.cash_balance.amount
        
        transaction = Transaction(
                type   = "sell",
                amount = 10,
                asset  = "gold",
                owner  = self.owner
        )
        transaction.save()
        transaction.status = Transaction.APPROVED
        transaction.save()
        gold_balance = Balance.objects.get(owner=self.owner, asset=self.gold)
        cash_balance = Balance.objects.get(owner=self.owner, asset=self.cash)
        new_gold_bal = gold_balance.amount
        new_cash_bal = cash_balance.amount
        
        gold_expected = gold_bal - 10
        cash_expected = cash_bal + (10 * 10)
        self.assertEqual(new_gold_bal, gold_expected)
        self.assertEqual(new_cash_bal, cash_expected)

    def test_reject_sell_transaction(self):
        gold_bal    = self.gold_balance.amount
        cash_bal    = self.cash_balance.amount
        
        transaction = Transaction(
                type   = "sell",
                amount = 10,
                asset  = "gold",
                owner  = self.owner
        )
        transaction.save()
        transaction.status = Transaction.DENIED
        transaction.save()
        new_gold_bal = self.gold_balance.amount
        new_cash_bal = self.cash_balance.amount
        
        self.assertEqual(new_gold_bal, gold_bal)
        self.assertEqual(new_cash_bal, cash_bal)

    def test_top_up_transaction(self):
        cash_bal = self.cash_balance.amount
        transaction = Transaction(
                type   = "top_up",
                amount = 10,
                asset  = "cash",
                owner  = self.owner
        )
        transaction.save()
        self.assertEqual(transaction.status, Transaction.PENDING)

    def test_approve_top_up_transaction(self):
        cash_bal = self.cash_balance.amount
        transaction = Transaction(
                type   = "top_up",
                amount = 10,
                asset  = "cash",
                owner  = self.owner
        )
        transaction.save()
        transaction.status = Transaction.APPROVED
        transaction.save()
        balance = Balance.objects.get(owner=self.owner, asset=self.cash)
        new_cash = balance.amount
        cash_expected = cash_bal + 10
        self.assertEqual(new_cash, cash_expected)

    def test_deny_top_up_transaction(self):
        cash_bal = self.cash_balance.amount
        transaction = Transaction(
                type   = "top_up",
                amount = 10,
                asset  = "cash",
                owner  = self.owner
        )
        transaction.save()
        transaction.status = Transaction.DENIED
        transaction.save()
        balance = Balance.objects.get(owner=self.owner, asset=self.cash)
        new_cash = balance.amount
        self.assertEqual(new_cash, cash_bal)

    def test_withdraw_transaction(self):
        transaction = Transaction(
                type   = "withdraw",
                amount = 10,
                asset  = "cash",
                owner  = self.owner
        )
        transaction.save()
        self.assertEqual(transaction.status, Transaction.PENDING)

    def test_withdraw_transaction_low_cash(self):
        transaction = Transaction(
                type   = "withdraw",
                amount = 10,
                asset  = "cash",
                owner  = self.owner_low_cash
        )
        transaction.save()
        self.assertEqual(transaction.status, Transaction.DENIED)

    def test_approve_withdraw_transaction(self):
        cash_bal = self.cash_balance.amount
        transaction = Transaction(
                type   = "withdraw",
                amount = 10,
                asset  = "cash",
                owner  = self.owner
        )
        transaction.save()
        transaction.status = Transaction.APPROVED
        transaction.save()

        cash_balance = Balance.objects.get(owner__id=self.owner.id, asset__id=self.cash.id)
        new_cash = cash_balance.amount
        cash_expected = cash_bal - transaction.amount
        self.assertEqual(transaction.status, Transaction.APPROVED)
        self.assertEqual(new_cash, cash_expected)

    def test_deny_withdraw_transaction(self):
        cash_bal = self.cash_balance.amount
        transaction = Transaction(
                type   = "withdraw",
                amount = 10,
                asset  = "cash",
                owner  = self.owner
        )
        transaction.save()
        transaction.status = Transaction.DENIED
        transaction.save()
        
        balance  = Balance.objects.get(asset=self.cash, owner=self.owner)
        new_cash = balance.amount
        self.assertEqual(new_cash, cash_bal)


# No change in balance as all status is not approved yet. 
# except when user is created or asset is created
# That is done on admin
class APIRequestTestCase(APITestCase):
    def setUp(self):
        # Setup date
        self.gold         = GoldFactory()
        self.cash         = CashFactory()

        # When user is created, balance is created for each asset
        # When asset is created, balance is created for each user for said asset
        # All is done on asset on models.py
        self.owner        = UserFactory()
        self.gold_balance = Balance.objects.get(owner=self.owner, asset=self.gold)
        self.gold_balance.amount = 1000
        self.gold_balance.save()
        self.cash_balance = Balance.objects.get(owner=self.owner, asset=self.cash)
        self.cash_balance.amount = 1000
        self.cash_balance.save()

        self.owner_low_gold = UserFactory()
        self.low_gold_bal  = Balance.objects.get(owner=self.owner_low_gold, asset=self.gold)
        self.norm_cash_bal = Balance.objects.get(owner=self.owner_low_gold, asset=self.cash)
        self.norm_cash_bal.amount = 1000
        self.norm_cash_bal.save()

        self.owner_low_cash = UserFactory()
        self.low_cash_bal = Balance.objects.get(owner=self.owner_low_cash, asset=self.cash)
        self.norm_gold_bal = Balance.objects.get(owner=self.owner_low_cash, asset=self.gold)
        self.norm_gold_bal.amount = 1000
        self.norm_gold_bal.save()
        # Now the request factory
        self.api_factory = APIRequestFactory()

    def test_buy_gold(self):
        data = {
            "type"   : "buy",
            "asset"  : "gold",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/buy", data)
        force_authenticate(request, user=self.owner)
        transaction_view = TransactionBuyView.as_view()
        response = transaction_view(request)
        transaction = Transaction.objects.get()

        self.assertEqual(transaction.status, Transaction.PENDING)

    def test_low_cash_owner_buy_gold(self):
        data = {
            "type"   : "buy",
            "asset"  : "gold",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/buy", data)
        force_authenticate(request, user=self.owner_low_cash)
        transaction_view = TransactionBuyView.as_view()
        response = transaction_view(request)
        transaction = Transaction.objects.get()
        
        self.assertEqual(transaction.status, Transaction.DENIED)

    def test_low_cash_owner_buy_gold_status(self):
        data = {
            "type"   : "buy",
            "asset"  : "gold",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/buy", data)
        force_authenticate(request, user=self.owner_low_cash)
        transaction_view = TransactionBuyView.as_view()
        response = transaction_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_buy_gold_status(self):
        data = {
            "type"   : "buy",
            "asset"  : "gold",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/buy", data)
        force_authenticate(request, user=self.owner)
        transaction_view = TransactionBuyView.as_view()
        response = transaction_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_sell_gold(self):
        data = {
            "type"   : "sell",
            "asset"  : "gold",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/sell", data)
        force_authenticate(request, user=self.owner)
        transaction_view = TransactionSellView.as_view()
        response = transaction_view(request)
        transaction = Transaction.objects.get()

        self.assertEqual(transaction.status, Transaction.PENDING)

    def test_low_gold_owner_sell_gold(self):
        data = {
            "type"   : "sell",
            "asset"  : "gold",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/sell", data)
        force_authenticate(request, user=self.owner_low_gold)
        transaction_view = TransactionSellView.as_view()
        response = transaction_view(request)
        transaction = Transaction.objects.get()

        self.assertEqual(transaction.status, Transaction.DENIED)

    def test_low_gold_owner_sell_gold_status(self):
        data = {
            "type"   : "sell",
            "asset"  : "gold",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/sell", data)
        force_authenticate(request, user=self.owner_low_gold)
        transaction_view = TransactionSellView.as_view()
        response = transaction_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_sell_gold_status(self):
        data = {
            "type"   : "sell",
            "asset"  : "gold",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/sell", data)
        force_authenticate(request, user=self.owner)
        transaction_view = TransactionSellView.as_view()
        response = transaction_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_sell_cash_at_sell_gold_status(self):
        data = {
            "type"   : "sell",
            "asset"  : "cash",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/sell", data)
        force_authenticate(request, user=self.owner)
        transaction_view = TransactionSellView.as_view()
        response = transaction_view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_cash_at_sell_gold_status(self):
        data = {
            "type"   : "buy",
            "asset"  : "cash",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/sell", data)
        force_authenticate(request, user=self.owner)
        transaction_view = TransactionSellView.as_view()
        response = transaction_view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_withdraw_cash(self):
        data = {
            "type"   : "withdraw",
            "asset"  : "cash",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/withdraw", data)
        force_authenticate(request, user=self.owner)
        transaction_view = TransactionWithdrawView.as_view()
        response = transaction_view(request)
        transaction = Transaction.objects.get()

        self.assertEqual(transaction.status, Transaction.PENDING)

    def test_low_cash_owner_withdraw_cash(self):
        data = {
            "type"   : "withdraw",
            "asset"  : "cash",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/withdraw", data)
        force_authenticate(request, user=self.owner_low_cash)
        transaction_view = TransactionWithdrawView.as_view()
        response = transaction_view(request)
        transaction = Transaction.objects.get()

        self.assertEqual(transaction.status, Transaction.DENIED)

    def test_withdraw_cash_status(self):
        data = {
            "type"   : "withdraw",
            "asset"  : "cash",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/withdraw", data)
        force_authenticate(request, user=self.owner)
        transaction_view = TransactionWithdrawView.as_view()
        response = transaction_view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_low_cash_owner_withdraw_cash_status(self):
        data = {
            "type"   : "withdraw",
            "asset"  : "cash",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/withdraw", data)
        force_authenticate(request, user=self.owner_low_cash)
        transaction_view = TransactionWithdrawView.as_view()
        response = transaction_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_top_up(self):
        data = {
            "type"   : "top_up",
            "asset"  : "cash",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/top_up", data)
        force_authenticate(request, user=self.owner)
        transaction_view = TransactionTopUpView.as_view()
        response = transaction_view(request)
        transaction = Transaction.objects.get()

        self.assertEqual(transaction.status, Transaction.PENDING)

    def test_top_up_status(self):
        data = {
            "type"   : "top_up",
            "asset"  : "cash",
            "amount" : 10
        }
        request = self.api_factory.post("/api/transactions/top_up", data)
        force_authenticate(request, user=self.owner)
        transaction_view = TransactionTopUpView.as_view()
        response = transaction_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_balance_status(self):
        request = self.api_factory.get("/api/balances")
        force_authenticate(request, user=self.owner)
        transaction_view = BalanceListView.as_view()
        response = transaction_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_transaction_list_status(self):
        request = self.api_factory.get("/api/transactions")
        force_authenticate(request, user=self.owner)
        transaction_view = TransactionListView.as_view()
        response = transaction_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_balance_data(self):
        request = self.api_factory.get("/api/balances")
        force_authenticate(request, user=self.owner)
        transaction_view = BalanceListView.as_view()
        response = transaction_view(request)
        
        data = response.data
        self.assertEqual(data["GLD"], 1000)
        self.assertEqual(data["CASH"], 1000)


