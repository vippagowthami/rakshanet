"""
Utility functions for language switching and management
"""
from django.conf import settings
from django.utils.translation import activate, get_language

def get_available_languages():
    """Returns list of available languages"""
    return settings.LANGUAGES

def set_user_language(request, language_code):
    """Set language preference for user"""
    if language_code in dict(settings.LANGUAGES):
        activate(language_code)
        request.session['django_language'] = language_code
        return True
    return False

def get_current_language(request):
    """Get current language from session or default"""
    return request.session.get('django_language', settings.LANGUAGE_CODE)

# Language mapping for UI display
LANGUAGE_NAMES = {
    'en': 'English',
    'hi': 'हिन्दी',
    'te': 'తెలుగు',
    'kn': 'ಕನ್ನಡ',
    'ta': 'தமிழ்',
    'ml': 'മലയാളം',
    'bn': 'বাংলা',
    'mr': 'मराठी',
    'gu': 'ગુજરાતી',
    'or': 'ଓଡ଼ିଆ',
}
