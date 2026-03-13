from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class DisasterType(models.Model):
    """Model for different types of disasters"""
    DISASTER_CATEGORIES = [
        ('natural', _('Natural Disaster')),
        ('man_made', _('Man-made Disaster')),
        ('health', _('Health Emergency')),
        ('conflict', _('Conflict/War')),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=DISASTER_CATEGORIES, default='natural')
    description = models.TextField(blank=True)
    severity_multiplier = models.FloatField(default=1.0)  # Used for priority calculation
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Disaster Type')
        verbose_name_plural = _('Disaster Types')


class ResourceType(models.Model):
    """Model for different types of resources needed in disasters"""
    RESOURCE_CATEGORIES = [
        ('food', _('Food & Water')),
        ('medical', _('Medical Supplies')),
        ('shelter', _('Shelter & Clothing')),
        ('rescue', _('Rescue Equipment')),
        ('communication', _('Communication Tools')),
        ('transport', _('Transportation')),
        ('financial', _('Financial Aid')),
        ('other', _('Other')),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=RESOURCE_CATEGORIES, default='other')
    unit_of_measurement = models.CharField(max_length=50, blank=True)  # e.g., kg, liters, units
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    class Meta:
        verbose_name = _('Resource Type')
        verbose_name_plural = _('Resource Types')


