from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from ..services import AuthService
from ..forms import CustomUserCreationForm


def home_view(request):
    """Homepage view with featured offers"""
    from ..services import OfferService, CategoryService
    from django.templatetags.static import static
    
    # Attach a reasonable static image per offer (fallback to a default)
    featured = list(OfferService.get_featured_offers())
    # simple keyword -> static image mapping
    img_map = {
        'gold coast': 'images/gold-coast-sunny.jpg',
        'gold-coast': 'images/gold-coast-sunny.jpg',
        'uluru': 'images/uluru.jpg',
        'byron': 'images/byron-bay.jpg',
        'byron bay': 'images/byron-bay.jpg',
        'cairns': 'images/cairns.jpg',
        'sunshine': 'images/sunshine-coast.jpg',
        'broome': 'images/broome.jpg',
        'whitsunday': 'images/whitsundays.jpg',
        'whitsundays': 'images/whitsundays.jpg',
        'margaret': 'images/margaret-river.jpg',
        'uluru': 'images/uluru.jpg'
    }

    for offer in featured:
        dest = (offer.destination or '') .lower()
        chosen = None
        for k, v in img_map.items():
            if k in dest:
                chosen = v
                break
        if not chosen:
            # try title match
            t = (offer.title or '').lower()
            for k, v in img_map.items():
                if k in t:
                    chosen = v
                    break
        offer.static_image = static(chosen or 'images/gold-coast-sunny.jpg')

    context = {
        'featured_offers': featured,
        'categories': CategoryService.get_categories_with_counts()
    }
    return render(request, 'home.html', context)


@require_http_methods(["POST"])
def ajax_login(request):
    """AJAX login endpoint"""
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'ok': False, 'error': 'Username and password are required'})
        
        user = AuthService.authenticate_user(username, password)
        if user:
            login(request, user)
            return JsonResponse({'ok': True, 'message': 'Login successful'})
        else:
            return JsonResponse({'ok': False, 'error': 'Invalid username or password'})
    
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@require_http_methods(["POST"])
def ajax_register(request):
    """AJAX registration endpoint"""
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        
        form = CustomUserCreationForm(data)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({'ok': True, 'message': 'Registration successful'})
        else:
            # Get first error message
            error_message = next(iter(form.errors.values()))[0] if form.errors else 'Registration failed'
            return JsonResponse({'ok': False, 'error': error_message})
    
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


def login_view(request):
    """Traditional login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = AuthService.authenticate_user(username, password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'auth/login.html')


def register_view(request):
    """Traditional registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile_view(request):
    """User profile view"""
    from ..forms import UserProfileForm
    from ..models import UserProfile

    # Ensure the related UserProfile exists to avoid RelatedObjectDoesNotExist
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Keep role lookup (used by some templates) but rely on user_profile for updates
    profile_role = AuthService.get_user_role(request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'auth/profile.html', {'form': form, 'profile': user_profile, 'role': profile_role})
