from django.core.mail import send_mail
from django.conf import settings
from .models import VolunteerProfile, Assignment
from .utils import find_nearest_available_volunteer


def assign_volunteer_to_request(request_obj, max_km=50.0):
    """Find nearest available volunteer and create an Assignment. Returns Assignment or None."""
    volunteers = VolunteerProfile.objects.filter(available=True)
    volunteer = find_nearest_available_volunteer(request_obj, volunteers, max_km=max_km)
    if not volunteer:
        return None
    ass = Assignment.objects.create(request=request_obj, volunteer=volunteer)
    # mark volunteer unavailable
    volunteer.available = False
    volunteer.save(update_fields=['available'])

    # notify volunteer via email if possible
    subject = f"New assignment: Request {request_obj.id}"
    message = f"You have been assigned to request {request_obj.id}.\nAddress: {request_obj.address}\nUrgency: {request_obj.urgency}\nContact: {request_obj.phone or 'N/A'}"
    recipient = []
    try:
        if volunteer.user.email:
            recipient.append(volunteer.user.email)
        if recipient:
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient, fail_silently=True)
    except Exception:
        pass

    # notify reporter (if exists)
    try:
        if request_obj.reporter and request_obj.reporter.email:
            send_mail(f"Your request {request_obj.id} assigned", f"A volunteer ({volunteer.user.username}) has been assigned.", settings.EMAIL_HOST_USER, [request_obj.reporter.email], fail_silently=True)
    except Exception:
        pass

    return ass
