from rest_framework import serializers
from .models import (
    CrisisRequest, VolunteerProfile, Donation, Assignment,
    DisasterType, ResourceType, NGOProfile, Shelter, EmergencyAlert,
    ResourceInventory, Notification, Feedback, SafetyTip, EmergencyContact
)
from django.contrib.auth import get_user_model

User = get_user_model()


class DisasterTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisasterType
        fields = '__all__'


class ResourceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceType
        fields = '__all__'


class NGOProfileSerializer(serializers.ModelSerializer):
    specialization = DisasterTypeSerializer(many=True, read_only=True)
    available_resources = ResourceTypeSerializer(many=True, read_only=True)
    
    class Meta:
        model = NGOProfile
        fields = '__all__'


class ShelterSerializer(serializers.ModelSerializer):
    available_capacity = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    managed_by_name = serializers.CharField(source='managed_by.organization_name', read_only=True)
    
    def get_available_capacity(self, obj):
        return obj.available_capacity()
    
    def get_is_available(self, obj):
        return obj.is_available()
    
    class Meta:
        model = Shelter
        fields = '__all__'


class EmergencyAlertSerializer(serializers.ModelSerializer):
    disaster_type_name = serializers.CharField(source='disaster_type.name', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.username', read_only=True)
    
    class Meta:
        model = EmergencyAlert
        fields = '__all__'


class CrisisRequestSerializer(serializers.ModelSerializer):
    disaster_type_name = serializers.CharField(source='disaster_type.name', read_only=True)
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    assigned_ngo_name = serializers.CharField(source='assigned_ngo.organization_name', read_only=True)
    
    class Meta:
        model = CrisisRequest
        fields = '__all__'


class VolunteerProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    primary_skill_display = serializers.CharField(source='get_primary_skill_display', read_only=True)
    affiliated_ngo_name = serializers.CharField(source='affiliated_ngo.organization_name', read_only=True)

    class Meta:
        model = VolunteerProfile
        fields = '__all__'


class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source='donor.username', read_only=True)
    
    class Meta:
        model = Donation
        fields = '__all__'


class AssignmentSerializer(serializers.ModelSerializer):
    volunteer_name = serializers.CharField(source='volunteer.user.username', read_only=True)
    request_details = CrisisRequestSerializer(source='request', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Assignment
        fields = '__all__'


class ResourceInventorySerializer(serializers.ModelSerializer):
    resource_name = serializers.CharField(source='resource_type.name', read_only=True)
    ngo_name = serializers.CharField(source='ngo.organization_name', read_only=True)
    
    class Meta:
        model = ResourceInventory
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.username', read_only=True)
    
    class Meta:
        model = Feedback
        fields = '__all__'


class SafetyTipSerializer(serializers.ModelSerializer):
    disaster_type_name = serializers.CharField(source='disaster_type.name', read_only=True)
    
    class Meta:
        model = SafetyTip
        fields = '__all__'


class EmergencyContactSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = EmergencyContact
        fields = '__all__'
