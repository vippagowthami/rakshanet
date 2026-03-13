"""
Role-based views for NGO, Volunteer, and User dashboards
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from datetime import timedelta, datetime
from django.core.paginator import Paginator

from .models import (
    CrisisRequest, VolunteerProfile, NGOProfile, Donation, Assignment,
    EmergencyAlert, Shelter, ResourceInventory, Notification, Feedback,
    DisasterType, ResourceType, SafetyTip, CrisisChatMessage,
    CommunityChannel, CommunityMessage, AIChatMessage, UserLocationPing,
    EmergencyBeacon
)
from users.models import Profile
from .forms import (
    CrisisRequestForm, VolunteerProfileForm, NGOProfileForm, ShelterForm,
    EmergencyAlertForm, ResourceInventoryForm, DonationForm, AssignmentForm,
    FeedbackForm, SafetyTipForm, CrisisRequestVerifyForm, AssignmentUpdateForm
)
from .utils import (
    infer_urgency_from_text, suggest_resource_types_for_request,
    ai_role_insights_for_requests, haversine_distance,
    generate_ai_coordination_reply, sync_request_status_from_assignments,
    CRISIS_PENDING_STATUSES, CRISIS_ACTIVE_STATUSES, CRISIS_COMPLETED_STATUSES
)


def _ensure_default_community_channels():
    """Create baseline channels once for role-based and all-hands collaboration."""
    defaults = [
        ('all-hands', 'All Hands Coordination', 'Cross-role emergency coordination channel.', 'all'),
        ('ngo-ops', 'NGO Operations', 'For NGO/Admin planning and resource allocation.', 'ngo'),
        ('volunteer-hub', 'Volunteer Hub', 'For volunteer updates, field constraints, and support.', 'volunteer'),
        ('user-support', 'User Support', 'For affected users to ask for guidance and updates.', 'user'),
    ]
    for slug, name, desc, scope in defaults:
        CommunityChannel.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'description': desc,
                'role_scope': scope,
                'is_active': True,
            }
        )


def _user_can_access_channel(user, channel):
    if channel.role_scope == 'all':
        return True
    if channel.role_scope == 'ngo':
        return user.profile.is_ngo_or_admin
    if channel.role_scope == 'volunteer':
        return user.profile.is_volunteer
    if channel.role_scope == 'user':
        return user.profile.is_common_user
    return False


def _resolve_user_location(user):
    """Best-effort location resolver from recent pings and role profiles."""
    latest_ping = UserLocationPing.objects.filter(user=user).first()
    if latest_ping:
        return float(latest_ping.latitude), float(latest_ping.longitude)

    if hasattr(user, 'volunteer_profile') and user.volunteer_profile.latitude and user.volunteer_profile.longitude:
        return float(user.volunteer_profile.latitude), float(user.volunteer_profile.longitude)

    if hasattr(user, 'ngo_profile') and user.ngo_profile.latitude and user.ngo_profile.longitude:
        return float(user.ngo_profile.latitude), float(user.ngo_profile.longitude)

    latest_request = CrisisRequest.objects.filter(reporter=user, latitude__isnull=False, longitude__isnull=False).order_by('-created_at').first()
    if latest_request:
        return float(latest_request.latitude), float(latest_request.longitude)

    return None


def _build_ngo_ai_recommendations(ngo_profile, candidate_requests):
    """Build lightweight AI-style recommendations for NGO dashboard."""
    inventory_qs = ResourceInventory.objects.filter(ngo=ngo_profile).select_related('resource_type')
    inventory_list = list(inventory_qs)
    recs = []

    for req in candidate_requests[:5]:
        req_text = f"{req.description or ''} {req.resources_required or ''}".lower()
        matched = []
        for item in inventory_list:
            rt_name = (item.resource_type.name or '').lower()
            rt_cat = (item.resource_type.category or '').lower()
            if item.quantity <= 0:
                continue
            if rt_name and rt_name in req_text:
                matched.append(item)
            elif rt_cat and rt_cat in req_text:
                matched.append(item)

        recs.append({
            'request': req,
            'matched_inventory': matched[:3],
            'needs_manual_procurement': len(matched) == 0,
        })

    return recs


def _build_volunteer_ai_suggestions(volunteer_profile, nearby_requests):
    """Build ranked nearby requests for volunteer based on distance and priority."""
    suggestions = []
    if volunteer_profile.latitude is None or volunteer_profile.longitude is None:
        return suggestions

    v_lat = float(volunteer_profile.latitude)
    v_lon = float(volunteer_profile.longitude)

    for req in nearby_requests:
        if req.latitude is None or req.longitude is None:
            continue
        try:
            distance_km = haversine_distance(v_lat, v_lon, float(req.latitude), float(req.longitude))
        except Exception:
            continue

        fit_score = (req.priority_score or 0) - min(distance_km * 0.7, 25)
        suggestions.append({
            'request': req,
            'distance_km': round(distance_km, 1),
            'fit_score': round(fit_score, 1),
        })

    suggestions.sort(key=lambda x: x['fit_score'], reverse=True)
    return suggestions[:5]


def _sync_requests_from_assignments(requests_qs):
    """Refresh stored crisis request statuses from assignment state for legacy rows."""
    for crisis_request in requests_qs.prefetch_related('assignments'):
        sync_request_status_from_assignments(crisis_request)


# ============= NGO Dashboard and Views =============

@login_required
def ngo_dashboard(request):
    """Dashboard for NGOs with their specific features"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied. NGO access only.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
    except NGOProfile.DoesNotExist:
        messages.info(request, 'Please complete your NGO profile.')
        return redirect('ngo-profile-setup')
    
    # Statistics - include both assigned and unassigned requests
    assigned_requests = CrisisRequest.objects.filter(assigned_ngo=ngo_profile)
    _sync_requests_from_assignments(assigned_requests)
    unassigned_requests = CrisisRequest.objects.filter(
        assigned_ngo__isnull=True, 
        status__in=['submitted', 'verified', 'pending']
    )
    
    # Combine for total available requests
    all_available_requests = assigned_requests | unassigned_requests
    
    pending_requests = all_available_requests.filter(status__in=['submitted', 'verified', 'pending'])
    in_progress = assigned_requests.filter(status='in_progress')
    completed = assigned_requests.filter(status='completed')
    
    # Recent activities - show both assigned and new unassigned requests
    recent_requests = all_available_requests.order_by('-created_at')[:10]
    unassigned_count = unassigned_requests.count()
    volunteers_count = ngo_profile.volunteers.filter(available=True).count()
    
    # Resource inventory
    inventory = ResourceInventory.objects.filter(ngo=ngo_profile).select_related('resource_type')
    
    # Donations received
    total_donations = Donation.objects.filter(
        request__assigned_ngo=ngo_profile,
        donation_type='money'
    ).aggregate(total=Sum('amount'))['total'] or 0

    ai_recommendations = _build_ngo_ai_recommendations(ngo_profile, list(recent_requests))
    ai_insights = ai_role_insights_for_requests(list(recent_requests))
    
    context = {
        'ngo_profile': ngo_profile,
        'total_requests': all_available_requests.count(),
        'pending_count': pending_requests.count(),
        'in_progress_count': in_progress.count(),
        'completed_count': completed.count(),
        'recent_requests': recent_requests,
        'volunteers_count': volunteers_count,
        'inventory': inventory,
        'total_donations': total_donations,
        'active_alerts': EmergencyAlert.objects.filter(active=True).order_by('-created_at')[:5],
        'unassigned_count': unassigned_count,
        'assigned_count': assigned_requests.count(),
        'ai_insights': ai_insights,
        'ai_recommendations': ai_recommendations,
    }
    
    return render(request, 'raksha/ngo_dashboard.html', context)


@login_required
def ngo_verify_request(request, request_id):
    """NGO can verify crisis requests"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    crisis_request = get_object_or_404(CrisisRequest, id=request_id)
    
    if request.method == 'POST':
        form = CrisisRequestVerifyForm(request.POST)
        
        if form.is_valid():
            action = form.cleaned_data['action']
            notes = form.cleaned_data['notes']
            assigned_ngo = form.cleaned_data['assigned_ngo']
            
            if action == 'verify':
                crisis_request.is_verified = True
                crisis_request.verified_by = request.user
                crisis_request.status = 'verified'
                if assigned_ngo:
                    crisis_request.assigned_ngo = assigned_ngo
                if notes:
                    crisis_request.notes = notes
                crisis_request.save()
                messages.success(request, 'Request verified successfully.')
            elif action == 'reject':
                crisis_request.status = 'cancelled'
                crisis_request.notes = notes or 'Rejected by NGO'
                crisis_request.save()
                messages.info(request, 'Request rejected.')
            
            return redirect('ngo-dashboard')
    else:
        form = CrisisRequestVerifyForm()
    
    return render(request, 'raksha/verify_request.html', {'request': crisis_request, 'form': form})


@login_required
def ngo_manage_volunteers(request):
    """NGOs can manage their volunteers"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
    except NGOProfile.DoesNotExist:
        messages.error(request, 'NGO profile not found.')
        return redirect('ngo-profile-setup')
    
    volunteers = VolunteerProfile.objects.filter(
        affiliated_ngo=ngo_profile
    ).select_related('user').order_by('-created_at')
    
    # Statistics
    available_volunteers = volunteers.filter(available=True)
    total_hours = volunteers.aggregate(Sum('total_hours_volunteered'))['total_hours_volunteered__sum'] or 0
    
    context = {
        'volunteers': volunteers,
        'available_count': available_volunteers.count(),
        'total_volunteers': volunteers.count(),
        'total_hours': total_hours,
    }
    
    return render(request, 'raksha/ngo_volunteers.html', context)


