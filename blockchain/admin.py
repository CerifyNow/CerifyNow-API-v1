from django.contrib import admin
from .models import BlockchainTransaction, BlockchainBlock, SmartContract


@admin.register(BlockchainTransaction)
class BlockchainTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_type',
        'transaction_hash_short',
        'certificate',
        'from_address',
        'to_address',
        'status',
        'confirmations',
        'is_confirmed',
        'created_at',
    )
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('transaction_hash', 'from_address', 'to_address', 'certificate__title')
    readonly_fields = ('transaction_hash', 'transaction_fee_eth', 'created_at', 'confirmed_at')

    def transaction_hash_short(self, obj):
        return obj.transaction_hash[:10] + '...'
    transaction_hash_short.short_description = "Tranzaksiya hash"


@admin.register(BlockchainBlock)
class BlockchainBlockAdmin(admin.ModelAdmin):
    list_display = (
        'block_number',
        'block_hash_short',
        'parent_hash_short',
        'timestamp',
        'miner',
        'gas_used',
        'transaction_count',
    )
    search_fields = ('block_hash', 'parent_hash', 'miner')
    list_filter = ('timestamp',)
    readonly_fields = ('created_at',)

    def block_hash_short(self, obj):
        return obj.block_hash[:10] + '...'
    block_hash_short.short_description = "Blok hash"

    def parent_hash_short(self, obj):
        return obj.parent_hash[:10] + '...'
    parent_hash_short.short_description = "Ota blok hash"


@admin.register(SmartContract)
class SmartContractAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'contract_type',
        'address_short',
        'deployed_by',
        'is_active',
        'is_verified',
        'created_at',
    )
    search_fields = ('name', 'address', 'deployed_by__email')
    list_filter = ('contract_type', 'is_active', 'is_verified')
    readonly_fields = ('created_at', 'updated_at')

    def address_short(self, obj):
        return obj.address[:10] + '...'
    address_short.short_description = "Kontrakt manzili"
