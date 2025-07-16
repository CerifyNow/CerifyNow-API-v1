from rest_framework import serializers
from .models import BlockchainTransaction, BlockchainBlock, SmartContract

class BlockchainTransactionSerializer(serializers.ModelSerializer):
    transaction_fee_eth = serializers.ReadOnlyField()
    is_confirmed = serializers.ReadOnlyField()
    
    class Meta:
        model = BlockchainTransaction
        fields = '__all__'
        read_only_fields = [
            'id', 'transaction_hash', 'block_number', 'block_hash',
            'created_at', 'confirmed_at', 'confirmations'
        ]

class BlockchainBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockchainBlock
        fields = '__all__'
        read_only_fields = ['created_at']

class SmartContractSerializer(serializers.ModelSerializer):
    deployed_by_name = serializers.CharField(source='deployed_by.full_name', read_only=True)
    
    class Meta:
        model = SmartContract
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
