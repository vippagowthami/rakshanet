from django.db import models
from django.contrib.auth.models import User

class ProfileManager(models.Manager):
    """Custom manager for Profile model with role-based queries"""
    
    def ngos_and_admins(self):
        """Get all NGO and Admin profiles (role=1)"""
        return self.filter(role=1)
    
    def volunteers(self):
        """Get all Volunteer profiles (role=2)"""
        return self.filter(role=2)
    
    def common_users(self):
        """Get all Common User profiles (role=3)"""
        return self.filter(role=3)
    
    def by_role(self, role):
        """Get profiles by specific role"""
        return self.filter(role=role)

class Profile(models.Model):
    ROLE_CHOICES = [
        (1, 'Admin or NGO'),
        (2, 'Volunteer'),
        (3, 'Common User (Need Help)'),
    ]
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    image = models.ImageField(default = 'default.jpg', upload_to='profile_pics')
    role = models.IntegerField(choices=ROLE_CHOICES, default=3)
    # Keep ngo field for backward compatibility
    ngo = models.BooleanField(default=False)
    
    objects = ProfileManager()

    def __str__(self):
        return f'{self.user.username} Profile'
    
    @property
    def is_ngo_or_admin(self):
        return self.role == 1
    
    @property
    def is_volunteer(self):
        return self.role == 2
    
    @property
    def is_common_user(self):
        return self.role == 3
    
class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default="")


    def __str__(self):
        return self.name