@login_required
def ngo_manage_shelters(request):
    """NGOs can manage emergency shelters"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
        shelters = Shelter.objects.filter(managed_by=ngo_profile).order_by('-created_at')
    except NGOProfile.DoesNotExist:
        shelters = []
    
    context = {
        'shelters': shelters,
    }
    
    return render(request, 'raksha/ngo_shelters.html', context)


@login_required
def ngo_resource_inventory(request):
    """Manage resource inventory for NGO"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
        inventory = ResourceInventory.objects.filter(
            ngo=ngo_profile
        ).select_related('resource_type').order_by('resource_type__category', 'resource_type__name')
    except NGOProfile.DoesNotExist:
        inventory = []
    
    context = {
        'inventory': inventory,
        'resource_types': ResourceType.objects.all().order_by('category', 'name'),
    }
    
    return render(request, 'raksha/ngo_inventory.html', context)


@login_required
def ngo_create_alert(request):
    """NGOs can create emergency alerts"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    if request.method == 'POST':
        form = EmergencyAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.issued_by = request.user
            alert.active = True
            alert.save()
            
            # TODO: Send notifications to affected users
            messages.success(request, 'Emergency alert created successfully.')
            return redirect('ngo-dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        form = EmergencyAlertForm()
    
    context = {
        'form': form,
        'disaster_types': DisasterType.objects.all(),
    }
    
    return render(request, 'raksha/ngo_create_alert.html', context)


# ============= Volunteer Dashboard and Views =============

@login_required
def volunteer_dashboard(request):
    """Dashboard for volunteers"""
    # Ensure profile exists
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=2)
    
    if not profile.is_volunteer:
        messages.error(request, '⚠️ Access denied. Volunteer access only.')
        return redirect('blog-home')
    
    try:
        volunteer_profile = request.user.volunteer_profile
    except VolunteerProfile.DoesNotExist:
        messages.info(request, '⚠️ Please complete your volunteer profile to access the dashboard.')
        return redirect('volunteer-profile-setup')
    
    # Assignments
    my_assignments = Assignment.objects.filter(
        volunteer=volunteer_profile
    ).select_related('request').order_by('-assigned_at')
    
    pending_assignments = my_assignments.filter(status='pending')
    active_assignments = my_assignments.filter(status__in=['accepted', 'in_progress'])
    completed_assignments = my_assignments.filter(status='completed')
    
    # Nearby crisis requests (if location is set)
    nearby_requests = []
    if volunteer_profile.latitude and volunteer_profile.longitude:
        # Simple proximity check (can be improved with geospatial queries)
        nearby_requests = CrisisRequest.objects.filter(
            status__in=['verified', 'approved'],
            latitude__isnull=False,
            longitude__isnull=False
        ).order_by('-priority_score')[:10]

    ai_suggested_requests = _build_volunteer_ai_suggestions(volunteer_profile, list(nearby_requests))
    ai_insights = ai_role_insights_for_requests([item['request'] for item in ai_suggested_requests])
    
    context = {
        'volunteer_profile': volunteer_profile,
        'pending_assignments': pending_assignments,
        'active_assignments': active_assignments,
        'completed_count': completed_assignments.count(),
        'total_hours': volunteer_profile.total_hours_volunteered,
        'rating': volunteer_profile.rating,
        'nearby_requests': nearby_requests,
        'active_alerts': EmergencyAlert.objects.filter(active=True).order_by('-created_at')[:5],
        'ai_suggested_requests': ai_suggested_requests,
        'ai_insights': ai_insights,
    }
    
    return render(request, 'raksha/volunteer_dashboard.html', context)


@login_required
@require_POST
def volunteer_accept_assignment(request, assignment_id):
    """Volunteer accepts an assignment"""
    # Ensure profile exists
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=2)
    
    if not profile.is_volunteer:
        messages.error(request, '⚠️ Access denied. Volunteer access only.')
        return JsonResponse({'error': 'Unauthorized', 'redirect': '/raksha/volunteer/profile-setup/'}, status=403)
    
    try:
        # Check if volunteer profile exists
        try:
            volunteer_profile = request.user.volunteer_profile
        except VolunteerProfile.DoesNotExist:
            messages.error(request, '⚠️ Please set up your volunteer profile first.')
            return JsonResponse({
                'error': 'Profile not found',
                'message': 'Please complete your volunteer profile first.',
                'redirect': '/raksha/volunteer/profile-setup/'
            }, status=404)
        
        assignment = get_object_or_404(Assignment, id=assignment_id, volunteer=volunteer_profile)
        
        if assignment.status == 'pending':
            assignment.status = 'accepted'
            assignment.accepted_at = timezone.now()
            assignment.save()
            sync_request_status_from_assignments(assignment.request)
            
            messages.success(request, f'✅ Assignment #{assignment.id} accepted successfully!')
            return JsonResponse({
                'success': True,
                'message': 'Assignment accepted successfully!',
                'assignment_id': assignment.id,
                'status': 'accepted'
            })
        else:
            messages.warning(request, f'⚠️ Assignment is already {assignment.status}.')
            return JsonResponse({
                'error': 'Assignment already processed',
                'status': assignment.status
            }, status=400)
    
    except Assignment.DoesNotExist:
        messages.error(request, '⚠️ Assignment not found.')
        return JsonResponse({'error': 'Assignment not found'}, status=404)
    except Exception as e:
        messages.error(request, f'⚠️ Error accepting assignment: {str(e)}')
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


@login_required
@require_POST
def volunteer_update_status(request, assignment_id):
    """Update assignment status"""
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=2)
    
    if not profile.is_volunteer:
        return JsonResponse({'error': '⚠️ Unauthorized'}, status=403)
    
    try:
        volunteer_profile = request.user.volunteer_profile
        assignment = get_object_or_404(Assignment, id=assignment_id, volunteer=volunteer_profile)
        
        new_status = request.POST.get('status')
        if new_status in ['in_progress', 'completed']:
            assignment.status = new_status
            
            if new_status == 'in_progress' and not assignment.started_at:
                assignment.started_at = timezone.now()
            elif new_status == 'completed' and not assignment.completed_at:
                assignment.completed_at = timezone.now()
                assignment.completed = True
                
                # Update volunteer stats
                volunteer_profile.tasks_completed += 1
                volunteer_profile.save()
            
            assignment.save()
            sync_request_status_from_assignments(assignment.request)
            messages.success(request, f'✅ Status updated to {new_status.replace("_", " ").title()}!')
            return JsonResponse({
                'success': True,
                'status': new_status,
                'message': f'Status updated to {new_status}'
            })
        else:
            return JsonResponse({'error': 'Invalid status'}, status=400)
    
    except VolunteerProfile.DoesNotExist:
        return JsonResponse({
            'error': '⚠️ Volunteer profile not found. Please set up your profile.',
            'redirect': '/volunteer/profile-setup/'
        }, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


@login_required
def volunteer_availability_toggle(request):
    """Toggle volunteer availability"""
    # Ensure profile exists
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=2)
    
    if not profile.is_volunteer:
        messages.error(request, '⚠️ Unauthorized access.')
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        volunteer_profile = request.user.volunteer_profile
        volunteer_profile.available = not volunteer_profile.available
        volunteer_profile.save()
        
        status_text = 'available' if volunteer_profile.available else 'unavailable'
        messages.success(request, f'✅ You are now {status_text}.')
        
        return JsonResponse({
            'success': True,
            'available': volunteer_profile.available,
            'message': f'You are now {status_text}'
        })
    except VolunteerProfile.DoesNotExist:
        messages.error(request, '⚠️ Please set up your volunteer profile first.')
        return JsonResponse({
            'error': 'Volunteer profile not found',
            'redirect': '/raksha/volunteer/profile-setup/'
        }, status=404)
    except Exception as e:
        messages.error(request, f'⚠️ Error: {str(e)}')
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


# ============= User/People Dashboard and Views =============

@login_required
def user_dashboard(request):
    """Dashboard for regular users seeking help"""
    profile = request.user.profile
    
    if not profile.is_common_user:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    # User's crisis requests
    my_requests = CrisisRequest.objects.filter(
        reporter=request.user
    ).order_by('-created_at')

    ai_priority_preview = []
    for req in my_requests[:5]:
        suggested_urgency = infer_urgency_from_text(req.description, req.resources_required, req.people_affected)
        suggested_resources = suggest_resource_types_for_request(req, ResourceType.objects.all())
        ai_priority_preview.append({
            'request': req,
            'suggested_urgency': suggested_urgency,
            'urgency_alignment': req.urgency == suggested_urgency,
            'suggested_resources': suggested_resources[:3],
        })

    ai_insights = ai_role_insights_for_requests(list(my_requests[:10]))
    
    # Active alerts nearby
    active_alerts = EmergencyAlert.objects.filter(active=True).order_by('-created_at')[:10]
    
    # Available shelters
    available_shelters = Shelter.objects.filter(status='active').order_by('-current_occupancy')[:10]
    
    # Safety tips
    safety_tips = SafetyTip.objects.filter(
        is_active=True,
        language__in=[request.LANGUAGE_CODE, 'en']
    ).order_by('-priority')[:5]
    
    context = {
        'my_requests': my_requests,
        'requests': my_requests,  # For template compatibility
        'active_alerts': active_alerts,
        'available_shelters': available_shelters,
        'nearby_shelters': available_shelters,
        'safety_tips': safety_tips,
        'total_requests': my_requests.count(),
        'pending_requests': my_requests.filter(status='submitted').count(),
        'inprogress_requests': my_requests.filter(status__in=['verified', 'approved', 'in_progress']).count(),
        'completed_requests': my_requests.filter(status='completed').count(),
        'pending_count': my_requests.filter(status='submitted').count(),
        'in_progress_count': my_requests.filter(status__in=['verified', 'approved', 'in_progress']).count(),
        'completed_count': my_requests.filter(status='completed').count(),
        'ai_priority_preview': ai_priority_preview,
        'ai_insights': ai_insights,
    }
    
    return render(request, 'raksha/user_dashboard.html', context)


@login_required
def create_crisis_request(request):
    """Users can create crisis requests"""
    # Ensure user has a profile
    try:
        profile = request.user.profile
    except:
        # Create profile if doesn't exist
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=3)
    
    if request.method == 'POST':
        form = CrisisRequestForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                crisis_request = form.save(commit=False)
                crisis_request.reporter = request.user
                
                # Auto-fill name if not provided
                if not crisis_request.name:
                    crisis_request.name = request.user.get_full_name() or request.user.username
                
                # Set initial status
                crisis_request.status = 'submitted'
                crisis_request.is_verified = False
                
                # Save the request
                crisis_request.save()
                
                messages.success(
                    request, 
                    f'✅ Crisis request #{crisis_request.id} submitted successfully! '
                    f'Our team will review and respond shortly.'
                )
                return redirect('user-dashboard')
                
            except Exception as e:
                messages.error(request, f'⚠️ Error saving request: {str(e)}. Please try again.')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        # Pre-fill form with user data
        initial_data = {
            'name': request.user.get_full_name() or request.user.username,
        }
        form = CrisisRequestForm(initial=initial_data)
    
    context = {
        'form': form,
        'disaster_types': DisasterType.objects.all().order_by('name'),
    }
    
    return render(request, 'raksha/create_request.html', context)


@login_required
def view_emergency_alerts(request):
    """View all active emergency alerts"""
    alerts = EmergencyAlert.objects.filter(active=True).select_related('disaster_type').order_by('-created_at')
    
    context = {
        'alerts': alerts,
    }
    
    return render(request, 'raksha/emergency_alerts.html', context)


@login_required
def view_shelters(request):
    """View available emergency shelters"""
    shelters = Shelter.objects.filter(status__in=['active', 'full', 'inactive'])
    status_filter = request.GET.get('status')
    if status_filter in ['active', 'full', 'inactive']:
        shelters = shelters.filter(status=status_filter)
    shelters = shelters.order_by('name')
    
    context = {
        'shelters': shelters,
    }
    
    return render(request, 'raksha/shelters.html', context)


@login_required
def view_safety_tips(request):
    """View safety tips for different disasters"""
    disaster_type = request.GET.get('type')
    
    if disaster_type:
        tips = SafetyTip.objects.filter(
            disaster_type_id=disaster_type,
            is_active=True
        ).order_by('-priority')
    else:
        tips = SafetyTip.objects.filter(is_active=True).select_related('disaster_type').order_by('-priority')
    
    context = {
        'tips': tips,
        'disaster_types': DisasterType.objects.all(),
    }
    
    return render(request, 'raksha/safety_tips.html', context)


# ============= Common Views =============

@login_required
def notifications_list(request):
    """List all notifications for user"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:50]
    
    # Mark as read when viewed
    notifications.filter(is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'raksha/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True})


# ============= CRUD Operations for Crisis Requests =============

@login_required
def edit_crisis_request(request, request_id):
    """Edit crisis request (owner or NGO can edit)"""
    crisis_request = get_object_or_404(CrisisRequest, id=request_id)
    
    # Check permissions
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=3)
    
    if crisis_request.reporter != request.user and not profile.is_ngo_or_admin:
        messages.error(request, '⚠️ You do not have permission to edit this request.')
        return redirect('user-dashboard')
    
    if request.method == 'POST':
        form = CrisisRequestForm(request.POST, request.FILES, instance=crisis_request)
        if form.is_valid():
            try:
                updated_request = form.save()
                messages.success(request, f'✅ Crisis request #{updated_request.id} updated successfully!')
                if profile.is_ngo_or_admin:
                    return redirect('ngo-dashboard')
                return redirect('user-dashboard')
            except Exception as e:
                messages.error(request, f'⚠️ Error updating request: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        form = CrisisRequestForm(instance=crisis_request)
    
    context = {
        'form': form,
        'crisis_request': crisis_request,
        'is_edit': True
    }
    
    return render(request, 'raksha/create_request.html', context)


@login_required
def delete_crisis_request(request, request_id):
    """Delete crisis request (owner or NGO can delete)"""
    crisis_request = get_object_or_404(CrisisRequest, id=request_id)
    
    # Check permissions
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=3)
    
    if crisis_request.reporter != request.user and not profile.is_ngo_or_admin:
        messages.error(request, '⚠️ You do not have permission to delete this request.')
        return redirect('user-dashboard')
    
    if request.method == 'POST':
        try:
            request_id_display = crisis_request.id
            crisis_request.delete()
            messages.success(request, f'✅ Crisis request #{request_id_display} deleted successfully.')
            if profile.is_ngo_or_admin:
                return redirect('ngo-dashboard')
            return redirect('user-dashboard')
        except Exception as e:
            messages.error(request, f'⚠️ Error deleting request: {str(e)}')
            return redirect('user-dashboard')
    
    context = {
        'crisis_request': crisis_request
    }
    
    return render(request, 'raksha/confirm_delete_request.html', context)


