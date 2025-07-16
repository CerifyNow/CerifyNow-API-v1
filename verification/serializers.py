from rest_framework import serializers
from .models import VerificationRequest, VerificationLog
from certificates.serializers import CertificateSerializer

class VerificationRequestSerializer(serializers.ModelSerializer):
    certificate = CertificateSerializer(read_only=True)
    
    class Meta:
        model = VerificationRequest
        fields = '__all__'
        read_only_fields = ['verification_date', 'verification_result']

class VerificationLogSerializer(serializers.ModelSerializer):
    certificate = CertificateSerializer(read_only=True)
    
    class Meta:
        model = VerificationLog
        fields = '__all__'
        read_only_fields = ['timestamp']

class CertificateVerifySerializer(serializers.Serializer):
    certificate_id = serializers.CharField(max_length=50)
    requester_email = serializers.EmailField(required=False)
    requester_organization = serializers.CharField(max_length=255, required=False)
