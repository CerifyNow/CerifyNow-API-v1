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
    certificate_id = serializers.CharField(max_length=50, required=False)
    certificate_hash = serializers.CharField(max_length=255, required=False)
    requester_email = serializers.EmailField(required=False)
    requester_organization = serializers.CharField(max_length=255, required=False)

    def validate(self, attrs):
        certificate_id = attrs.get('certificate_id')
        certificate_hash = attrs.get('certificate_hash')

        if not certificate_id and not certificate_hash:
            raise serializers.ValidationError(
                'certificate_id yoki certificate_hash dan biri talab qilinadi'
            )

        return attrs


class QRVerificationSerializer(serializers.Serializer):
    """Serializer for QR code verification response"""
    is_valid = serializers.BooleanField()
    certificate = serializers.DictField(required=False)
    verification = serializers.DictField(required=False)
    message = serializers.CharField(required=False)
    error_code = serializers.CharField(required=False)