@login_required
def view_crisis_request(request, request_id):
    """View detailed crisis request"""
    crisis_request = get_object_or_404(CrisisRequest, id=request_id)
    assignments = crisis_request.assignments.all().select_related('volunteer__user')
    donations = crisis_request.donations.all().select_related('donor')

    if request.user.profile.is_volunteer:
        permitted = crisis_request.assignments.filter(volunteer__user=request.user).exists() or crisis_request.reporter == request.user
    else:
        permitted = request.user == crisis_request.reporter or request.user.profile.is_ngo_or_admin

    if not permitted:
        messages.error(request, 'You do not have permission to view this request.')
        return redirect('blog-home')

    chat_messages = crisis_request.chat_messages.select_related('sender').all()[:100]

    suggested_resources = suggest_resource_types_for_request(
        crisis_request,
        ResourceType.objects.all().order_by('category', 'name')
    )
    
    context = {
        'crisis_request': crisis_request,
        'assignments': assignments,
        'donations': donations,
        'chat_messages': chat_messages,
        'suggested_resources': suggested_resources,
        'can_edit': request.user == crisis_request.reporter or request.user.profile.is_ngo_or_admin
    }
    
    return render(request, 'raksha/view_request.html', context)


@login_required
@require_POST
def post_crisis_chat_message(request, request_id):
    """Post a chat message on a crisis request for allowed participants."""
    crisis_request = get_object_or_404(CrisisRequest, id=request_id)
    profile = request.user.profile

    is_reporter = crisis_request.reporter == request.user
    is_ngo = profile.is_ngo_or_admin
    is_assigned_volunteer = crisis_request.assignments.filter(volunteer__user=request.user).exists()

    if not (is_reporter or is_ngo or is_assigned_volunteer):
        messages.error(request, 'You are not allowed to post chat messages for this request.')
        return redirect('blog-home')

    message_text = (request.POST.get('message') or '').strip()
    if not message_text:
        messages.error(request, 'Message cannot be empty.')
        return redirect('view-crisis-request', request_id=request_id)

    CrisisChatMessage.objects.create(
        crisis_request=crisis_request,
        sender=request.user,
        message=message_text
    )

    messages.success(request, 'Message posted to crisis coordination chat.')
    return redirect('view-crisis-request', request_id=request_id)


