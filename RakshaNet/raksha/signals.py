from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CrisisRequest
from .utils import compute_priority_score
from .assignment import assign_volunteer_to_request


@receiver(post_save, sender=CrisisRequest)
def update_priority_on_save(sender, instance, created, **kwargs):
    """Compute and save priority_score when a request is saved."""
    try:
        score = compute_priority_score(instance)
        if instance.priority_score != score:
            instance.priority_score = score
            # avoid infinite recursion: update fields only
            instance.__class__.objects.filter(pk=instance.pk).update(priority_score=score)
    except Exception:
        # avoid breaking request save in case of any error
        pass

    # attempt auto-assignment for high-priority requests with no assignments
    try:
        # threshold can be tuned; use 70 by default
        if instance.priority_score >= 70.0:
            # check if already assigned
            if not instance.assignments.exists():
                assign_volunteer_to_request(instance, max_km=50.0)
    except Exception:
        pass
