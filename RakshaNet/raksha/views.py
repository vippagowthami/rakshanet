from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect
from django.db.models import Q, F, Count, Avg
from django.utils import timezone
from .permissions import IsOwnerOrReadOnly, IsNGO
from .models import (
    CrisisRequest, VolunteerProfile, Donation, Assignment,
    DisasterType, ResourceType, NGOProfile, Shelter, EmergencyAlert,
    ResourceInventory, Notification, Feedback, SafetyTip, EmergencyContact
)
from .serializers import (
    CrisisRequestSerializer, VolunteerProfileSerializer,
    DonationSerializer, AssignmentSerializer, DisasterTypeSerializer,
    ResourceTypeSerializer, NGOProfileSerializer, ShelterSerializer,
    EmergencyAlertSerializer, ResourceInventorySerializer,
    NotificationSerializer, FeedbackSerializer, SafetyTipSerializer,
    EmergencyContactSerializer
)
from .utils import sync_request_status_from_assignments


class DisasterTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for disaster types"""
    queryset = DisasterType.objects.all()
    serializer_class = DisasterTypeSerializer
    permission_classes = [permissions.AllowAny]


class ResourceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for resource types"""
    queryset = ResourceType.objects.all()
    serializer_class = ResourceTypeSerializer
    permission_classes = [permissions.AllowAny]


class NGOProfileViewSet(viewsets.ModelViewSet):
    """API endpoint for NGO profiles"""
    queryset = NGOProfile.objects.filter(active=True)
    serializer_class = NGOProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['organization_name', 'service_areas']
    ordering_fields = ['created_at', 'organization_name']


class ShelterViewSet(viewsets.ModelViewSet):
    """API endpoint for emergency shelters"""
    queryset = Shelter.objects.all()
    serializer_class = ShelterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address']
    ordering_fields = ['current_occupancy', 'capacity']
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only available shelters"""
        shelters = self.queryset.filter(status='active', current_occupancy__lt=F('capacity'))
        serializer = self.get_serializer(shelters, many=True)
        return Response(serializer.data)


class EmergencyAlertViewSet(viewsets.ModelViewSet):
    """API endpoint for emergency alerts"""
    queryset = EmergencyAlert.objects.filter(active=True).order_by('-created_at')
    serializer_class = EmergencyAlertSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'affected_area']
    ordering_fields = ['created_at', 'severity']
    
    def get_permissions(self):
        """Only NGOs and admins can create/update alerts"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsNGO()]
        return super().get_permissions()


class CrisisRequestViewSet(viewsets.ModelViewSet):
    queryset = CrisisRequest.objects.all().order_by('-priority_score', '-created_at')
    serializer_class = CrisisRequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'address', 'resources_required']
    ordering_fields = ['created_at', 'priority_score', 'urgency']
    
    def get_queryset(self):
        """Filter based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return queryset.filter(status__in=['verified', 'approved'])
        
        # Users see their own requests
        if hasattr(user, 'profile') and user.profile.is_common_user:
            return queryset.filter(Q(reporter=user) | Q(status__in=['verified', 'approved']))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get current user's crisis requests"""
        requests = self.queryset.filter(reporter=request.user)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsNGO])
    def verify(self, request, pk=None):
        """NGOs can verify requests"""
        crisis_request = self.get_object()
        crisis_request.is_verified = True
        crisis_request.verified_by = request.user
        crisis_request.status = 'verified'
        crisis_request.save()
        return Response({'status': 'verified'})