@login_required
def community_chat(request):
    """Role-aware community channels with live feed polling support."""
    _ensure_default_community_channels()

    channels = CommunityChannel.objects.filter(is_active=True).order_by('name')
    accessible_channels = [ch for ch in channels if _user_can_access_channel(request.user, ch)]

    if not accessible_channels:
        messages.error(request, 'No community channels are available for your role yet.')
        return redirect('raksha-home')

    selected_slug = request.GET.get('channel')
    selected_channel = next((c for c in accessible_channels if c.slug == selected_slug), accessible_channels[0])

    recent_messages = selected_channel.messages.select_related('sender').order_by('-created_at')[:120]
    recent_messages = list(recent_messages)
    recent_messages.reverse()

    ai_history = AIChatMessage.objects.filter(user=request.user).order_by('-created_at')[:20]
    ai_history = list(ai_history)
    ai_history.reverse()

    context = {
        'channels': accessible_channels,
        'selected_channel': selected_channel,
        'community_messages': recent_messages,
        'ai_history': ai_history,
    }
    return render(request, 'raksha/community_chat.html', context)


@login_required
@require_POST
def post_community_message(request):
    """Post a message to selected community channel if role is permitted."""
    channel = get_object_or_404(CommunityChannel, slug=request.POST.get('channel_slug', ''))

    if not _user_can_access_channel(request.user, channel):
        messages.error(request, 'You do not have access to this community channel.')
        return redirect('community-chat')

    text = (request.POST.get('message') or '').strip()
    if not text:
        messages.error(request, 'Message cannot be empty.')
        return redirect(f"/raksha/community/chat/?channel={channel.slug}")

    urgent_tokens = ['urgent', 'sos', 'critical', 'immediate help']
    is_urgent = any(token in text.lower() for token in urgent_tokens)

    CommunityMessage.objects.create(
        channel=channel,
        sender=request.user,
        message=text,
        is_urgent=is_urgent,
    )

    if is_urgent and channel.role_scope == 'all':
        responder_profiles = Profile.objects.filter(role__in=[1, 2]).select_related('user')[:50]
        Notification.objects.bulk_create([
            Notification(
                recipient=profile.user,
                notification_type='alert',
                title='Urgent Community Chat Update',
                message=f'Urgent message in {channel.name} by {request.user.username}.',
                link='/raksha/community/chat/?channel=all-hands',
            )
            for profile in responder_profiles
            if profile.user_id != request.user.id
        ])

    return redirect(f"/raksha/community/chat/?channel={channel.slug}")


@login_required
def community_messages_api(request):
    """Return community messages for lightweight live refresh in UI."""
    channel = get_object_or_404(CommunityChannel, slug=request.GET.get('channel', ''))

    if not _user_can_access_channel(request.user, channel):
        return JsonResponse({'error': 'forbidden'}, status=403)

    try:
        since_id = int(request.GET.get('since_id', 0))
    except (TypeError, ValueError):
        since_id = 0

    queryset = channel.messages.select_related('sender').order_by('id')
    if since_id > 0:
        queryset = queryset.filter(id__gt=since_id)
    else:
        queryset = queryset.order_by('-id')[:60]
        queryset = reversed(list(queryset))

    payload = [
        {
            'id': msg.id,
            'sender': msg.sender.username,
            'message': msg.message,
            'is_urgent': msg.is_urgent,
            'created_at': timezone.localtime(msg.created_at).strftime('%b %d, %Y %H:%M'),
        }
        for msg in queryset
    ]

    return JsonResponse({'messages': payload})


@login_required
@require_POST
def ai_chat_assistant(request):
    """Generate and store AI-style assistant guidance for any role."""
    prompt = (request.POST.get('prompt') or '').strip()
    if not prompt:
        messages.error(request, 'Please enter a question for AI assistant.')
        return redirect('community-chat')

    if request.user.profile.is_ngo_or_admin:
        role = 'ngo'
    elif request.user.profile.is_volunteer:
        role = 'volunteer'
    else:
        role = 'user'

    response_text = generate_ai_coordination_reply(prompt, role=role)

    AIChatMessage.objects.create(
        user=request.user,
        prompt=prompt,
        response=response_text,
        context_tag=role,
    )
    return redirect('community-chat')


@login_required
@require_POST
def geolocation_update(request):
    """Receive browser geolocation updates and persist the latest user location."""
    try:
        latitude = float(request.POST.get('latitude', ''))
        longitude = float(request.POST.get('longitude', ''))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid latitude or longitude.'}, status=400)

    accuracy = request.POST.get('accuracy')
    try:
        accuracy_value = float(accuracy) if accuracy else None
    except (TypeError, ValueError):
        accuracy_value = None

    UserLocationPing.objects.create(
        user=request.user,
        latitude=latitude,
        longitude=longitude,
        accuracy_meters=accuracy_value,
        source='browser',
    )

    if request.user.profile.is_volunteer and hasattr(request.user, 'volunteer_profile'):
        vp = request.user.volunteer_profile
        vp.latitude = latitude
        vp.longitude = longitude
        vp.save(update_fields=['latitude', 'longitude'])
    elif request.user.profile.is_ngo_or_admin and hasattr(request.user, 'ngo_profile'):
        np = request.user.ngo_profile
        np.latitude = latitude
        np.longitude = longitude
        np.save(update_fields=['latitude', 'longitude'])

    return JsonResponse({'success': True})


@login_required
def geolocation_services(request):
    """Return prioritized nearby services and resources based on latest user location."""
    location = _resolve_user_location(request.user)
    if not location:
        return JsonResponse({'needs_location': True, 'services': [], 'resources': [], 'requests': []})

    user_lat, user_lon = location

    shelters_payload = []
    shelters = Shelter.objects.filter(status='active', latitude__isnull=False, longitude__isnull=False).order_by('-created_at')[:120]
    for shelter in shelters:
        distance = haversine_distance(user_lat, user_lon, float(shelter.latitude), float(shelter.longitude))
        shelters_payload.append({
            'type': 'shelter',
            'name': shelter.name,
            'distance_km': round(distance, 1),
            'detail': shelter.address,
            'capacity': shelter.available_capacity(),
        })

    ngo_payload = []
    ngos = NGOProfile.objects.filter(active=True, latitude__isnull=False, longitude__isnull=False).order_by('-verified')[:120]
    for ngo in ngos:
        distance = haversine_distance(user_lat, user_lon, float(ngo.latitude), float(ngo.longitude))
        ngo_payload.append({
            'type': 'ngo',
            'name': ngo.organization_name,
            'distance_km': round(distance, 1),
            'detail': ngo.service_areas,
            'capacity': None,
        })

    services = sorted(shelters_payload + ngo_payload, key=lambda x: x['distance_km'])[:6]

    resources = []
    inventory = ResourceInventory.objects.filter(
        quantity__gt=0,
        ngo__active=True,
        ngo__latitude__isnull=False,
        ngo__longitude__isnull=False,
    ).select_related('ngo', 'resource_type')[:240]
    for item in inventory:
        distance = haversine_distance(user_lat, user_lon, float(item.ngo.latitude), float(item.ngo.longitude))
        priority_score = round(float(item.quantity) - (distance * 0.5), 2)
        resources.append({
            'resource': item.resource_type.name,
            'ngo': item.ngo.organization_name,
            'quantity': item.quantity,
            'unit': item.unit,
            'distance_km': round(distance, 1),
            'priority_score': priority_score,
        })

    resources = sorted(resources, key=lambda x: x['priority_score'], reverse=True)[:8]

    requests_payload = []
    requests_qs = CrisisRequest.objects.filter(
        status__in=['verified', 'approved', 'in_progress'],
        latitude__isnull=False,
        longitude__isnull=False,
    ).order_by('-priority_score')[:120]
    for crisis in requests_qs:
        distance = haversine_distance(user_lat, user_lon, float(crisis.latitude), float(crisis.longitude))
        reach_score = round((crisis.priority_score or 0) - (distance * 0.8), 2)
        requests_payload.append({
            'id': crisis.id,
            'urgency': crisis.urgency,
            'distance_km': round(distance, 1),
            'reach_score': reach_score,
            'address': crisis.address,
        })

    requests_payload = sorted(requests_payload, key=lambda x: x['reach_score'], reverse=True)[:6]

    return JsonResponse({
        'needs_location': False,
        'user_location': {'latitude': user_lat, 'longitude': user_lon},
        'services': services,
        'resources': resources,
        'requests': requests_payload,
    })


@login_required
@require_POST
def trigger_sos_beacon(request):
    """Trigger an SOS beacon and notify responders."""
    location = _resolve_user_location(request.user)

    message_text = (request.POST.get('message') or '').strip()[:280]
    if not message_text:
        message_text = 'Emergency SOS triggered. Immediate coordination required.'

    beacon = EmergencyBeacon.objects.create(
        triggered_by=request.user,
        latitude=location[0] if location else None,
        longitude=location[1] if location else None,
        message=message_text,
        status='open',
    )

    responders = Profile.objects.filter(role__in=[1, 2]).select_related('user')
    if request.user.profile.is_ngo_or_admin:
        responders = responders.filter(role=2)

    notifications = []
    for profile in responders[:120]:
        if profile.user_id == request.user.id:
            continue
        notifications.append(Notification(
            recipient=profile.user,
            notification_type='alert',
            title='SOS Beacon Triggered',
            message=f'{request.user.username} triggered SOS: {message_text[:120]}',
            link='/raksha/home/',
        ))

    if notifications:
        Notification.objects.bulk_create(notifications)

    return JsonResponse({'success': True, 'beacon_id': beacon.id})


