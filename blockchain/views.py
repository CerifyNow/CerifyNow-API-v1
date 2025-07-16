from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Sum
from .models import BlockchainTransaction, BlockchainBlock, SmartContract
from .serializers import (
    BlockchainTransactionSerializer, BlockchainBlockSerializer,
    SmartContractSerializer
)

class BlockchainTransactionListView(generics.ListAPIView):
    serializer_class = BlockchainTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['transaction_type', 'status', 'certificate']
    search_fields = ['transaction_hash', 'certificate__certificate_id']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return BlockchainTransaction.objects.all()
        elif user.role == 'organization':
            return BlockchainTransaction.objects.filter(certificate__issuer=user)
        else:
            return BlockchainTransaction.objects.filter(certificate__holder=user)

class BlockchainTransactionDetailView(generics.RetrieveAPIView):
    queryset = BlockchainTransaction.objects.all()
    serializer_class = BlockchainTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_hash'

class BlockchainBlockListView(generics.ListAPIView):
    queryset = BlockchainBlock.objects.all()
    serializer_class = BlockchainBlockSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-block_number']

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def blockchain_stats(request):
    """Get blockchain statistics"""
    if request.user.role != 'admin':
        return Response(
            {'error': 'Faqat administratorlar bu ma\'lumotni ko\'ra oladi'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Transaction stats
    total_transactions = BlockchainTransaction.objects.count()
    confirmed_transactions = BlockchainTransaction.objects.filter(status='confirmed').count()
    pending_transactions = BlockchainTransaction.objects.filter(status='pending').count()
    failed_transactions = BlockchainTransaction.objects.filter(status='failed').count()
    
    # Block stats
    total_blocks = BlockchainBlock.objects.count()
    latest_block = BlockchainBlock.objects.first()
    
    # Gas stats
    total_gas_used = BlockchainTransaction.objects.aggregate(
        total=Sum('gas_used')
    )['total'] or 0
    
    # Transaction type distribution
    transaction_types = BlockchainTransaction.objects.values('transaction_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    stats = {
        'transactions': {
            'total': total_transactions,
            'confirmed': confirmed_transactions,
            'pending': pending_transactions,
            'failed': failed_transactions,
        },
        'blocks': {
            'total': total_blocks,
            'latest_block_number': latest_block.block_number if latest_block else 0,
        },
        'gas': {
            'total_used': total_gas_used,
            'average_per_transaction': total_gas_used / total_transactions if total_transactions > 0 else 0,
        },
        'transaction_types': transaction_types,
    }
    
    return Response(stats)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_transaction(request, transaction_hash):
    """Verify a blockchain transaction"""
    try:
        transaction = BlockchainTransaction.objects.get(transaction_hash=transaction_hash)
        
        # Mock verification process
        if transaction.status == 'pending':
            transaction.status = 'confirmed'
            transaction.confirmations = 12
            transaction.save()
        
        serializer = BlockchainTransactionSerializer(transaction)
        return Response({
            'message': 'Tranzaksiya tasdiqlandi',
            'transaction': serializer.data
        })
        
    except BlockchainTransaction.DoesNotExist:
        return Response(
            {'error': 'Tranzaksiya topilmadi'},
            status=status.HTTP_404_NOT_FOUND
        )

class SmartContractListView(generics.ListAPIView):
    queryset = SmartContract.objects.filter(is_active=True)
    serializer_class = SmartContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['contract_type', 'is_verified']
    search_fields = ['name', 'address']
    ordering = ['-created_at']