class NGOProfile(models.Model):
    """Extended profile for NGOs and organizations"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ngo_profile')
    organization_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100, blank=True)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    service_areas = models.TextField(help_text=_("Areas where NGO operates (comma separated)"))
    specialization = models.ManyToManyField(DisasterType, blank=True)
    available_resources = models.ManyToManyField(ResourceType, blank=True)
    verified = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.organization_name
    
    class Meta:
        verbose_name = _('NGO Profile')
        verbose_name_plural = _('NGO Profiles')


class Shelter(models.Model):
    """Model for emergency shelters"""
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('full', _('Full Capacity')),
        ('inactive', _('Inactive')),
    ]
    
    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    capacity = models.IntegerField(help_text=_("Maximum number of people"))
    current_occupancy = models.IntegerField(default=0)
    managed_by = models.ForeignKey(NGOProfile, null=True, blank=True, on_delete=models.SET_NULL)
    contact_number = models.CharField(max_length=32)
    facilities = models.TextField(help_text=_("Available facilities (comma separated)"))
    disaster_types = models.ManyToManyField(DisasterType, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def available_capacity(self):
        return max(0, self.capacity - self.current_occupancy)
    
    def is_available(self):
        return self.status == 'active' and self.current_occupancy < self.capacity
    
    def __str__(self):
        return f"{self.name} - {self.available_capacity()}/{self.capacity}"
    
    class Meta:
        verbose_name = _('Shelter')
        verbose_name_plural = _('Shelters')


class EmergencyAlert(models.Model):
    """Model for broadcasting emergency alerts"""
    SEVERITY_LEVELS = [
        ('info', _('Information')),
        ('warning', _('Warning')),
        ('critical', _('Critical')),
        ('extreme', _('Extreme Emergency')),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    disaster_type = models.ForeignKey(DisasterType, on_delete=models.SET_NULL, null=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='warning')
    affected_area = models.CharField(max_length=200, help_text=_("Location/Area affected"))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    radius_km = models.FloatField(default=50, help_text=_("Alert radius in kilometers"))
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_severity_display()}"
    
    class Meta:
        verbose_name = _('Emergency Alert')
        verbose_name_plural = _('Emergency Alerts')
        ordering = ['-created_at']


class CrisisRequest(models.Model):
    STATUS_CHOICES = [
        ('submitted', _('Submitted')),
        ('verified', _('Verified')),
        ('approved', _('Approved')),
        ('allocated', _('Allocated')),
        ('in_progress', _('In Progress')),
        ('delivered', _('Delivered')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    URGENCY = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='crisis_requests')
    disaster_type = models.ForeignKey(DisasterType, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=512, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    resources_required = models.TextField(blank=True, help_text=_("List required resources"))
    people_affected = models.IntegerField(default=1, help_text=_("Number of people affected"))
    urgency = models.CharField(max_length=10, choices=URGENCY, default='medium')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='submitted')
    priority_score = models.FloatField(default=0.0)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='verified_requests')
    image = models.ImageField(upload_to='crisis_images/', null=True, blank=True, help_text=_("Upload image of the situation"))
    video_url = models.URLField(blank=True, help_text=_("Link to video documentation"))
    assigned_ngo = models.ForeignKey(NGOProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_requests')
    notes = models.TextField(blank=True, help_text=_("Internal notes for tracking"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.id} - {self.status} - {self.urgency}"
    
    class Meta:
        verbose_name = _('Crisis Request')
        verbose_name_plural = _('Crisis Requests')
        ordering = ['-priority_score', '-created_at']


class VolunteerProfile(models.Model):
    SKILL_CHOICES = [
        ('medical', _('Medical/First Aid')),
        ('rescue', _('Search & Rescue')),
        ('logistics', _('Logistics & Distribution')),
        ('communication', _('Communication')),
        ('counseling', _('Counseling/Psychosocial Support')),
        ('technical', _('Technical Skills')),
        ('driver', _('Driver/Transportation')),
        ('translator', _('Translation Services')),
        ('general', _('General Help')),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='volunteer_profile')
    phone = models.CharField(max_length=32, blank=True)
    alternate_phone = models.CharField(max_length=32, blank=True)
    skills = models.TextField(blank=True, help_text=_("List your skills (comma separated)"))
    primary_skill = models.CharField(max_length=20, choices=SKILL_CHOICES, default='general')
    experience_years = models.IntegerField(default=0, help_text=_("Years of volunteering experience"))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    available = models.BooleanField(default=True)
    has_vehicle = models.BooleanField(default=False)
    vehicle_type = models.CharField(max_length=50, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=32, blank=True)
    languages_spoken = models.CharField(max_length=200, blank=True, help_text=_("Languages you can speak"))
    affiliated_ngo = models.ForeignKey(NGOProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='volunteers')
    certifications = models.TextField(blank=True, help_text=_("Relevant certifications"))
    total_hours_volunteered = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    tasks_completed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Volunteer {self.user.username} - {self.get_primary_skill_display()}"
    
    class Meta:
        verbose_name = _('Volunteer Profile')
        verbose_name_plural = _('Volunteer Profiles')


class Donation(models.Model):
    DONATION_TYPE = [
        ('money', 'Money'),
        ('goods', 'Goods'),
    ]

    donor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    request = models.ForeignKey(CrisisRequest, null=True, blank=True, on_delete=models.SET_NULL, related_name='donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    donation_type = models.CharField(max_length=8, choices=DONATION_TYPE, default='money')
    note = models.TextField(blank=True)
    image = models.ImageField(upload_to='donation_images/', null=True, blank=True, help_text=_("Upload receipt or proof of donation"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donation {self.id} - {self.donation_type}"


class DonationMedia(models.Model):
    """Media documentation for donations and relief efforts"""
    MEDIA_TYPE = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donation_media')
    donation = models.ForeignKey(Donation, null=True, blank=True, on_delete=models.SET_NULL, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE, default='image')
    file = models.FileField(upload_to='donation_media/', help_text=_("Upload image or video"))
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.media_type} - {self.uploaded_by.username} - {self.created_at}"
    
    class Meta:
        verbose_name = _('Donation Media')
        verbose_name_plural = _('Donation Media')
        ordering = ['-created_at']


class Assignment(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    request = models.ForeignKey(CrisisRequest, on_delete=models.CASCADE, related_name='assignments')
    volunteer = models.ForeignKey(VolunteerProfile, on_delete=models.CASCADE, related_name='assignments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    hours_spent = models.FloatField(default=0.0)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Assignment {self.id} - req {self.request.id} -> {self.volunteer.user.username}"
    
    class Meta:
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')


class ResourceInventory(models.Model):
    """Track available resources at NGOs or warehouses"""
    ngo = models.ForeignKey(NGOProfile, on_delete=models.CASCADE, related_name='inventory')
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0.0)
    unit = models.CharField(max_length=50, help_text=_("Unit of measurement"))
    location = models.CharField(max_length=200)
    expiry_date = models.DateField(null=True, blank=True, help_text=_("Expiry date (if applicable)"))
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.resource_type.name} - {self.quantity} {self.unit} at {self.ngo.organization_name}"
    
    class Meta:
        verbose_name = _('Resource Inventory')
        verbose_name_plural = _('Resource Inventories')


class Notification(models.Model):
    """System notifications for users"""
    NOTIFICATION_TYPES = [
        ('alert', _('Emergency Alert')),
        ('assignment', _('New Assignment')),
        ('request_update', _('Request Update')),
        ('donation', _('Donation Received')),
        ('system', _('System Notification')),
    ]
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, help_text=_("Link to related page"))
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']


class CrisisChatMessage(models.Model):
    """Chat messages tied to a crisis request for cross-role coordination."""
    crisis_request = models.ForeignKey(CrisisRequest, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='crisis_chat_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat #{self.id} req {self.crisis_request_id} by {self.sender.username}"

    class Meta:
        verbose_name = _('Crisis Chat Message')
        verbose_name_plural = _('Crisis Chat Messages')
        ordering = ['created_at']


class CommunityChannel(models.Model):
    """Role-aware chat channels for broad coordination."""
    ROLE_SCOPE_CHOICES = [
        ('all', _('All Roles')),
        ('ngo', _('NGO/Admin Only')),
        ('volunteer', _('Volunteer Only')),
        ('user', _('Common User Only')),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    role_scope = models.CharField(max_length=20, choices=ROLE_SCOPE_CHOICES, default='all')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role_scope})"

    class Meta:
        verbose_name = _('Community Channel')
        verbose_name_plural = _('Community Channels')
        ordering = ['name']


class CommunityMessage(models.Model):
    """Messages posted in community channels."""
    channel = models.ForeignKey(CommunityChannel, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_messages')
    message = models.TextField()
    is_urgent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Community #{self.id} channel {self.channel_id} by {self.sender.username}"

    class Meta:
        verbose_name = _('Community Message')
        verbose_name_plural = _('Community Messages')
        ordering = ['created_at']


class AIChatMessage(models.Model):
    """Stores user prompts and generated assistant responses for audit and continuity."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_chat_messages')
    prompt = models.TextField()
    response = models.TextField()
    context_tag = models.CharField(max_length=32, default='general')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI chat #{self.id} for {self.user.username}"

    class Meta:
        verbose_name = _('AI Chat Message')
        verbose_name_plural = _('AI Chat Messages')
        ordering = ['-created_at']


