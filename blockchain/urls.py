from django.urls import path
from .views import (
    BlockchainTransactionListView, BlockchainTransactionDetailView,
    BlockchainBlockListView, blockchain_stats, verify_transaction,
    SmartContractListView
)

urlpatterns = [
    path('transactions/', BlockchainTransactionListView.as_view(), name='blockchain-transactions'),
    path('transactions/<str:transaction_hash>/', BlockchainTransactionDetailView.as_view(), name='blockchain-transaction-detail'),
    path('transactions/<str:transaction_hash>/verify/', verify_transaction, name='verify-transaction'),
    path('blocks/', BlockchainBlockListView.as_view(), name='blockchain-blocks'),
    path('contracts/', SmartContractListView.as_view(), name='smart-contracts'),
    path('stats/', blockchain_stats, name='blockchain-stats'),
]