@login_required
def sos_beacon_feed(request):
    """Live SOS feed for responders and personal beacon history for users."""
    if request.user.profile.is_ngo_or_admin or request.user.profile.is_volunteer:
        queryset = EmergencyBeacon.objects.select_related('triggered_by', 'acknowledged_by').order_by('-created_at')[:30]
    else:
        queryset = EmergencyBeacon.objects.select_related('triggered_by', 'acknowledged_by').filter(triggered_by=request.user).order_by('-created_at')[:30]

    payload = []
    for beacon in queryset:
        if beacon.latitude is not None and beacon.longitude is not None:
            user_loc = _resolve_user_location(request.user)
            if user_loc:
                distance_km = round(haversine_distance(user_loc[0], user_loc[1], float(beacon.latitude), float(beacon.longitude)), 1)
            else:
                distance_km = None
        else:
            distance_km = None

        payload.append({
            'id': beacon.id,
            'triggered_by': beacon.triggered_by.username,
            'status': beacon.status,
            'message': beacon.message,
            'created_at': timezone.localtime(beacon.created_at).strftime('%b %d, %Y %H:%M'),
            'acknowledged_by': beacon.acknowledged_by.username if beacon.acknowledged_by else None,
            'distance_km': distance_km,
        })

    return JsonResponse({'beacons': payload})


@login_required
@require_POST
def acknowledge_sos_beacon(request, beacon_id):
    """Responder acknowledges or resolves a beacon."""
    if not (request.user.profile.is_ngo_or_admin or request.user.profile.is_volunteer):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    beacon = get_object_or_404(EmergencyBeacon, id=beacon_id)
    action = (request.POST.get('action') or 'ack').strip()

    if action == 'resolve':
        beacon.status = 'resolved'
        beacon.resolved_at = timezone.now()
    else:
        if beacon.status == 'open':
            beacon.status = 'acknowledged'
        beacon.acknowledged_by = request.user
        beacon.acknowledged_at = timezone.now()

    beacon.save()

    if beacon.triggered_by_id != request.user.id:
        Notification.objects.create(
            recipient=beacon.triggered_by,
            notification_type='request_update',
            title='SOS Beacon Updated',
            message=f'Your SOS #{beacon.id} is now {beacon.status}.',
            link='/raksha/home/',
        )

    return JsonResponse({'success': True, 'status': beacon.status})


# ============= NGO Advanced Features =============

