from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..services import DashboardService, AuthService, OfferService, BookingService, FavouriteService


@login_required
def student_dashboard_view(request):
    """Student dashboard"""
    user_role = AuthService.get_user_role(request.user)
    if user_role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    dashboard_data = DashboardService.get_student_dashboard_data(request.user)
    
    context = {
        'dashboard_data': dashboard_data,
        'user_role': user_role
    }
    return render(request, 'dashboards/student.html', context)


@login_required
def advertiser_dashboard_view(request):
    """Advertiser dashboard"""
    user_role = AuthService.get_user_role(request.user)
    if user_role != 'advertiser':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    dashboard_data = DashboardService.get_advertiser_dashboard_data(request.user)
    
    # Get recent offers
    my_offers = OfferService.get_advertiser_offers(request.user)[:5]
    recent_bookings = BookingService.get_advertiser_bookings(request.user)[:5]
    
    context = {
        'dashboard_data': dashboard_data,
        'my_offers': my_offers,
        'recent_bookings': recent_bookings,
        'user_role': user_role
    }
    return render(request, 'dashboards/advertiser.html', context)


@login_required
def moderator_dashboard_view(request):
    """Moderator dashboard"""
    user_role = AuthService.get_user_role(request.user)
    if user_role not in ['moderator', 'admin']:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    from ..repositories import TravelOfferRepository
    
    # Get pending offers for review
    pending_offers = TravelOfferRepository.get_pending_offers()
    
    context = {
        'pending_offers': pending_offers,
        'user_role': user_role
    }
    return render(request, 'dashboards/moderator.html', context)


@login_required
def admin_dashboard_view(request):
    """Admin dashboard"""
    user_role = AuthService.get_user_role(request.user)
    if user_role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    dashboard_data = DashboardService.get_admin_dashboard_data()
    
    from ..repositories import TravelOfferRepository, BookingRepository
    from django.contrib.auth.models import User
    
    # Get recent activity
    recent_offers = TravelOfferRepository.get_pending_offers()[:10]
    recent_bookings = BookingRepository.get_booking_stats()
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    context = {
        'dashboard_data': dashboard_data,
        'recent_offers': recent_offers,
        'recent_bookings': recent_bookings,
        'recent_users': recent_users,
        'user_role': user_role
    }
    return render(request, 'dashboards/admin.html', context)


@login_required
def favourites_view(request):
    """User's favourite offers"""
    user_role = AuthService.get_user_role(request.user)
    if user_role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    favourites = FavouriteService.get_user_favourites(request.user)
    
    context = {
        'favourites': favourites
    }
    return render(request, 'dashboards/favourites.html', context)


def dashboard_redirect_view(request):
    """Redirect to appropriate dashboard based on user role"""
    if not request.user.is_authenticated:
        return redirect('home')
    
    user_role = AuthService.get_user_role(request.user)
    
    if user_role == 'student':
        return redirect('student_dashboard')
    elif user_role == 'advertiser':
        return redirect('advertiser_dashboard')
    elif user_role == 'moderator':
        return redirect('moderator_dashboard')
    elif user_role == 'admin':
        return redirect('admin_dashboard')
    else:
        return redirect('home')
