"""
Template tags for RakshaNet user roles and permissions
"""

from django import template
from django.contrib.auth.models import User
from users.models import Profile

register = template.Library()


@register.filter
def is_ngo(user):
    """Check if user is NGO/Admin"""
    try:
        return user.profile.role == 1
    except:
        return False


@register.filter
def is_volunteer(user):
    """Check if user is Volunteer"""
    try:
        return user.profile.role == 2
    except:
        return False


@register.filter
def is_common_user(user):
    """Check if user needs help"""
    try:
        return user.profile.role == 3
    except:
        return False


@register.filter
def user_role_name(user):
    """Get user's role name"""
    try:
        profile = user.profile
        return dict(Profile.ROLE_CHOICES).get(profile.role, 'Unknown')
    except:
        return 'Unknown'


@register.filter
def user_role_id(user):
    """Get user's role ID"""
    try:
        return user.profile.role
    except:
        return None


@register.simple_tag
def ngo_helpers_count():
    """Get count of NGO/Admin users"""
    return Profile.objects.ngos_and_admins().count()


@register.simple_tag
def volunteers_count():
    """Get count of volunteers"""
    return Profile.objects.volunteers().count()


@register.simple_tag
def users_needing_help_count():
    """Get count of common users needing help"""
    return Profile.objects.common_users().count()