class VolunteerViewSet(viewsets.ModelViewSet):
    queryset = VolunteerProfile.objects.select_related('user').all()
    serializer_class = VolunteerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'skills', 'languages_spoken']
    ordering_fields = ['created_at', 'rating', 'tasks_completed']

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def set_available(self, request, pk=None):
        obj = self.get_object()
        available = request.data.get('available')
        obj.available = bool(available)
        obj.save(update_fields=['available'])
        return Response({'available': obj.available})
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available volunteers"""
        volunteers = self.queryset.filter(available=True)
        serializer = self.get_serializer(volunteers, many=True)
        return Response(serializer.data)


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all().order_by('-created_at')
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'amount']
    
    def get_queryset(self):
        """Filter donations based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return queryset.none()
        
        # NGO/Admin users see donations for their managed requests
        if hasattr(user, 'profile') and user.profile.is_ngo_or_admin:
            try:
                ngo_profile = user.ngo_profile
                return queryset.filter(request__assigned_ngo=ngo_profile)
            except:
                # If no NGO profile, return all donations (for system admins)
                return queryset
        
        # Regular users see only their own donations
        return queryset.filter(donor=user)


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all().order_by('-assigned_at')
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['assigned_at', 'status']
    
    def get_queryset(self):
        """Filter assignments based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Volunteers see their own assignments
        if hasattr(user, 'volunteer_profile'):
            return queryset.filter(volunteer__user=user)
        
        # NGOs see assignments for their requests
        if hasattr(user, 'ngo_profile'):
            return queryset.filter(request__assigned_ngo__user=user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Volunteer accepts assignment"""
        assignment = self.get_object()
        if assignment.volunteer.user == request.user:
            assignment.status = 'accepted'
            assignment.accepted_at = assignment.accepted_at or timezone.now()
            assignment.save()
            sync_request_status_from_assignments(assignment.request)
            return Response({'status': 'accepted'})
        return Response({'error': 'Not authorized'}, status=403)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark assignment as complete"""
        assignment = self.get_object()
        if assignment.volunteer.user == request.user:
            if not assignment.completed_at:
                volunteer_profile = assignment.volunteer
                volunteer_profile.tasks_completed += 1
                volunteer_profile.save(update_fields=['tasks_completed', 'updated_at'])
            assignment.status = 'completed'
            assignment.completed = True
            assignment.completed_at = assignment.completed_at or timezone.now()
            assignment.save()
            sync_request_status_from_assignments(assignment.request)
            return Response({'status': 'completed'})
        return Response({'error': 'Not authorized'}, status=403)


class ResourceInventoryViewSet(viewsets.ModelViewSet):
    """API endpoint for resource inventory"""
    queryset = ResourceInventory.objects.all()
    serializer_class = ResourceInventorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """NGOs see their own inventory"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if hasattr(user, 'ngo_profile'):
            return queryset.filter(ngo__user=user)
        
        return queryset


class NotificationViewSet(viewsets.ModelViewSet):
    """API endpoint for notifications"""
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Users see only their notifications"""
        return self.queryset.filter(recipient=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        notifications = self.queryset.filter(recipient=request.user, is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'read'})


class FeedbackViewSet(viewsets.ModelViewSet):
    """API endpoint for feedback"""
    queryset = Feedback.objects.all().order_by('-created_at')
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Users should only see feedback they submitted."""
        return self.queryset.filter(submitted_by=self.request.user)


class SafetyTipViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for safety tips"""
    queryset = SafetyTip.objects.filter(is_active=True).order_by('-priority')
    serializer_class = SafetyTipSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']


class EmergencyContactViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for emergency contacts"""
    queryset = EmergencyContact.objects.filter(active=True)
    serializer_class = EmergencyContactSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'category', 'description']


