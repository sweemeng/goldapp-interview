from django.conf.urls import url, include
from .views import BalanceListView
from .views import TransactionListView
from .views import TransactionBuyView
from .views import TransactionSellView
from .views import TransactionTopUpView
from .views import TransactionWithdrawView


urlpatterns = [
    url(r'^balances$', BalanceListView.as_view(), name='balance_list'),
    url(r'^transactions$', TransactionListView.as_view(), name='transaction_list'),
    url(r'^transactions/buy$', TransactionBuyView.as_view(), name='transaction_buy'),
    url(r'^transactions/sell$', TransactionSellView.as_view(), name='transaction_sell'),
    url(r'^transactions/top_up$', TransactionTopUpView.as_view(), name='transaction_top_up'),
    url(r'^transactions/withdraw$', TransactionWithdrawView.as_view(), name='transaction_withdraw'),
]