@login_required
def ngo_create_shelter(request):
    """NGO can create new shelter"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
    except NGOProfile.DoesNotExist:
        messages.error(request, 'NGO profile not found.')
        return redirect('ngo-profile-setup')
    
    if request.method == 'POST':
        form = ShelterForm(request.POST)
        if form.is_valid():
            shelter = form.save(commit=False)
            shelter.managed_by = ngo_profile
            shelter.save()
            form.save_m2m()  # Save many-to-many relations
            messages.success(request, 'Shelter created successfully.')
            return redirect('ngo-shelters')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        form = ShelterForm()
    
    context = {
        'form': form,
        'is_edit': False
    }
    
    return render(request, 'raksha/shelter_form.html', context)


@login_required
def ngo_edit_shelter(request, shelter_id):
    """NGO can edit shelter"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
        shelter = get_object_or_404(Shelter, id=shelter_id, managed_by=ngo_profile)
    except NGOProfile.DoesNotExist:
        messages.error(request, 'NGO profile not found.')
        return redirect('ngo-profile-setup')
    
    if request.method == 'POST':
        form = ShelterForm(request.POST, instance=shelter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shelter updated successfully.')
            return redirect('ngo-shelters')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        form = ShelterForm(instance=shelter)
    
    context = {
        'form': form,
        'shelter': shelter,
        'is_edit': True
    }
    
    return render(request, 'raksha/shelter_form.html', context)


@login_required
def ngo_delete_shelter(request, shelter_id):
    """NGO can delete shelter"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
        shelter = get_object_or_404(Shelter, id=shelter_id, managed_by=ngo_profile)
    except NGOProfile.DoesNotExist:
        messages.error(request, 'NGO profile not found.')
        return redirect('ngo-profile-setup')
    
    if request.method == 'POST':
        shelter.delete()
        messages.success(request, 'Shelter deleted successfully.')
        return redirect('ngo-shelters')
    
    context = {
        'shelter': shelter
    }
    
    return render(request, 'raksha/confirm_delete_shelter.html', context)


@login_required
def ngo_add_inventory(request):
    """NGO can add resource inventory"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
    except NGOProfile.DoesNotExist:
        messages.error(request, 'NGO profile not found.')
        return redirect('ngo-profile-setup')
    
    if request.method == 'POST':
        form = ResourceInventoryForm(request.POST)
        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.ngo = ngo_profile
            inventory.updated_by = request.user
            inventory.save()
            messages.success(request, 'Resource added to inventory.')
            return redirect('ngo-inventory')
    else:
        form = ResourceInventoryForm()
    
    context = {
        'form': form,
        'is_edit': False
    }
    
    return render(request, 'raksha/inventory_form.html', context)


@login_required
def ngo_edit_inventory(request, inventory_id):
    """NGO can edit resource inventory"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
        inventory = get_object_or_404(ResourceInventory, id=inventory_id, ngo=ngo_profile)
    except NGOProfile.DoesNotExist:
        messages.error(request, 'NGO profile not found.')
        return redirect('ngo-profile-setup')
    
    if request.method == 'POST':
        form = ResourceInventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.updated_by = request.user
            inventory.save()
            messages.success(request, 'Inventory updated successfully.')
            return redirect('ngo-inventory')
    else:
        form = ResourceInventoryForm(instance=inventory)
    
    context = {
        'form': form,
        'inventory': inventory,
        'is_edit': True
    }
    
    return render(request, 'raksha/inventory_form.html', context)


@login_required
def ngo_delete_inventory(request, inventory_id):
    """NGO can delete resource inventory"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
        inventory = get_object_or_404(ResourceInventory, id=inventory_id, ngo=ngo_profile)
    except NGOProfile.DoesNotExist:
        messages.error(request, 'NGO profile not found.')
        return redirect('ngo-profile-setup')
    
    if request.method == 'POST':
        inventory.delete()
        messages.success(request, 'Inventory item deleted successfully.')
        return redirect('ngo-inventory')
    
    context = {
        'inventory': inventory
    }
    
    return render(request, 'raksha/confirm_delete_inventory.html', context)


@login_required
def ngo_create_assignment(request):
    """NGO can create volunteer assignments"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            ngo_profile = request.user.ngo_profile
            crisis_request = assignment.request

            if crisis_request.assigned_ngo_id and crisis_request.assigned_ngo_id != ngo_profile.id:
                messages.error(request, 'This crisis request is already assigned to another organization.')
                return redirect('ngo-manage-requests')

            if crisis_request.assigned_ngo_id != ngo_profile.id:
                crisis_request.assigned_ngo = ngo_profile
                crisis_request.save()

            assignment.save()
            sync_request_status_from_assignments(crisis_request)
            messages.success(request, f'Assignment created for volunteer {assignment.volunteer.user.username}.')
            
            # Create notification for volunteer
            Notification.objects.create(
                recipient=assignment.volunteer.user,
                notification_type='assignment',
                title='New Assignment',
                message=f'You have been assigned to crisis request #{assignment.request.id}',
                link=f'/raksha/volunteer/dashboard/'
            )
            
            return redirect('ngo-dashboard')
    else:
        form = AssignmentForm()
        # Filter forms based on context
        crisis_request_id = request.GET.get('request')
        if crisis_request_id:
            form.fields['request'].initial = crisis_request_id
    
    context = {
        'form': form
    }
    
    return render(request, 'raksha/assignment_form.html', context)


@login_required
def ngo_manage_alerts(request):
    """NGO can view and manage all alerts"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    alerts = EmergencyAlert.objects.filter(
        issued_by=request.user
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    alerts_page = paginator.get_page(page_number)
    
    context = {
        'alerts': alerts_page
    }
    
    return render(request, 'raksha/ngo_manage_alerts.html', context)


@login_required
def ngo_edit_alert(request, alert_id):
    """NGO can edit emergency alert"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    alert = get_object_or_404(EmergencyAlert, id=alert_id, issued_by=request.user)
    
    if request.method == 'POST':
        form = EmergencyAlertForm(request.POST, instance=alert)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alert updated successfully.')
            return redirect('ngo-manage-alerts')
    else:
        form = EmergencyAlertForm(instance=alert)
    
    context = {
        'form': form,
        'alert': alert,
        'is_edit': True
    }
    
    return render(request, 'raksha/ngo_create_alert.html', context)


@login_required
def ngo_deactivate_alert(request, alert_id):
    """NGO can deactivate emergency alert"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    alert = get_object_or_404(EmergencyAlert, id=alert_id, issued_by=request.user)
    alert.active = False
    alert.save()
    
    messages.success(request, 'Alert deactivated.')
    return redirect('ngo-manage-alerts')


@login_required
def ngo_reports(request):
    """NGO can view reports and statistics"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
    except NGOProfile.DoesNotExist:
        messages.error(request, 'NGO profile not found.')
        return redirect('ngo-profile-setup')
    
    # Get date range from query params (optional filtering)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base query - all requests assigned to NGO
    requests = CrisisRequest.objects.filter(assigned_ngo=ngo_profile)
    _sync_requests_from_assignments(requests)
    
    # Apply date filter only if explicitly provided
    date_filtered = False
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            requests = requests.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )
            date_filtered = True
        except ValueError:
            messages.warning(request, 'Invalid date format. Showing all records.')
            start_date = None
            end_date = None
    else:
        # Default: show all time data
        start_date = None
        end_date = None
    
    total_requests = requests.count()
    completed = requests.filter(status__in=CRISIS_COMPLETED_STATUSES).count()
    pending = requests.filter(status__in=CRISIS_PENDING_STATUSES).count()
    in_progress = requests.filter(status__in=CRISIS_ACTIVE_STATUSES).count()
    
    # Calculate success rate
    success_rate = round((completed * 100.0 / total_requests), 1) if total_requests > 0 else 0
    
    # Donations query - apply date filter if set
    donations_query = Donation.objects.filter(
        request__assigned_ngo=ngo_profile,
        donation_type='money'
    )
    if date_filtered and start_date and end_date:
        donations_query = donations_query.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
    
    stats = {
        'total_requests': total_requests,
        'completed': completed,
        'pending': pending,
        'in_progress': in_progress,
        'cancelled': requests.filter(status='cancelled').count(),
        'people_helped': requests.aggregate(Sum('people_affected'))['people_affected__sum'] or 0,
        'by_disaster_type': requests.values('disaster_type__name').annotate(count=Count('id')).order_by('-count'),
        'by_urgency': requests.values('urgency').annotate(count=Count('id')).order_by('-count'),
        'volunteers_active': ngo_profile.volunteers.filter(available=True).count(),
        'total_volunteers': ngo_profile.volunteers.count(),
        'total_donations': donations_query.aggregate(Sum('amount'))['amount__sum'] or 0,
        'success_rate': success_rate
    }
    
    context = {
        'stats': stats,
        'start_date': start_date,
        'end_date': end_date,
        'date_filtered': date_filtered,
        'ngo_profile': ngo_profile
    }
    
    return render(request, 'raksha/ngo_reports.html', context)


# ============= Volunteer Advanced Features =============

@login_required
def volunteer_profile_setup(request):
    """Volunteer can setup/edit their profile"""
    # Ensure profile exists
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=2)
    
    if not profile.is_volunteer:
        messages.error(request, '⚠️ Access denied. Volunteer access only.')
        return redirect('blog-home')
    
    try:
        volunteer_profile = request.user.volunteer_profile
    except VolunteerProfile.DoesNotExist:
        volunteer_profile = None
    
    if request.method == 'POST':
        form = VolunteerProfileForm(request.POST, instance=volunteer_profile)
        if form.is_valid():
            try:
                vol_profile = form.save(commit=False)
                if not volunteer_profile:
                    vol_profile.user = request.user
                vol_profile.save()
                
                messages.success(request, f'✅ Volunteer profile {"updated" if volunteer_profile else "created"} successfully!')
                return redirect('volunteer-dashboard')
            except Exception as e:
                messages.error(request, f'⚠️ Error saving profile: {str(e)}')
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        form = VolunteerProfileForm(instance=volunteer_profile)
    
    context = {
        'form': form,
        'volunteer_profile': volunteer_profile,
        'is_new': volunteer_profile is None
    }
    
    return render(request, 'raksha/volunteer_profile_form.html', context)


@login_required
def volunteer_assignment_details(request, assignment_id):
    """View assignment details"""
    # Ensure profile exists
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=2)
    
    if not profile.is_volunteer:
        messages.error(request, '⚠️ Access denied. Volunteer access only.')
        return redirect('blog-home')
    
    try:
        volunteer_profile = request.user.volunteer_profile
        assignment = get_object_or_404(Assignment, id=assignment_id, volunteer=volunteer_profile)
    except VolunteerProfile.DoesNotExist:
        messages.error(request, '⚠️ Volunteer profile not found. Please set up your profile first.')
        return redirect('volunteer-profile-setup')
    
    context = {
        'assignment': assignment
    }
    
    return render(request, 'raksha/volunteer_assignment_details.html', context)


@login_required
def volunteer_update_assignment(request, assignment_id):
    """Volunteer can update assignment progress"""
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=2)
    
    if not profile.is_volunteer:
        messages.error(request, '⚠️ Access denied. Volunteer access only.')
        return redirect('blog-home')
    
    try:
        volunteer_profile = request.user.volunteer_profile
        assignment = get_object_or_404(Assignment, id=assignment_id, volunteer=volunteer_profile)
    except VolunteerProfile.DoesNotExist:
        messages.error(request, '⚠️ Volunteer profile not found. Please set up your profile first.')
        return redirect('volunteer-profile-setup')
    
    if request.method == 'POST':
        form = AssignmentUpdateForm(request.POST, instance=assignment)
        if form.is_valid():
            try:
                assignment = form.save(commit=False)
                
                # Update timestamps
                if assignment.status == 'in_progress' and not assignment.started_at:
                    assignment.started_at = timezone.now()
                elif assignment.status == 'completed' and not assignment.completed_at:
                    assignment.completed_at = timezone.now()
                    assignment.completed = True
                    
                    # Update volunteer stats
                    volunteer_profile.tasks_completed += 1
                    if assignment.hours_spent:
                        volunteer_profile.total_hours_volunteered += assignment.hours_spent
                    volunteer_profile.save()
                
                assignment.save()
                sync_request_status_from_assignments(assignment.request)
                messages.success(request, f'✅ Assignment #{assignment.id} updated successfully!')
                return redirect('volunteer-dashboard')
            except Exception as e:
                messages.error(request, f'⚠️ Error updating assignment: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        form = AssignmentUpdateForm(instance=assignment)
    
    context = {
        'form': form,
        'assignment': assignment
    }
    
    return render(request, 'raksha/volunteer_update_assignment.html', context)


@login_required
def volunteer_history(request):
    """View volunteer's assignment history"""
    # Ensure profile exists
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=2)
    
    if not profile.is_volunteer:
        messages.error(request, '⚠️ Access denied. Volunteer access only.')
        return redirect('blog-home')
    
    try:
        volunteer_profile = request.user.volunteer_profile
    except VolunteerProfile.DoesNotExist:
        messages.info(request, '⚠️ Please complete your volunteer profile first.')
        return redirect('volunteer-profile-setup')
    
    assignments = Assignment.objects.filter(
        volunteer=volunteer_profile
    ).select_related('request').order_by('-assigned_at')
    
    # Pagination
    paginator = Paginator(assignments, 20)
    page_number = request.GET.get('page')
    assignments_page = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total_assignments': assignments.count(),
        'completed': assignments.filter(status='completed').count(),
        'in_progress': assignments.filter(status__in=['accepted', 'in_progress']).count(),
        'pending': assignments.filter(status='pending').count(),
        'total_hours': volunteer_profile.total_hours_volunteered,
        'rating': volunteer_profile.rating,
        'tasks_completed': volunteer_profile.tasks_completed
    }
    
    context = {
        'assignments': assignments_page,
        'stats': stats,
        'volunteer_profile': volunteer_profile
    }
    
    return render(request, 'raksha/volunteer_history.html', context)


# ============= User Advanced Features =============

@login_required
def user_request_history(request):
    """View user's request history"""
    my_requests = CrisisRequest.objects.filter(
        reporter=request.user
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(my_requests, 20)
    page_number = request.GET.get('page')
    requests_page = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total': my_requests.count(),
        'pending': my_requests.filter(status='submitted').count(),
        'in_progress': my_requests.filter(status__in=['verified', 'approved', 'in_progress']).count(),
        'completed': my_requests.filter(status='completed').count(),
        'cancelled': my_requests.filter(status='cancelled').count()
    }
    
    context = {
        'requests': requests_page,
        'stats': stats
    }
    
    return render(request, 'raksha/user_request_history.html', context)


