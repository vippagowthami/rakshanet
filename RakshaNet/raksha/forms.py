"""
Forms for RakshaNet disaster management system
"""
from django import forms
from django.contrib.auth.models import User
from .models import (
    CrisisRequest, VolunteerProfile, NGOProfile, Shelter, EmergencyAlert,
    ResourceInventory, Donation, Assignment, Feedback, SafetyTip, DisasterType,
    ResourceType
)


class CrisisRequestForm(forms.ModelForm):
    """Form for creating and updating crisis requests"""
    
    urgency = forms.ChoiceField(
        choices=CrisisRequest.URGENCY,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        required=True,
        initial='medium',
        label='Urgency Level'
    )
    
    class Meta:
        model = CrisisRequest
        fields = [
            'disaster_type', 'name', 'phone', 'description', 'address',
            'latitude', 'longitude', 'resources_required', 'people_affected',
            'urgency', 'image', 'video_url'
        ]
        widgets = {
            'disaster_type': forms.Select(attrs={
                'class': 'form-control',
                'required': False
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact number',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the emergency situation',
                'required': True
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full address',
                'required': True
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Latitude (optional)',
                'step': '0.000001'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Longitude (optional)',
                'step': '0.000001'
            }),
            'resources_required': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List required resources (food, water, medical supplies, etc.)'
            }),
            'people_affected': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'YouTube/Video link (optional)'
            })
        }

class VolunteerProfileForm(forms.ModelForm):
    """Form for volunteer profile management"""
    
    class Meta:
        model = VolunteerProfile
        fields = [
            'phone', 'alternate_phone', 'primary_skill', 'skills',
            'experience_years', 'latitude', 'longitude', 'has_vehicle',
            'vehicle_type', 'emergency_contact_name', 'emergency_contact_phone',
            'languages_spoken', 'certifications', 'available'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'alternate_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'primary_skill': forms.Select(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List your skills (comma separated)'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'has_vehicle': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'vehicle_type': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'languages_spoken': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., English, Hindi, Telugu'}),
            'certifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class NGOProfileForm(forms.ModelForm):
    """Form for NGO profile management"""
    
    class Meta:
        model = NGOProfile
        fields = [
            'organization_name', 'registration_number', 'contact_person',
            'phone', 'email', 'address', 'latitude', 'longitude',
            'service_areas', 'specialization', 'available_resources'
        ]
        widgets = {
            'organization_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'service_areas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Areas where you operate (comma separated)'}),
            'specialization': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '8'}),
            'available_resources': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}),
        }


class ShelterForm(forms.ModelForm):
    """Form for shelter management"""
    
    class Meta:
        model = Shelter
        fields = [
            'name', 'address', 'latitude', 'longitude', 'capacity',
            'current_occupancy', 'contact_number', 'facilities',
            'disaster_types', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'required': True}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'required': True}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'required': True}),
            'current_occupancy': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'facilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List facilities (comma separated)'}),
            'disaster_types': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '6'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class EmergencyAlertForm(forms.ModelForm):
    """Form for creating emergency alerts"""
    
    class Meta:
        model = EmergencyAlert
        fields = [
            'title', 'message', 'disaster_type', 'severity', 'affected_area',
            'latitude', 'longitude', 'radius_km', 'expires_at'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Alert title'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True, 'placeholder': 'Detailed alert message'}),
            'disaster_type': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'affected_area': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Location/Area'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'radius_km': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'value': 50}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class ResourceInventoryForm(forms.ModelForm):
    """Form for managing resource inventory"""
    
    class Meta:
        model = ResourceInventory
        fields = ['resource_type', 'quantity', 'unit', 'location', 'expiry_date']
        widgets = {
            'resource_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01', 'required': True}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'e.g., kg, liters, units'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class DonationForm(forms.ModelForm):
    """Form for recording donations"""
    
    class Meta:
        model = Donation
        fields = ['request', 'donation_type', 'amount', 'note', 'image']
        widgets = {
            'request': forms.Select(attrs={'class': 'form-control'}),
            'donation_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class AssignmentForm(forms.ModelForm):
    """Form for creating assignments"""
    
    class Meta:
        model = Assignment
        fields = ['request', 'volunteer', 'notes']
        widgets = {
            'request': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'volunteer': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class FeedbackForm(forms.ModelForm):
    """Form for submitting feedback"""
    
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'volunteer', 'ngo', 'assignment', 'rating', 'comment']
        widgets = {
            'feedback_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'volunteer': forms.Select(attrs={'class': 'form-control'}),
            'ngo': forms.Select(attrs={'class': 'form-control'}),
            'assignment': forms.Select(attrs={'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class SafetyTipForm(forms.ModelForm):
    """Form for managing safety tips"""
    
    class Meta:
        model = SafetyTip
        fields = ['disaster_type', 'title', 'content', 'language', 'priority']
        widgets = {
            'disaster_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'required': True}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class CrisisRequestVerifyForm(forms.Form):
    """Form for verifying crisis requests"""
    action = forms.ChoiceField(
        choices=[('verify', 'Verify'), ('reject', 'Reject')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add notes (optional)'}),
        required=False
    )
    assigned_ngo = forms.ModelChoiceField(
        queryset=NGOProfile.objects.filter(verified=True, active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label="Assign to NGO (optional)"
    )


class AssignmentUpdateForm(forms.ModelForm):
    """Form for updating assignment status"""
    
    class Meta:
        model = Assignment
        fields = ['status', 'notes', 'hours_spent']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hours_spent': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.5'}),
        }
