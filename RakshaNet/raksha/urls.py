from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CrisisRequestViewSet, VolunteerViewSet, AssignmentViewSet,
    HomePageView, DashboardView, DisasterTypeViewSet, ResourceTypeViewSet, NGOProfileViewSet,
    ShelterViewSet, EmergencyAlertViewSet, ResourceInventoryViewSet,
    NotificationViewSet, FeedbackViewSet, SafetyTipViewSet, EmergencyContactViewSet,
    api_dashboard, api_map_data, ProfilePageView, LandingPageView
)
from .role_views import (
    ngo_dashboard, ngo_verify_request, ngo_manage_volunteers, ngo_manage_shelters,
    ngo_resource_inventory, ngo_create_alert, ngo_create_shelter, ngo_edit_shelter,
    ngo_delete_shelter, ngo_add_inventory, ngo_edit_inventory, ngo_delete_inventory,
    ngo_create_assignment, ngo_manage_alerts, ngo_edit_alert, ngo_deactivate_alert,
    ngo_reports, ngo_profile_setup, ngo_manage_requests, ngo_claim_request, ngo_edit_request,
    volunteer_dashboard, volunteer_accept_assignment, volunteer_update_status,
    volunteer_availability_toggle, volunteer_profile_setup, volunteer_assignment_details,
    volunteer_update_assignment, volunteer_history,
    user_dashboard, create_crisis_request, edit_crisis_request, delete_crisis_request,
    public_crisis_request,
    view_crisis_request, post_crisis_chat_message, user_request_history, submit_feedback,
    community_chat, post_community_message, community_messages_api, ai_chat_assistant,
    geolocation_update, geolocation_services,
    trigger_sos_beacon, sos_beacon_feed, acknowledge_sos_beacon,
    view_emergency_alerts, view_shelters, view_safety_tips,
    notifications_list, mark_notification_read,
    # Public views (no login required)
    view_emergency_alerts_public, view_shelters_public, view_safety_tips_public,
    view_emergency_contacts_public,
    # New views for resources and donations
    resources_view, donations_view, create_donation, edit_donation, delete_donation,
    upload_donation_media,
    # Feedback CRUD
    edit_feedback, delete_feedback, feedback_list
)