class UserLocationPing(models.Model):
    """Tracks user-reported geolocation updates for nearby service recommendations."""
    SOURCE_CHOICES = [
        ('browser', _('Browser Geolocation')),
        ('manual', _('Manual Entry')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='location_pings')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy_meters = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='browser')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"LocPing {self.user.username} ({self.latitude}, {self.longitude})"

    class Meta:
        verbose_name = _('User Location Ping')
        verbose_name_plural = _('User Location Pings')
        ordering = ['-created_at']


class EmergencyBeacon(models.Model):
    """SOS beacon for instant emergency escalation and responder coordination."""
    STATUS_CHOICES = [
        ('open', _('Open')),
        ('acknowledged', _('Acknowledged')),
        ('resolved', _('Resolved')),
    ]

    triggered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='emergency_beacons')
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_beacons'
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    message = models.CharField(max_length=280, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"SOS #{self.id} by {self.triggered_by.username} ({self.status})"

    class Meta:
        verbose_name = _('Emergency Beacon')
        verbose_name_plural = _('Emergency Beacons')
        ordering = ['-created_at']


class Feedback(models.Model):
    """Feedback and ratings for volunteers, NGOs, or the system"""
    FEEDBACK_TYPES = [
        ('volunteer', _('Volunteer Feedback')),
        ('ngo', _('NGO Feedback')),
        ('system', _('System Feedback')),
    ]
    
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='system')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_feedback')
    volunteer = models.ForeignKey(VolunteerProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='received_feedback')
    ngo = models.ForeignKey(NGOProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='received_feedback')
    assignment = models.ForeignKey(Assignment, null=True, blank=True, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text=_("Rating from 1-5"))
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_feedback_type_display()} - Rating: {self.rating}"
    
    class Meta:
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedback')


class EmergencyContact(models.Model):
    """Important emergency contact numbers for different areas"""
    name = models.CharField(max_length=200, help_text=_("Organization or service name"))
    category = models.CharField(max_length=100, choices=[
        ('police', _('Police/Law Enforcement')),
        ('medical', _('Medical/Ambulance')),
        ('fire', _('Fire Department')),
        ('emergency', _('Emergency Services')),
        ('disaster', _('Disaster Management')),
        ('ngo', _('NGO')),
        ('other', _('Other')),
    ], default='emergency', help_text=_("Category of service"))
    phone_number = models.CharField(max_length=32)
    alternate_number = models.CharField(max_length=32, blank=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True, help_text=_("Additional information about this contact"))
    active = models.BooleanField(default=True)
    available_247 = models.BooleanField(default=True)
    languages_supported = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"
    
    class Meta:
        verbose_name = _('Emergency Contact')
        verbose_name_plural = _('Emergency Contacts')
        ordering = ['category', 'name']


class SafetyTip(models.Model):
    """Safety tips for different disaster types"""
    disaster_type = models.ForeignKey(DisasterType, on_delete=models.CASCADE, related_name='safety_tips')
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=[
        ('before', _('Before Disaster')),
        ('during', _('During Disaster')),
        ('after', _('After Disaster')),
    ], default='before', help_text=_("When this tip should be followed"))
    language = models.CharField(max_length=10, default='en')
    priority = models.IntegerField(default=0, help_text=_("Higher number = higher priority"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.disaster_type.name})"
    
    class Meta:
        verbose_name = _('Safety Tip')
        verbose_name_plural = _('Safety Tips')
        ordering = ['-priority', 'title']