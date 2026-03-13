#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_start.settings')
django.setup()

from users.models import Profile

# Fix all invalid role values
invalid_profiles = Profile.objects.all()
for profile in invalid_profiles:
    if profile.role is None or not isinstance(profile.role, int) or profile.role not in [1, 2, 3]:
        print(f"Fixing user {profile.user.username}: role={profile.role} -> 3 (Common User)")
        profile.role = 3
        profile.ngo = False
        profile.save(update_fields=['role', 'ngo'])

print("Done! All profiles fixed.")
