from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Contact
from django.views.generic import (DetailView)
from django.utils.translation import activate
from django.http import JsonResponse
from .language_utils import set_user_language, LANGUAGE_NAMES

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            
            # Create or update profile with selected role
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = int(form.cleaned_data.get("role"))
            # Set ngo flag for backward compatibility
            profile.ngo = (profile.role == 1)  # True if Admin/NGO (role=1)
            profile.save()
            
            role_name = dict(form.fields['role'].choices).get(profile.role, 'User')
            messages.success(request, f'Your account has been created as {role_name}! Please log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance = request.user)
        p_form = ProfileUpdateForm(request.POST, 
                                   request.FILES, 
                                   instance = request.user.profile
                                  )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('edit-profile')
        messages.error(request, 'Unable to update profile. Please check the form and try again.')
    else:
        u_form = UserUpdateForm(instance = request.user)
        p_form = ProfileUpdateForm(instance = request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'users/edit_profile.html', context)

class ProfileView(DetailView):
    model = Profile
    template_name = 'users/profile_view.html'

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        desc = request.POST.get('desc', '').strip()

        if name and email and desc:
            contact = Contact(name=name, email=email, phone=phone, desc=desc)
            contact.save()
            messages.success(request, 'Your support request has been submitted successfully.')
        else:
            messages.error(request, 'Please fill in name, email, and message.')
    return render(request, 'users/contact_support.html')

def set_language(request):
    """View to handle language switching"""
    if request.method == 'POST':
        language_code = request.POST.get('language')
        if set_user_language(request, language_code):
            next_url = request.POST.get('next', '/')
            return redirect(next_url)
    
    # Return available languages for AJAX requests
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'languages': [{'code': code, 'name': name} for code, name in LANGUAGE_NAMES.items()]
        })
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

def user_logout(request):
    """Custom logout view that handles both GET and POST requests"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('landing')