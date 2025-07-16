from rest_framework import serializers
from .models import DashboardStats, SystemStats

class DashboardStatsSerializer(serializers.ModelSerializer):
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = DashboardStats
        fields = '__all__'
        read_only_fields = ['user', 'last_updated']
    
    def get_success_rate(self, obj):
        if obj.total_verifications > 0:
            return round((obj.successful_verifications / obj.total_verifications) * 100, 2)
        return 0

class SystemStatsSerializer(serializers.ModelSerializer):
    verification_success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemStats
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_verification_success_rate(self, obj):
        if obj.total_verifications > 0:
            return round((obj.successful_verifications / obj.total_verifications) * 100, 2)
        return 0

class AnalyticsOverviewSerializer(serializers.Serializer):
    # User analytics
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    students_count = serializers.IntegerField()
    organizations_count = serializers.IntegerField()
    admins_count = serializers.IntegerField()
    
    # Certificate analytics
    total_certificates = serializers.IntegerField()
    verified_certificates = serializers.IntegerField()
    pending_certificates = serializers.IntegerField()
    certificates_this_month = serializers.IntegerField()
    
    # Verification analytics
    total_verifications = serializers.IntegerField()
    successful_verifications = serializers.IntegerField()
    verification_success_rate = serializers.FloatField()
    verifications_this_month = serializers.IntegerField()
    
    # Growth analytics
    user_growth_rate = serializers.FloatField()
    certificate_growth_rate = serializers.FloatField()
