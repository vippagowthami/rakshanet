"""
Role-based permissions and access control for RakshaNet users.
"""

from django.core.exceptions import PermissionDenied
from .models import Profile


class RolePermissionMixin:
    """Mixin to check user roles in views"""
    
    required_role = None  # Set in subclass: 1 (Admin/NGO), 2 (Volunteer), 3 (Common User), or a list
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('login')
        
        if not self._check_role_permission(request.user):
            raise PermissionDenied("You don't have permission to access this page.")
        
        return super().dispatch(request, *args, **kwargs)
    
    def _check_role_permission(self, user):
        """Check if user has required role"""
        try:
            profile = user.profile
            if isinstance(self.required_role, list):
                return profile.role in self.required_role
            else:
                return profile.role == self.required_role
        except Profile.DoesNotExist:
            return False


def require_role(*roles):
    """Decorator to require specific user roles"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect('login')
            
            try:
                profile = request.user.profile
                if profile.role not in roles:
                    raise PermissionDenied(f"This action requires one of these roles: {roles}")
            except Profile.DoesNotExist:
                raise PermissionDenied("User profile not found")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def is_ngo_or_admin(user):
    """Check if user is NGO or Admin (role=1)"""
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role == 1
    except Profile.DoesNotExist:
        return False


def is_volunteer(user):
    """Check if user is Volunteer (role=2)"""
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role == 2
    except Profile.DoesNotExist:
        return False


def is_common_user(user):
    """Check if user is Common User (role=3)"""
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role == 3
    except Profile.DoesNotExist:
        return False


def get_user_role_display(user):
    """Get the display name of user's role"""
    try:
        profile = user.profile
        return dict(Profile.ROLE_CHOICES).get(profile.role, 'Unknown')
    except Profile.DoesNotExist:
        return 'No Role'
