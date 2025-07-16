from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from certificates.models import Certificate
import uuid
import hashlib
import json
from datetime import datetime

User = get_user_model()

class BlockchainTransaction(models.Model):
    """Mock blockchain transaction model"""
    TRANSACTION_TYPES = [
        ('certificate_issue', _('Sertifikat chiqarish')),
        ('certificate_verify', _('Sertifikat tasdiqlash')),
        ('certificate_revoke', _('Sertifikat bekor qilish')),
        ('certificate_transfer', _('Sertifikat o\'tkazish')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Kutilmoqda')),
        ('confirmed', _('Tasdiqlangan')),
        ('failed', _('Muvaffaqiyatsiz')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_hash = models.CharField(_('Tranzaksiya hash'), max_length=66, unique=True)
    block_number = models.BigIntegerField(_('Blok raqami'), null=True, blank=True)
    block_hash = models.CharField(_('Blok hash'), max_length=66, blank=True)
    
    # Transaction details
    transaction_type = models.CharField(_('Tranzaksiya turi'), max_length=30, choices=TRANSACTION_TYPES)
    from_address = models.CharField(_('Yuboruvchi manzil'), max_length=42)
    to_address = models.CharField(_('Qabul qiluvchi manzil'), max_length=42, blank=True)
    
    # Related certificate
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='blockchain_transactions')
    
    # Transaction data
    transaction_data = models.JSONField(_('Tranzaksiya ma\'lumotlari'), default=dict)
    
    # Gas and fees (mock)
    gas_used = models.BigIntegerField(_('Ishlatilgan gaz'), default=21000)
    gas_price = models.BigIntegerField(_('Gaz narxi'), default=20000000000)  # 20 Gwei
    transaction_fee = models.DecimalField(_('Tranzaksiya to\'lovi'), max_digits=20, decimal_places=8, default=0)
    
    # Status and timestamps
    status = models.CharField(_('Holat'), max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(_('Yaratilgan'), auto_now_add=True)
    confirmed_at = models.DateTimeField(_('Tasdiqlangan'), null=True, blank=True)
    
    # Confirmations
    confirmations = models.IntegerField(_('Tasdiqlar soni'), default=0)
    required_confirmations = models.IntegerField(_('Kerakli tasdiqlar'), default=12)
    
    class Meta:
        verbose_name = _('Blokcheyn tranzaksiyasi')
        verbose_name_plural = _('Blokcheyn tranzaksiyalari')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['certificate', 'status']),
            models.Index(fields=['block_number']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_hash[:10]}..."
    
    def save(self, *args, **kwargs):
        if not self.transaction_hash:
            self.transaction_hash = self.generate_transaction_hash()
        super().save(*args, **kwargs)
    
    def generate_transaction_hash(self):
        """Generate a mock transaction hash"""
        data = {
            'certificate_id': str(self.certificate.id),
            'transaction_type': self.transaction_type,
            'from_address': self.from_address,
            'timestamp': datetime.now().isoformat(),
            'nonce': str(uuid.uuid4())
        }
        return '0x' + hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    @property
    def is_confirmed(self):
        return self.confirmations >= self.required_confirmations
    
    @property
    def transaction_fee_eth(self):
        """Convert transaction fee to ETH (mock)"""
        return float(self.gas_used * self.gas_price) / 10**18

class BlockchainBlock(models.Model):
    """Mock blockchain block model"""
    block_number = models.BigIntegerField(_('Blok raqami'), unique=True)
    block_hash = models.CharField(_('Blok hash'), max_length=66, unique=True)
    parent_hash = models.CharField(_('Ota-blok hash'), max_length=66)
    
    # Block metadata
    timestamp = models.DateTimeField(_('Vaqt belgisi'))
    miner = models.CharField(_('Miner'), max_length=42)
    difficulty = models.BigIntegerField(_('Qiyinchilik'), default=1000000)
    gas_limit = models.BigIntegerField(_('Gaz limiti'), default=8000000)
    gas_used = models.BigIntegerField(_('Ishlatilgan gaz'), default=0)
    
    # Transactions in this block
    transaction_count = models.IntegerField(_('Tranzaksiyalar soni'), default=0)
    
    # Merkle root of transactions
    transactions_root = models.CharField(_('Tranzaksiyalar root'), max_length=66)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Blokcheyn bloki')
        verbose_name_plural = _('Blokcheyn bloklari')
        ordering = ['-block_number']
    
    def __str__(self):
        return f"Block #{self.block_number}"

class SmartContract(models.Model):
    """Mock smart contract model"""
    CONTRACT_TYPES = [
        ('certificate_registry', _('Sertifikat reestri')),
        ('organization_registry', _('Tashkilot reestri')),
        ('verification_contract', _('Tekshiruv kontrakti')),
    ]
    
    name = models.CharField(_('Nomi'), max_length=255)
    contract_type = models.CharField(_('Turi'), max_length=30, choices=CONTRACT_TYPES)
    address = models.CharField(_('Kontrakt manzili'), max_length=42, unique=True)
    
    # Contract metadata
    abi = models.JSONField(_('ABI'), default=list)
    bytecode = models.TextField(_('Bytecode'), blank=True)
    source_code = models.TextField(_('Manba kodi'), blank=True)
    
    # Deployment info
    deployed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    deployment_transaction = models.CharField(_('Deploy tranzaksiyasi'), max_length=66, blank=True)
    deployment_block = models.BigIntegerField(_('Deploy bloki'), null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(_('Faol'), default=True)
    is_verified = models.BooleanField(_('Tasdiqlangan'), default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Smart kontrakt')
        verbose_name_plural = _('Smart kontraktlar')
    
    def __str__(self):
        return f"{self.name} ({self.address[:10]}...)"
