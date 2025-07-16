from rest_framework import serializers
from .models import Organization, OrganizationMembership
from accounts.serializers import UserSerializer

class OrganizationSerializer(serializers.ModelSerializer):
    admin_users = UserSerializer(many=True, read_only=True)
    certificates_count = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_certificates_count(self, obj):
        return obj.issued_certificates.count() if hasattr(obj, 'issued_certificates') else 0
    
    def get_members_count(self, obj):
        return obj.memberships.filter(is_active=True).count()

class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)
    
    class Meta:
        model = OrganizationMembership
        fields = '__all__'
        read_only_fields = ['joined_at']

class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'name', 'short_name', 'organization_type', 'email', 'phone',
            'website', 'address', 'city', 'region', 'postal_code',
            'license_number', 'tax_id', 'registration_number',
            'logo', 'description', 'established_date'
        ]
