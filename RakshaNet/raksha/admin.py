from django.contrib import admin
from .models import (
    CrisisRequest, VolunteerProfile, Donation, DonationMedia, Assignment,
    DisasterType, ResourceType, NGOProfile, Shelter, EmergencyAlert,
    ResourceInventory, Notification, Feedback, EmergencyContact, SafetyTip,
    CrisisChatMessage, CommunityChannel, CommunityMessage, AIChatMessage,
    UserLocationPing, EmergencyBeacon
)


@admin.register(DisasterType)
class DisasterTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'severity_multiplier', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')


@admin.register(ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit_of_measurement')
    list_filter = ('category',)
    search_fields = ('name', 'description')


@admin.register(NGOProfile)
class NGOProfileAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'contact_person', 'phone', 'verified', 'active', 'created_at')
    list_filter = ('verified', 'active')
    search_fields = ('organization_name', 'registration_number', 'email')
    filter_horizontal = ('specialization', 'available_resources')


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'current_occupancy', 'available_capacity', 'status', 'managed_by')
    list_filter = ('status',)
    search_fields = ('name', 'address')
    readonly_fields = ('available_capacity',)


@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'severity', 'disaster_type', 'affected_area', 'active', 'issued_by', 'created_at')
    list_filter = ('severity', 'active', 'disaster_type')
    search_fields = ('title', 'message', 'affected_area')
    date_hierarchy = 'created_at'


@admin.register(CrisisRequest)
class CrisisRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'disaster_type', 'urgency', 'status', 'priority_score', 'people_affected', 'is_verified', 'created_at')
    list_filter = ('urgency', 'status', 'is_verified', 'disaster_type')
    search_fields = ('reporter__username', 'name', 'phone', 'address', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(VolunteerProfile)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('user', 'primary_skill', 'phone', 'available', 'rating', 'tasks_completed', 'total_hours_volunteered')
    list_filter = ('available', 'primary_skill', 'has_vehicle')
    search_fields = ('user__username', 'skills', 'languages_spoken')


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'donor', 'donation_type', 'amount', 'request', 'created_at')
    list_filter = ('donation_type',)
    search_fields = ('donor__username', 'note')
    date_hierarchy = 'created_at'

@admin.register(DonationMedia)
class DonationMediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'uploaded_by', 'media_type', 'donation', 'created_at']
    list_filter = ['media_type', 'created_at']
    search_fields = ['uploaded_by__username', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'volunteer', 'status', 'assigned_at', 'completed', 'hours_spent')
    list_filter = ('status', 'completed')
    search_fields = ('volunteer__user__username',)
    date_hierarchy = 'assigned_at'


@admin.register(ResourceInventory)
class ResourceInventoryAdmin(admin.ModelAdmin):
    list_display = ('ngo', 'resource_type', 'quantity', 'unit', 'location', 'expiry_date', 'last_updated')
    list_filter = ('ngo', 'resource_type__category')
    search_fields = ('location', 'ngo__organization_name', 'resource_type__name')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'message', 'recipient__username')
    date_hierarchy = 'created_at'


@admin.register(CrisisChatMessage)
class CrisisChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'crisis_request', 'sender', 'created_at')
    search_fields = ('crisis_request__id', 'sender__username', 'message')
    date_hierarchy = 'created_at'


@admin.register(CommunityChannel)
class CommunityChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'role_scope', 'is_active', 'created_at')
    list_filter = ('role_scope', 'is_active')
    search_fields = ('name', 'slug', 'description')


@admin.register(CommunityMessage)
class CommunityMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'sender', 'is_urgent', 'created_at')
    list_filter = ('channel', 'is_urgent')
    search_fields = ('sender__username', 'message', 'channel__name')
    date_hierarchy = 'created_at'


@admin.register(AIChatMessage)
class AIChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'context_tag', 'created_at')
    list_filter = ('context_tag',)
    search_fields = ('user__username', 'prompt', 'response')
    date_hierarchy = 'created_at'


@admin.register(UserLocationPing)
class UserLocationPingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'latitude', 'longitude', 'accuracy_meters', 'source', 'created_at')
    list_filter = ('source',)
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'


@admin.register(EmergencyBeacon)
class EmergencyBeaconAdmin(admin.ModelAdmin):
    list_display = ('id', 'triggered_by', 'status', 'acknowledged_by', 'created_at', 'acknowledged_at')
    list_filter = ('status',)
    search_fields = ('triggered_by__username', 'message')
    date_hierarchy = 'created_at'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_type', 'submitted_by', 'rating', 'volunteer', 'ngo', 'created_at')
    list_filter = ('feedback_type', 'rating')
    search_fields = ('submitted_by__username', 'comment')
    date_hierarchy = 'created_at'


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'phone_number', 'active', 'available_247')
    list_filter = ('active', 'category', 'available_247')
    search_fields = ('name', 'category', 'phone_number', 'address')


@admin.register(SafetyTip)
class SafetyTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'disaster_type', 'category', 'language', 'priority', 'is_active', 'created_at')
    list_filter = ('disaster_type', 'category', 'language', 'is_active')
    search_fields = ('title', 'content')
