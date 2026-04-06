from users.models import Profile


class EnsureUserProfileMiddleware:
    """Guarantee authenticated users always have a Profile object."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            # Some legacy accounts were created before profile signals were stable.
            Profile.objects.get_or_create(user=user)
        return self.get_response(request)