@login_required
def submit_feedback(request):
    """Submit feedback for volunteer or NGO"""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            try:
                feedback = form.save(commit=False)
                feedback.submitted_by = request.user
                feedback.save()
                
                # Update ratings
                if feedback.volunteer:
                    # Recalculate volunteer rating
                    avg_rating = Feedback.objects.filter(
                        volunteer=feedback.volunteer
                    ).aggregate(Avg('rating'))['rating__avg']
                    feedback.volunteer.rating = avg_rating or 0.0
                    feedback.volunteer.save()
                
                messages.success(request, f'✅ Thank you! Your feedback has been submitted successfully.')
                return redirect('user-dashboard')
            except Exception as e:
                messages.error(request, f'⚠️ Error submitting feedback: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        form = FeedbackForm()
        
        # Pre-populate from query params
        assignment_id = request.GET.get('assignment')
        if assignment_id:
            try:
                assignment = Assignment.objects.get(id=assignment_id)
                form.fields['assignment'].initial = assignment
                form.fields['volunteer'].initial = assignment.volunteer
                form.fields['feedback_type'].initial = 'volunteer'
            except Assignment.DoesNotExist:
                messages.warning(request, '⚠️ Assignment not found.')
    
    context = {
        'form': form
    }
    
    return render(request, 'raksha/feedback_form.html', context)


@login_required
def ngo_profile_setup(request):
    """NGO can setup/edit their profile"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied. NGO access only.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
    except NGOProfile.DoesNotExist:
        ngo_profile = None
    
    if request.method == 'POST':
        form = NGOProfileForm(request.POST)
        if form.is_valid():
            ngo_prof = form.save(commit=False)
            if not ngo_profile:
                ngo_prof.user = request.user
                ngo_prof.verified = False  # Needs admin verification
            ngo_prof.save()
            form.save_m2m()  # Save many-to-many relations
            messages.success(request, 'NGO profile updated successfully. Awaiting admin verification.')
            return redirect('ngo-dashboard')
    else:
        form = NGOProfileForm(instance=ngo_profile)
    
    context = {
        'form': form,
        'ngo_profile': ngo_profile
    }
    
    return render(request, 'raksha/ngo_profile_form.html', context)


# ============= Public Views (No Login Required) =============

def view_emergency_alerts_public(request):
    """Public view for emergency alerts (no login required)"""
    alerts = EmergencyAlert.objects.filter(active=True).order_by('-created_at')
    
    context = {
        'alerts': alerts,
    }
    
    return render(request, 'raksha/emergency_alerts.html', context)


def view_shelters_public(request):
    """Public view for shelters (no login required)"""
    shelters = Shelter.objects.filter(status__in=['active', 'full', 'inactive'])
    status_filter = request.GET.get('status')
    if status_filter in ['active', 'full', 'inactive']:
        shelters = shelters.filter(status=status_filter)
    shelters = shelters.order_by('name')
    
    context = {
        'shelters': shelters,
    }
    
    return render(request, 'raksha/shelters.html', context)


def view_safety_tips_public(request):
    """Public view for safety tips (no login required)"""
    disaster_type = request.GET.get('type')
    
    if disaster_type:
        tips = SafetyTip.objects.filter(
            disaster_type_id=disaster_type,
            is_active=True
        ).order_by('-priority')
    else:
        tips = SafetyTip.objects.filter(is_active=True).select_related('disaster_type').order_by('-priority')
    
    context = {
        'tips': tips,
        'disaster_types': DisasterType.objects.all(),
    }
    
    return render(request, 'raksha/safety_tips.html', context)


def view_emergency_contacts_public(request):
    """Public view for emergency contacts (no login required)"""
    from .models import EmergencyContact
    
    contacts = EmergencyContact.objects.filter(active=True).order_by('name')
    
    context = {
        'contacts': contacts,
    }
    
    return render(request, 'raksha/emergency_contacts.html', context)


@login_required
def resources_view(request):
    """View for managing and viewing resources"""
    from .models import ResourceInventory, ResourceType
    
    # Filter resources based on user role
    if request.user.profile.is_ngo_or_admin:
        try:
            ngo_profile = request.user.ngo_profile
            resources = ResourceInventory.objects.filter(ngo=ngo_profile).select_related('resource_type', 'ngo')
        except:
            resources = ResourceInventory.objects.all().select_related('resource_type', 'ngo')
    else:
        # Show all available resources for regular users
        resources = ResourceInventory.objects.filter(quantity__gt=0).select_related('resource_type', 'ngo')
    
    resource_types = ResourceType.objects.all()
    
    # Filter by type if specified
    resource_type_filter = request.GET.get('type')
    if resource_type_filter:
        resources = resources.filter(resource_type_id=resource_type_filter)
    
    context = {
        'resources': resources,
        'resource_types': resource_types,
    }
    
    return render(request, 'raksha/resources.html', context)


@login_required
def donations_view(request):
    """View for managing and viewing donations"""
    from .models import Donation, DonationMedia
    
    # Filter donations based on user role
    if request.user.profile.is_ngo_or_admin:
        try:
            ngo_profile = request.user.ngo_profile
            # NGOs see donations for their assigned crisis requests
            donations = Donation.objects.filter(
                request__assigned_ngo=ngo_profile
            ).select_related('donor', 'request').prefetch_related('media').order_by('-created_at')
        except NGOProfile.DoesNotExist:
            # If no NGO profile, show all donations (for system admins)
            messages.info(request, 'No NGO profile found. Showing all donations.')
            donations = Donation.objects.all().select_related('donor', 'request').prefetch_related('media').order_by('-created_at')
        except Exception as e:
            # Handle any other errors
            messages.error(request, f'Error loading donations: {str(e)}')
            donations = Donation.objects.all().select_related('donor', 'request').prefetch_related('media').order_by('-created_at')
    else:
        # Show user's own donations
        donations = Donation.objects.filter(donor=request.user).select_related('request').prefetch_related('media').order_by('-created_at')
    
    # Get all media uploaded by the user
    all_media = DonationMedia.objects.filter(uploaded_by=request.user).prefetch_related('donation').order_by('-created_at')
    
    # Calculate total donations
    from django.db.models import Sum
    total_money = donations.filter(donation_type='money').aggregate(Sum('amount'))['amount__sum'] or 0
    total_donations = donations.count()
    
    context = {
        'donations': donations,
        'all_media': all_media,
        'total_money': total_money,
        'total_donations': total_donations,
        'is_ngo': request.user.profile.is_ngo_or_admin,
    }
    
    return render(request, 'raksha/donations.html', context)


@login_required
def create_donation(request):
    """Create a new donation"""
    if request.method == 'POST':
        form = DonationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                donation = form.save(commit=False)
                donation.donor = request.user
                donation.save()
                
                messages.success(
                    request, 
                    f'✅ Thank you for your generous donation! '
                    f'Donation #{donation.id} recorded successfully.'
                )
                return redirect('donations')
            except Exception as e:
                messages.error(request, f'⚠️ Error recording donation: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        form = DonationForm()
        
        # Pre-populate request if provided in URL
        request_id = request.GET.get('request')
        if request_id:
            form.fields['request'].initial = request_id
    
    context = {
        'form': form,
        'is_create': True
    }
    
    return render(request, 'raksha/donation_form.html', context)


@login_required
def edit_donation(request, donation_id):
    """Edit an existing donation (owner or NGO can edit)"""
    donation = get_object_or_404(Donation, id=donation_id)
    
    # Check permissions
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=3)
    
    if donation.donor != request.user and not profile.is_ngo_or_admin:
        messages.error(request, '⚠️ You do not have permission to edit this donation.')
        return redirect('donations')
    
    if request.method == 'POST':
        form = DonationForm(request.POST, request.FILES, instance=donation)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'✅ Donation #{donation.id} updated successfully.')
                return redirect('donations')
            except Exception as e:
                messages.error(request, f'⚠️ Error updating donation: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        form = DonationForm(instance=donation)
    
    context = {
        'form': form,
        'donation': donation,
        'is_edit': True
    }
    
    return render(request, 'raksha/donation_form.html', context)


@login_required
def delete_donation(request, donation_id):
    """Delete a donation (owner or admin can delete)"""
    donation = get_object_or_404(Donation, id=donation_id)
    
    # Check permissions
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=3)
    
    if donation.donor != request.user and not profile.is_ngo_or_admin:
        messages.error(request, '⚠️ You do not have permission to delete this donation.')
        return redirect('donations')
    
    if request.method == 'POST':
        try:
            donation_id_copy = donation.id
            donation.delete()
            messages.success(request, f'✅ Donation #{donation_id_copy} deleted successfully.')
        except Exception as e:
            messages.error(request, f'⚠️ Error deleting donation: {str(e)}')
        return redirect('donations')
    
    context = {
        'donation': donation
    }
    
    return render(request, 'raksha/confirm_delete_donation.html', context)


@login_required
def edit_feedback(request, feedback_id):
    """Edit existing feedback (owner can edit)"""
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    # Only the person who submitted can edit
    if feedback.submitted_by != request.user:
        messages.error(request, '⚠️ You do not have permission to edit this feedback.')
        return redirect('user-dashboard')
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            try:
                form.save()
                
                # Update ratings
                if feedback.volunteer:
                    avg_rating = Feedback.objects.filter(
                        volunteer=feedback.volunteer
                    ).aggregate(Avg('rating'))['rating__avg']
                    feedback.volunteer.rating = avg_rating or 0.0
                    feedback.volunteer.save()
                
                messages.success(request, f'✅ Feedback #{feedback.id} updated successfully.')
                return redirect('user-dashboard')
            except Exception as e:
                messages.error(request, f'⚠️ Error updating feedback: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        form = FeedbackForm(instance=feedback)
    
    context = {
        'form': form,
        'feedback': feedback,
        'is_edit': True
    }
    
    return render(request, 'raksha/feedback_form.html', context)


@login_required
def delete_feedback(request, feedback_id):
    """Delete feedback (owner or admin can delete)"""
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    # Check permissions
    try:
        profile = request.user.profile
    except:
        from users.models import Profile
        profile = Profile.objects.create(user=request.user, role=3)
    
    if feedback.submitted_by != request.user and not profile.is_ngo_or_admin:
        messages.error(request, '⚠️ You do not have permission to delete this feedback.')
        return redirect('user-dashboard')
    
    if request.method == 'POST':
        try:
            # Store volunteer for rating recalculation
            volunteer = feedback.volunteer
            feedback_id_copy = feedback.id
            
            feedback.delete()
            
            # Recalculate volunteer rating
            if volunteer:
                avg_rating = Feedback.objects.filter(
                    volunteer=volunteer
                ).aggregate(Avg('rating'))['rating__avg']
                volunteer.rating = avg_rating or 0.0
                volunteer.save()
            
            messages.success(request, f'✅ Feedback #{feedback_id_copy} deleted successfully.')
        except Exception as e:
            messages.error(request, f'⚠️ Error deleting feedback: {str(e)}')
        
        return redirect('user-dashboard')
    
    context = {
        'feedback': feedback
    }
    
    return render(request, 'raksha/confirm_delete_feedback.html', context)


@login_required
def feedback_list(request):
    """View all feedback (filtered by role)"""
    profile = request.user.profile
    
    if profile.is_ngo_or_admin:
        # NGOs see feedback for their organization
        try:
            ngo_profile = request.user.ngo_profile
            feedback = Feedback.objects.filter(
                Q(ngo=ngo_profile) | Q(assignment__request__assigned_ngo=ngo_profile)
            ).select_related('submitted_by', 'volunteer__user', 'ngo').order_by('-created_at')
        except:
            feedback = Feedback.objects.all().select_related('submitted_by', 'volunteer__user', 'ngo').order_by('-created_at')
    elif profile.is_volunteer:
        # Volunteers see feedback about themselves
        try:
            volunteer_profile = request.user.volunteer_profile
            feedback = Feedback.objects.filter(volunteer=volunteer_profile).select_related('submitted_by').order_by('-created_at')
        except:
            feedback = Feedback.objects.filter(submitted_by=request.user).select_related('volunteer__user', 'ngo').order_by('-created_at')
    else:
        # Regular users see their own feedback
        feedback = Feedback.objects.filter(submitted_by=request.user).select_related('volunteer__user', 'ngo').order_by('-created_at')
    
    context = {
        'feedback_list': feedback,
    }
    
    return render(request, 'raksha/feedback_list.html', context)


@login_required
def ngo_manage_requests(request):
    """NGOs can manage all requests assigned to them"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
        
        # Filter by status if provided
        status_filter = request.GET.get('status', 'all')
        view_filter = request.GET.get('view', 'all')  # 'all', 'assigned', 'unassigned'
        
        # Show both assigned and unassigned requests
        if view_filter == 'assigned':
            requests = CrisisRequest.objects.filter(assigned_ngo=ngo_profile)
        elif view_filter == 'unassigned':
            requests = CrisisRequest.objects.filter(
                assigned_ngo__isnull=True,
                status__in=['submitted', 'verified', 'pending']
            )
        else:  # 'all' - show both assigned and available unassigned
            assigned = CrisisRequest.objects.filter(assigned_ngo=ngo_profile)
            unassigned = CrisisRequest.objects.filter(
                assigned_ngo__isnull=True,
                status__in=['submitted', 'verified', 'pending']
            )
            requests = assigned | unassigned
        
        if status_filter != 'all':
            requests = requests.filter(status=status_filter)
        
        requests = requests.select_related('disaster_type', 'reporter').order_by('-priority_score', '-created_at')
        
        # Pagination
        paginator = Paginator(requests, 20)
        page_number = request.GET.get('page')
        requests_page = paginator.get_page(page_number)
        
        # Stats - include unassigned requests
        assigned_qs = CrisisRequest.objects.filter(assigned_ngo=ngo_profile)
        _sync_requests_from_assignments(assigned_qs)
        unassigned_qs = CrisisRequest.objects.filter(
            assigned_ngo__isnull=True,
            status__in=['submitted', 'verified', 'pending']
        )
        
        stats = {
            'total': assigned_qs.count() + unassigned_qs.count(),
            'assigned': assigned_qs.count(),
            'unassigned': unassigned_qs.count(),
            'pending': assigned_qs.filter(status__in=['submitted', 'verified', 'pending']).count() + unassigned_qs.count(),
            'in_progress': assigned_qs.filter(status='in_progress').count(),
            'completed': assigned_qs.filter(status='completed').count(),
        }
        
    except NGOProfile.DoesNotExist:
        messages.error(request, 'NGO profile not found.')
        return redirect('ngo-profile-setup')
    
    context = {
        'requests': requests_page,
        'stats': stats,
        'status_filter': status_filter,
        'view_filter': view_filter,
    }
    
    return render(request, 'raksha/ngo_manage_requests.html', context)


@login_required
def ngo_claim_request(request, request_id):
    """NGO can claim an unassigned crisis request"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    try:
        ngo_profile = request.user.ngo_profile
    except NGOProfile.DoesNotExist:
        messages.error(request, 'NGO profile not found.')
        return redirect('ngo-profile-setup')
    
    crisis_request = get_object_or_404(CrisisRequest, id=request_id)
    
    # Check if request is unassigned
    if crisis_request.assigned_ngo is not None:
        messages.warning(request, 'This crisis request is already assigned to another NGO.')
        return redirect('ngo-manage-requests')
    
    # Check if request is in a verifiable status
    if crisis_request.status not in ['submitted', 'verified', 'pending']:
        messages.warning(request, 'This crisis request cannot be claimed in its current status.')
        return redirect('ngo-manage-requests')
    
    # Assign request to this NGO
    crisis_request.assigned_ngo = ngo_profile
    
    # If not verified yet, set to pending for this NGO to verify
    if crisis_request.status == 'submitted':
        crisis_request.status = 'pending'
    
    crisis_request.save()
    
    messages.success(
        request, 
        f'✅ Crisis Request #{crisis_request.id} has been successfully claimed by {ngo_profile.organization_name}!'
    )
    return redirect('ngo-manage-requests')


@login_required
def ngo_edit_request(request, request_id):
    """NGO can edit requests assigned to them"""
    profile = request.user.profile
    
    if not profile.is_ngo_or_admin:
        messages.error(request, 'Access denied.')
        return redirect('blog-home')
    
    crisis_request = get_object_or_404(CrisisRequest, id=request_id)
    
    # Check if NGO is assigned to this request
    try:
        ngo_profile = request.user.ngo_profile
        if crisis_request.assigned_ngo != ngo_profile and not request.user.is_staff:
            messages.error(request, 'You can only edit requests assigned to your organization.')
            return redirect('ngo-dashboard')
    except NGOProfile.DoesNotExist:
        messages.error(request, 'NGO profile not found.')
        return redirect('ngo-profile-setup')
    
    if request.method == 'POST':
        form = CrisisRequestForm(request.POST, request.FILES, instance=crisis_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Request updated successfully.')
            return redirect('ngo-manage-requests')
    else:
        form = CrisisRequestForm(instance=crisis_request)
    
    context = {
        'form': form,
        'crisis_request': crisis_request,
        'is_edit': True
    }
    
    return render(request, 'raksha/create_request.html', context)


@login_required
def upload_donation_media(request):
    """Upload media (images/videos) for donation documentation"""
    if request.method == 'POST':
        media_file = request.FILES.get('media_file')
        description = request.POST.get('description', '')
        
        if not media_file:
            messages.error(request, 'Please select a file to upload.')
            return redirect('donations')
        
        # Determine media type
        content_type = media_file.content_type
        if content_type.startswith('image/'):
            media_type = 'image'
        elif content_type.startswith('video/'):
            media_type = 'video'
        else:
            messages.error(request, 'Invalid file type. Please upload an image or video.')
            return redirect('donations')
        
        # Check file size (50MB max)
        if media_file.size > 50 * 1024 * 1024:
            messages.error(request, 'File size exceeds 50MB limit.')
            return redirect('donations')
        
        try:
            from .models import DonationMedia
            # Create media record
            media = DonationMedia.objects.create(
                uploaded_by=request.user,
                media_type=media_type,
                file=media_file,
                description=description
            )
            messages.success(request, f'{media_type.title()} uploaded successfully!')
        except Exception as e:
            messages.error(request, f'Error uploading file: {str(e)}')
        
        return redirect('donations')
    
    return redirect('donations')