# API Router
router = DefaultRouter()
router.register(r'disaster-types', DisasterTypeViewSet)
router.register(r'resource-types', ResourceTypeViewSet)
router.register(r'ngos', NGOProfileViewSet)
router.register(r'shelters', ShelterViewSet)
router.register(r'alerts', EmergencyAlertViewSet)
router.register(r'requests', CrisisRequestViewSet)
router.register(r'volunteers', VolunteerViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'inventory', ResourceInventoryViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'feedback', FeedbackViewSet)
router.register(r'safety-tips', SafetyTipViewSet)
router.register(r'emergency-contacts', EmergencyContactViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/dashboard/', api_dashboard, name='api-dashboard'),
    path('api/map-data/', api_map_data, name='api-map-data'),
    
    # Landing page (public - no login required)
    path('', LandingPageView.as_view(), name='landing'),
    path('welcome/', LandingPageView.as_view(), name='main-home'),
    
    # Home page (authenticated only)
    path('home/', HomePageView.as_view(), name='raksha-home'),
    path('home/dashboard/', HomePageView.as_view(), name='blog-home'),
    
    # General dashboard
    path('dashboard/', DashboardView.as_view(), name='raksha-dashboard'),
    
    # User Profile
    path('profile/', ProfilePageView.as_view(), name='profile'),
    # NGO-specific URLs
    path('ngo/dashboard/', ngo_dashboard, name='ngo-dashboard'),
    path('ngo/profile-setup/', ngo_profile_setup, name='ngo-profile-setup'),
    path('ngo/verify/<int:request_id>/', ngo_verify_request, name='ngo-verify-request'),
    path('ngo/volunteers/', ngo_manage_volunteers, name='ngo-volunteers'),
    path('ngo/shelters/', ngo_manage_shelters, name='ngo-shelters'),
    path('ngo/shelters/create/', ngo_create_shelter, name='ngo-create-shelter'),
    path('ngo/shelters/<int:shelter_id>/edit/', ngo_edit_shelter, name='ngo-edit-shelter'),
    path('ngo/shelters/<int:shelter_id>/delete/', ngo_delete_shelter, name='ngo-delete-shelter'),
    path('ngo/inventory/', ngo_resource_inventory, name='ngo-inventory'),
    path('ngo/inventory/add/', ngo_add_inventory, name='ngo-add-inventory'),
    path('ngo/inventory/<int:inventory_id>/edit/', ngo_edit_inventory, name='ngo-edit-inventory'),
    path('ngo/inventory/<int:inventory_id>/delete/', ngo_delete_inventory, name='ngo-delete-inventory'),
    path('ngo/alerts/', ngo_manage_alerts, name='ngo-manage-alerts'),
    path('ngo/alerts/create/', ngo_create_alert, name='ngo-create-alert'),
    path('ngo/alerts/<int:alert_id>/edit/', ngo_edit_alert, name='ngo-edit-alert'),
    path('ngo/alerts/<int:alert_id>/deactivate/', ngo_deactivate_alert, name='ngo-deactivate-alert'),
    path('ngo/assignments/create/', ngo_create_assignment, name='ngo-create-assignment'),
    path('ngo/reports/', ngo_reports, name='ngo-reports'),
    path('ngo/requests/', ngo_manage_requests, name='ngo-manage-requests'),
    path('ngo/requests/<int:request_id>/claim/', ngo_claim_request, name='ngo-claim-request'),
    path('ngo/requests/<int:request_id>/edit/', ngo_edit_request, name='ngo-edit-request'),
    
    # Volunteer-specific URLs
    path('volunteer/dashboard/', volunteer_dashboard, name='volunteer-dashboard'),
    path('volunteer/profile-setup/', volunteer_profile_setup, name='volunteer-profile-setup'),
    path('volunteer/assignment/<int:assignment_id>/', volunteer_assignment_details, name='volunteer-assignment-details'),
    path('volunteer/assignment/<int:assignment_id>/accept/', volunteer_accept_assignment, name='volunteer-accept-assignment'),
    path('volunteer/assignment/<int:assignment_id>/update/', volunteer_update_assignment, name='volunteer-update-assignment'),
    path('volunteer/toggle-availability/', volunteer_availability_toggle, name='volunteer-toggle-availability'),
    path('volunteer/history/', volunteer_history, name='volunteer-history'),
    
    # User/People-specific URLs
    path('user/dashboard/', user_dashboard, name='user-dashboard'),
    path('user/requests/create/', create_crisis_request, name='create-crisis-request'),
    path('emergency/request/', public_crisis_request, name='public-crisis-request'),
    path('user/requests/<int:request_id>/', view_crisis_request, name='view-crisis-request'),
    path('user/requests/<int:request_id>/chat/', post_crisis_chat_message, name='post-crisis-chat-message'),
    path('user/requests/<int:request_id>/edit/', edit_crisis_request, name='edit-crisis-request'),
    path('user/requests/<int:request_id>/delete/', delete_crisis_request, name='delete-crisis-request'),
    path('community/chat/', community_chat, name='community-chat'),
    path('community/chat/post/', post_community_message, name='post-community-message'),
    path('community/chat/messages/', community_messages_api, name='community-messages-api'),
    path('community/chat/ai/', ai_chat_assistant, name='ai-chat-assistant'),
    path('geo/update/', geolocation_update, name='geo-update'),
    path('geo/services/', geolocation_services, name='geo-services'),
    path('sos/trigger/', trigger_sos_beacon, name='sos-trigger'),
    path('sos/feed/', sos_beacon_feed, name='sos-feed'),
    path('sos/<int:beacon_id>/ack/', acknowledge_sos_beacon, name='sos-ack'),
    path('user/feedback/<int:feedback_id>/edit/', edit_feedback, name='edit-feedback'),
    path('user/feedback/<int:feedback_id>/delete/', delete_feedback, name='delete-feedback'),
    path('user/requests/history/', user_request_history, name='user-request-history'),
    path('user/feedback/', submit_feedback, name='submit-feedback'),
    
    # Common URLs
    path('alerts/', view_emergency_alerts, name='emergency-alerts'),
    path('shelters/', view_shelters, name='view-shelters'),
    path('safety-tips/', view_safety_tips, name='safety-tips'),
    path('notifications/', notifications_list, name='notifications'),
    path('notifications/<int:notification_id>/read/', mark_notification_read, name='mark-notification-read'),
    path('resources/', resources_view, name='resources'),
    path('feedback/', feedback_list, name='feedback-list'),
    
    # Donations - specific paths must come before general path
    path('donations/create/', create_donation, name='create-donation'),
    path('donations/<int:donation_id>/edit/', edit_donation, name='edit-donation'),
    path('donations/<int:donation_id>/delete/', delete_donation, name='delete-donation'),
    path('donations/upload-media/', upload_donation_media, name='upload-donation-media'),
    path('donations/', donations_view, name='donations'),
    
    # Public URLs (No login required)
    path('public/alerts/', view_emergency_alerts_public, name='public_emergency_alerts'),
    path('public/shelters/', view_shelters_public, name='public_shelters'),
    path('public/safety-tips/', view_safety_tips_public, name='public_safety_tips'),
    path('public/emergency-contacts/', view_emergency_contacts_public, name='emergency_contacts'),
]
