from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

# Import raksha models but with try/except to avoid circular imports
def get_ngo_profile_model():
    try:
        from raksha.models import NGOProfile
        return NGOProfile
    except:
        return None

def get_volunteer_profile_model():
    try:
        from raksha.models import VolunteerProfile
        return VolunteerProfile
    except:
        return None

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Create basic profile
        profile, _ = Profile.objects.get_or_create(user=instance)
        
        # Create NGO profile if not exists (default creation, not linked to role yet)
        NGOProfile = get_ngo_profile_model()
        if NGOProfile:
            try:
                NGOProfile.objects.get_or_create(
                    user=instance,
                    defaults={
                        'organization_name': f'{instance.username}\'s Organization',
                        'contact_person': instance.get_full_name() or instance.username,
                        'phone': '+1-000-000-0000',
                        'email': instance.email,
                        'address': 'Address TBD',
                        'service_areas': 'Nationwide'
                    }
                )
            except Exception as e:
                print(f"Error creating NGOProfile: {e}")
        
        # Create Volunteer profile if not exists
        VolunteerProfile = get_volunteer_profile_model()
        if VolunteerProfile:
            try:
                VolunteerProfile.objects.get_or_create(
                    user=instance,
                    defaults={
                        'phone': '+1-000-000-0000',
                        'primary_skill': 'general'
                    }
                )
            except Exception as e:
                print(f"Error creating VolunteerProfile: {e}")

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        try:
            # Ensure role is a valid integer
            if instance.profile.role is None or not isinstance(instance.profile.role, int):
                instance.profile.role = 3  # Set to common user as default
            instance.profile.save(update_fields=['role', 'ngo'])
        except Exception as e:
            # Silently fail to avoid breaking login process
            print(f"Error saving profile: {e}")
            pass