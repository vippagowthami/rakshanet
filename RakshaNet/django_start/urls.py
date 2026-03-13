"""django_start URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from rest_framework.authtoken import views as drf_auth_views
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer, BrowsableAPIRenderer
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language
from users.views import ProfileView

# Non-localized URL patterns
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/', set_language, name='set_language'),
]

# Localized URL patterns
localized_patterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name="register"),
    path('contact/', user_views.contact, name="contact"),
    path('profile/edit/', user_views.profile, name='edit-profile'),
    path('profile/', user_views.profile, name="profile"),
    path('profile/<pk>/', ProfileView.as_view(), name='profile-view'),
    path('set-language/', user_views.set_language, name='set-language'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name="login"),
    path('logout/', user_views.user_logout, name="logout"),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), 
         name="password-reset"),
    path('password-reset-done/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name="password_reset_done"),
    path('password-reset-confirm/done/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
         name="password_reset_confirm"),
    path('password-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name="password_reset_complete"),
    path('', include('raksha.urls')),  # Root path points to raksha home
    path('raksha/', include('raksha.urls')),
    path('api-token-auth/', drf_auth_views.obtain_auth_token),
    path('api/schema/', get_schema_view(title='RakshaNet API', description='API schema for RakshaNet'), name='openapi-schema'),
]

urlpatterns += i18n_patterns(*localized_patterns)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)