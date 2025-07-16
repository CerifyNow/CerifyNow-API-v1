from rest_framework import serializers
from .models import Certificate, CertificateTemplate, CertificateVerification
from accounts.serializers import UserSerializer

class CertificateSerializer(serializers.ModelSerializer):
    holder = UserSerializer(read_only=True)
    issuer = UserSerializer(read_only=True)
    holder_id = serializers.UUIDField(write_only=True, required=False)
    issuer_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Certificate
        fields = '__all__'
        read_only_fields = ['id', 'certificate_id', 'blockchain_hash', 'qr_code', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set issuer to current user if not provided
        if 'issuer_id' not in validated_data:
            validated_data['issuer'] = self.context['request'].user
        else:
            validated_data['issuer_id'] = validated_data.pop('issuer_id')
        
        if 'holder_id' in validated_data:
            validated_data['holder_id'] = validated_data.pop('holder_id')
        
        return super().create(validated_data)

class CertificateCreateSerializer(serializers.ModelSerializer):
    holder_email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'title', 'description', 'certificate_type', 'institution_name',
            'institution_address', 'degree', 'field_of_study', 'grade',
            'issue_date', 'expiry_date', 'holder_email', 'certificate_file'
        ]
    
    def create(self, validated_data):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        holder_email = validated_data.pop('holder_email')
        try:
            holder = User.objects.get(email=holder_email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'holder_email': 'Bunday email bilan foydalanuvchi topilmadi'})
        
        validated_data['holder'] = holder
        validated_data['issuer'] = self.context['request'].user
        validated_data['status'] = 'issued'
        
        return super().create(validated_data)

class CertificateTemplateSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = CertificateTemplate
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class CertificateVerificationSerializer(serializers.ModelSerializer):
    certificate = CertificateSerializer(read_only=True)
    
    class Meta:
        model = CertificateVerification
        fields = '__all__'
        read_only_fields = ['verification_date']

class CertificateStatsSerializer(serializers.Serializer):
    total_certificates = serializers.IntegerField()
    verified_certificates = serializers.IntegerField()
    pending_certificates = serializers.IntegerField()
    revoked_certificates = serializers.IntegerField()
    certificates_this_month = serializers.IntegerField()
    verifications_count = serializers.IntegerField()
