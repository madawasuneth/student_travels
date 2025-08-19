from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from .services import AuthService


def role_required(allowed_roles):
    """
    Decorator that checks if user has one of the allowed roles
    Usage: @role_required(['admin', 'moderator'])
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            
            user_role = AuthService.get_user_role(request.user)
            if user_role not in allowed_roles:
                raise PermissionDenied("You don't have permission to access this page.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def is_student(user):
    """Check if user is a student"""
    if not user.is_authenticated:
        return False
    return AuthService.get_user_role(user) == 'student'


def is_advertiser(user):
    """Check if user is an advertiser"""
    if not user.is_authenticated:
        return False
    return AuthService.get_user_role(user) == 'advertiser'


def is_moderator(user):
    """Check if user is a moderator or admin"""
    if not user.is_authenticated:
        return False
    role = AuthService.get_user_role(user)
    return role in ['moderator', 'admin']


def is_admin(user):
    """Check if user is an admin"""
    if not user.is_authenticated:
        return False
    return AuthService.get_user_role(user) == 'admin'


def can_edit_offer(user, offer):
    """Check if user can edit the given offer"""
    if not user.is_authenticated:
        return False
    
    user_role = AuthService.get_user_role(user)
    
    # Advertisers can edit their own offers
    if user_role == 'advertiser' and offer.advertiser == user:
        return True
    
    # Admins and moderators can edit any offer
    if user_role in ['admin', 'moderator']:
        return True
    
    return False


def can_view_booking(user, booking):
    """Check if user can view the given booking"""
    if not user.is_authenticated:
        return False
    
    user_role = AuthService.get_user_role(user)
    
    # Students can view their own bookings
    if user_role == 'student' and booking.student == user:
        return True
    
    # Advertisers can view bookings for their offers
    if user_role == 'advertiser' and booking.offer.advertiser == user:
        return True
    
    # Admins and moderators can view any booking
    if user_role in ['admin', 'moderator']:
        return True
    
    return False


def can_update_booking_status(user, booking):
    """Check if user can update booking status"""
    if not user.is_authenticated:
        return False
    
    user_role = AuthService.get_user_role(user)
    
    # Advertisers can update status of bookings for their offers
    if user_role == 'advertiser' and booking.offer.advertiser == user:
        return True
    
    # Admins and moderators can update any booking status
    if user_role in ['admin', 'moderator']:
        return True
    
    return False


# Decorators using user_passes_test
student_required = user_passes_test(is_student)
advertiser_required = user_passes_test(is_advertiser)
moderator_required = user_passes_test(is_moderator)
admin_required = user_passes_test(is_admin)