class HomePageView(TemplateView):
    """Home page view showing different dashboards based on user role"""
    template_name = 'raksha/home.html'

    def dispatch(self, request, *args, **kwargs):
        """Require login"""
        if not request.user.is_authenticated:
            from django.contrib.auth.decorators import login_required
            return login_required(super().dispatch)(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # Ensure user has a profile
        if not hasattr(self.request.user, 'profile'):
            from users.models import Profile
            Profile.objects.get_or_create(user=self.request.user)
        
        # Add any common context data
        ctx['active_alerts'] = EmergencyAlert.objects.filter(active=True).count()
        ctx['available_shelters'] = Shelter.objects.filter(status='active').count()
        return ctx


def _build_map_dashboard_payload(user):
    """Build role-aware map datasets for initial render and live refresh API."""
    request_qs = CrisisRequest.objects.select_related('disaster_type', 'assigned_ngo').order_by('-priority_score', '-created_at')

    if hasattr(user, 'profile'):
        profile = user.profile
        if profile.is_ngo_or_admin and hasattr(user, 'ngo_profile'):
            ngo_profile = user.ngo_profile
            request_qs = request_qs.filter(
                Q(assigned_ngo=ngo_profile) |
                Q(assigned_ngo__isnull=True, status__in=['submitted', 'verified', 'pending', 'approved'])
            )
        elif profile.is_volunteer:
            request_qs = request_qs.filter(status__in=['verified', 'approved', 'allocated', 'in_progress'])
        elif profile.is_common_user:
            request_qs = request_qs.filter(
                Q(reporter=user) | Q(status__in=['verified', 'approved', 'allocated', 'in_progress'])
            )

    shelters_qs = Shelter.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
        status='active'
    ).select_related('managed_by').order_by('-updated_at')

    alerts_qs = EmergencyAlert.objects.filter(
        active=True,
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('disaster_type').order_by('-created_at')

    ngos_qs = NGOProfile.objects.filter(
        active=True,
        latitude__isnull=False,
        longitude__isnull=False
    ).order_by('organization_name')

    requests = []
    mappable_request_count = 0
    for req in request_qs[:250]:
        # Keep request status in sync with assignment updates for legacy rows.
        sync_request_status_from_assignments(req)

        lat = float(req.latitude) if req.latitude is not None else None
        lng = float(req.longitude) if req.longitude is not None else None
        if lat is not None and lng is not None:
            mappable_request_count += 1

        requests.append({
            'id': req.id,
            'lat': lat,
            'lng': lng,
            'urgency': req.get_urgency_display(),
            'urgency_code': req.urgency,
            'status': req.get_status_display(),
            'status_code': req.status,
            'priority_score': float(req.priority_score or 0),
            'people_affected': int(req.people_affected or 0),
            'address': req.address or 'N/A',
            'disaster_type': req.disaster_type.name if req.disaster_type else 'N/A',
        })

    shelters = []
    for shelter in shelters_qs[:150]:
        shelters.append({
            'id': shelter.id,
            'name': shelter.name,
            'lat': float(shelter.latitude),
            'lng': float(shelter.longitude),
            'current_occupancy': int(shelter.current_occupancy or 0),
            'capacity': int(shelter.capacity or 0),
            'available_capacity': int(shelter.available_capacity()),
            'address': shelter.address or 'N/A',
        })

    alerts = []
    for alert in alerts_qs[:120]:
        alerts.append({
            'id': alert.id,
            'title': alert.title,
            'lat': float(alert.latitude),
            'lng': float(alert.longitude),
            'severity': alert.get_severity_display(),
            'severity_code': alert.severity,
            'affected_area': alert.affected_area or 'N/A',
        })

    ngos = []
    for ngo in ngos_qs[:120]:
        ngos.append({
            'id': ngo.id,
            'name': ngo.organization_name,
            'lat': float(ngo.latitude),
            'lng': float(ngo.longitude),
            'service_areas': ngo.service_areas or 'N/A',
            'verified': bool(ngo.verified),
            'email': ngo.email or 'N/A',
            'phone': ngo.phone or 'N/A',
        })

    critical_requests = sum(1 for req in requests if req['urgency_code'] == 'critical')
    high_requests = sum(1 for req in requests if req['urgency_code'] == 'high')
    avg_priority = round(sum(req['priority_score'] for req in requests) / max(1, len(requests)), 1) if requests else 0.0
    address_only = sum(1 for req in requests if req['lat'] is None or req['lng'] is None)
    map_ai_insights = []
    if requests:
        map_ai_insights.append(f"AI sees {critical_requests} critical and {high_requests} high urgency request(s) on the map.")
        map_ai_insights.append(f"Average mapped priority score is {avg_priority} across {len(requests)} tracked requests.")
        if address_only:
            map_ai_insights.append(f"{address_only} request(s) are being placed using address estimation and should be geotagged for higher accuracy.")
        if shelters:
            total_beds = sum(shelter['available_capacity'] for shelter in shelters)
            map_ai_insights.append(f"Nearby shelters show {total_beds} currently available capacity across {len(shelters)} shelter point(s).")
    else:
        map_ai_insights.append('AI map insights will appear after crisis requests are created.')

    map_center = [20.5937, 78.9629]
    first_mappable_request = next((item for item in requests if item['lat'] is not None and item['lng'] is not None), None)
    if first_mappable_request:
        map_center = [first_mappable_request['lat'], first_mappable_request['lng']]
    elif alerts:
        map_center = [alerts[0]['lat'], alerts[0]['lng']]
    elif shelters:
        map_center = [shelters[0]['lat'], shelters[0]['lng']]
    elif ngos:
        map_center = [ngos[0]['lat'], ngos[0]['lng']]

    return {
        'requests': requests,
        'shelters': shelters,
        'active_alerts': alerts,
        'ngos': ngos,
        'map_ai_insights': map_ai_insights,
        'map_center_lat': map_center[0],
        'map_center_lng': map_center[1],
        'total_map_points': mappable_request_count + len(shelters) + len(alerts) + len(ngos),
        'mappable_request_count': mappable_request_count,
        'request_count': len(requests),
        'updated_at': timezone.now().isoformat(),
    }

class DashboardView(TemplateView):
    template_name = 'raksha/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        """Require login"""
        if not request.user.is_authenticated:
            from django.contrib.auth.decorators import login_required
            return login_required(super().dispatch)(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        payload = _build_map_dashboard_payload(self.request.user)
        ctx.update(payload)
        ctx['map_payload'] = payload
        return ctx


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_map_data(request):
    """Live map payload for interactive dashboard auto-refresh."""
    return Response(_build_map_dashboard_payload(request.user), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_dashboard(request):
    """
    API endpoint for dashboard statistics based on user role.
    URL: /raksha/api/dashboard/
    Supports both Token and Session authentication
    """
    user = request.user
    data = {'status': 'success'}
    
    try:
        # Common data for all users
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name() or user.username,
        }
        
        # Ensure user has a profile
        if not hasattr(user, 'profile'):
            # Create profile if it doesn't exist
            from users.models import Profile
            profile = Profile.objects.create(user=user)
        else:
            profile = user.profile
        
        # Ensure NGOProfile exists for all users (for compatibility)
        if not hasattr(user, 'ngo_profile'):
            try:
                NGOProfile.objects.create(
                    user=user,
                    organization_name=f'{user.username}\'s Organization',
                    contact_person=user.get_full_name() or user.username,
                    phone='+1-000-000-0000',
                    email=user.email,
                    address='Address TBD',
                    service_areas='Nationwide'
                )
            except Exception as e:
                pass  # Profile already created or error
        
        # Ensure VolunteerProfile exists for all users (for compatibility)
        if not hasattr(user, 'volunteer_profile'):
            try:
                VolunteerProfile.objects.create(
                    user=user,
                    phone='+1-000-000-0000',
                    primary_skill='general'
                )
            except Exception as e:
                pass  # Profile already created or error
        
        # Set role in response
        data['role'] = {
            'id': profile.role,
            'is_ngo': profile.is_ngo_or_admin,
            'is_volunteer': profile.is_volunteer,
            'is_common_user': profile.is_common_user,
        }
        
        # Role-based statistics
        if profile.is_ngo_or_admin:  # NGO/Admin
            # Pending requests
            data['pending_requests'] = CrisisRequest.objects.filter(
                status__in=['pending', 'verified', 'submitted']
            ).count()
            
            # Assigned requests
            data['assigned_requests'] = CrisisRequest.objects.filter(
                status='assigned'
            ).count()
            
            # Shelters - try to get user's NGO profile
            try:
                ngo = user.ngo_profile
                data['shelters_count'] = Shelter.objects.filter(
                    managed_by=ngo
                ).count()
                
                # Inventory items
                data['inventory_count'] = ResourceInventory.objects.filter(
                    ngo=ngo
                ).count()
            except:
                data['shelters_count'] = 0
                data['inventory_count'] = 0
            
            # Active alerts
            data['active_alerts'] = EmergencyAlert.objects.filter(
                active=True
            ).count()
            
            # Available volunteers
            data['available_volunteers'] = VolunteerProfile.objects.filter(
                available=True
            ).count()
            
            # All assignments
            data['total_assignments'] = Assignment.objects.count()
            data['pending_assignments'] = Assignment.objects.filter(
                status='pending'
            ).count()
            
            # Active rescue operations
            data['active_operations'] = CrisisRequest.objects.filter(
                status__in=['assigned', 'in_progress']
            ).count()

            # Donation metrics for home dashboard
            try:
                ngo = user.ngo_profile
                ngo_donations = Donation.objects.filter(request__assigned_ngo=ngo)
            except:
                ngo_donations = Donation.objects.all()

            data['donation_count'] = ngo_donations.count()
            data['donation_total_money'] = float(
                ngo_donations.filter(donation_type='money').aggregate(Sum('amount'))['amount__sum'] or 0
            )
                
        elif profile.is_volunteer:  # Volunteer
            # Get or create volunteer profile
            try:
                volunteer = VolunteerProfile.objects.get(user=user)
            except VolunteerProfile.DoesNotExist:
                volunteer = VolunteerProfile.objects.create(
                    user=user,
                    phone='+1-000-000-0000',
                    primary_skill='general'
                )
            
            # Pending assignments
            data['pending_assignments'] = Assignment.objects.filter(
                volunteer=volunteer,
                status='pending'
            ).count()
            
            # Accepted assignments
            data['accepted_assignments'] = Assignment.objects.filter(
                volunteer=volunteer,
                status='accepted'
            ).count()
            
            # In-progress assignments
            data['in_progress_assignments'] = Assignment.objects.filter(
                volunteer=volunteer,
                status='in_progress'
            ).count()
            
            # Completed assignments
            data['completed_assignments'] = Assignment.objects.filter(
                volunteer=volunteer,
                status='completed'
            ).count()
            
            # Volunteer profile info
            data['available'] = volunteer.available
            data['rating'] = float(getattr(volunteer, 'rating', 0.0))
            data['tasks_completed'] = getattr(volunteer, 'tasks_completed', 0)
            
        elif profile.is_common_user:  # Common User
            # Total requests
            data['total_requests'] = CrisisRequest.objects.filter(
                reporter=user
            ).count()
            
            # Pending requests
            data['pending_requests'] = CrisisRequest.objects.filter(
                reporter=user,
                status='pending'
            ).count()
            
            # In-progress requests
            data['in_progress_requests'] = CrisisRequest.objects.filter(
                reporter=user,
                status__in=['assigned', 'in_progress', 'verified']
            ).count()
            
            # Completed requests
            data['completed_requests'] = CrisisRequest.objects.filter(
                reporter=user,
                status='completed'
            ).count()
            
            # Verified requests
            data['verified_requests'] = CrisisRequest.objects.filter(
                reporter=user,
                status='verified'
            ).count()
            
            # Active alerts nearby (sample - can be enhanced with location)
            data['active_alerts_nearby'] = EmergencyAlert.objects.filter(
                active=True
            ).count()
        else:
            # Unknown role
            data['warning'] = 'Unknown user role'
            data['pending_requests'] = 0
    
    except Exception as e:
        import logging
        logging.error(f"Dashboard API error: {str(e)}", exc_info=True)
        data['error'] = str(e)
        data['status'] = 'error'
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(data, status=status.HTTP_200_OK)


class ProfilePageView(TemplateView):
    """View for user profile page"""
    template_name = 'raksha/profile_complete.html'
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        context = self.get_context_data(**kwargs)
        context['user'] = request.user
        
        # Fetch donations
        try:
            donations = Donation.objects.filter(donor=request.user).order_by('-created_at')[:10]
            context['donations'] = donations
            context['donation_count'] = donations.count()
        except:
            context['donations'] = []
            context['donation_count'] = 0
        
        # Fetch feedback/reviews
        try:
            feedback = Feedback.objects.filter(submitted_by=request.user).order_by('-created_at')[:10]
            context['feedback'] = feedback
            context['feedback_count'] = feedback.count()
            if feedback.exists():
                avg_rating = feedback.aggregate(Avg('rating'))['rating__avg']
                context['avg_rating'] = round(avg_rating, 1) if avg_rating else 0
            else:
                context['avg_rating'] = 0
        except:
            context['feedback'] = []
            context['feedback_count'] = 0
            context['avg_rating'] = 0
        
        # Fetch contact/notification history (support queries)
        try:
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
            context['notifications'] = notifications
            context['notification_count'] = notifications.count()
        except:
            context['notifications'] = []
            context['notification_count'] = 0
        
        # Get additional profile info if available
        if hasattr(request.user, 'volunteer_profile'):
            context['volunteer_profile'] = request.user.volunteer_profile
        
        if hasattr(request.user, 'ngo_profile'):
            context['ngo_profile'] = request.user.ngo_profile
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        """Handle profile updates like account deletion"""
        if not request.user.is_authenticated:
            return redirect('login')
        
        action = request.POST.get('action')
        
        if action == 'delete_account':
            # Verify password
            from django.contrib.auth import authenticate
            user = authenticate(username=request.user.username, password=request.POST.get('password'))
            
            if user is not None:
                # Delete user account
                from django.contrib.auth.models import User
                from django.shortcuts import redirect
                from django.contrib import messages
                
                request.user.delete()
                messages.success(request, 'Account deleted successfully.')
                return redirect('landing')
            else:
                from django.contrib import messages
                messages.error(request, 'Invalid password. Account not deleted.')
                return redirect('profile')
        
        from django.shortcuts import redirect
        return redirect('profile')


class LandingPageView(TemplateView):
    """Public landing page view (no authentication required)"""
    template_name = 'raksha/landing.html'
    
    def get(self, request, *args, **kwargs):
        # If user is already logged in, redirect to dashboard
        if request.user.is_authenticated:
            return redirect('raksha-home')
        
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)
