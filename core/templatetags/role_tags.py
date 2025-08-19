from django import template
from django.contrib.auth.models import User
from ..services import AuthService, MessageService, FavouriteService

register = template.Library()


@register.simple_tag
def user_role(user):
    """Get user role"""
    if user.is_authenticated:
        return AuthService.get_user_role(user)
    return None


@register.simple_tag
def unread_message_count(user):
    """Get unread message count for user"""
    if user.is_authenticated:
        return MessageService.get_unread_count(user)
    return 0


@register.simple_tag
def is_favourite(user, offer):
    """Check if offer is in user's favourites"""
    if user.is_authenticated:
        return FavouriteService.get_user_favourites(user).filter(offer=offer).exists()
    return False


@register.filter
def has_role(user, role):
    """Check if user has specific role"""
    if user.is_authenticated:
        return AuthService.get_user_role(user) == role
    return False


@register.filter
def has_any_role(user, roles):
    """Check if user has any of the specified roles"""
    if user.is_authenticated:
        user_role = AuthService.get_user_role(user)
        role_list = roles.split(',')
        return user_role in [role.strip() for role in role_list]
    return False


@register.inclusion_tag('components/user_menu.html', takes_context=True)
def user_menu(context):
    """Render user menu based on role"""
    user = context['user']
    if user.is_authenticated:
        role = AuthService.get_user_role(user)
        unread_count = MessageService.get_unread_count(user)
        return {
            'user': user,
            'role': role,
            'unread_count': unread_count
        }
    return {'user': user}


@register.inclusion_tag('components/offer_card.html', takes_context=True)
def offer_card(context, offer, show_actions=True):
    """Render offer card with user-specific actions"""
    user = context['user']
    is_fav = False
    user_booking = None
    
    if user.is_authenticated:
        is_fav = FavouriteService.get_user_favourites(user).filter(offer=offer).exists()
        # Check if user has booked this offer
        from ..repositories import BookingRepository
        bookings = BookingRepository.get_bookings_by_student(user)
        for booking in bookings:
            if booking.offer.id == offer.id:
                user_booking = booking
                break
    
    return {
        'offer': offer,
        'is_favourite': is_fav,
        'user_booking': user_booking,
        'show_actions': show_actions,
        'user': user
    }


@register.filter
def multiply(value, arg):
    """Multiply filter for template calculations"""
    return value * arg


@register.filter
def currency(value):
    """Format value as currency"""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return value


@register.filter
def stars(rating):
    """Convert rating to star representation"""
    try:
        rating = int(rating)
        full_stars = '★' * rating
        empty_stars = '☆' * (5 - rating)
        return full_stars + empty_stars
    except (ValueError, TypeError):
        return '☆☆☆☆☆'


@register.simple_tag
def dashboard_url(user):
    """Get appropriate dashboard URL for user"""
    if not user.is_authenticated:
        return '/'
    
    role = AuthService.get_user_role(user)
    role_urls = {
        'student': 'student_dashboard',
        'advertiser': 'advertiser_dashboard',
        'moderator': 'moderator_dashboard',
        'admin': 'admin_dashboard'
    }
    return role_urls.get(role, 'home')


@register.filter
def bootstrap_status_class(status):
    """Convert status to Bootstrap CSS class"""
    status_classes = {
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'confirmed': 'success',
        'cancelled': 'secondary',
        'completed': 'info'
    }
    return status_classes.get(status, 'secondary')


@register.filter
def truncate_chars(value, length):
    """Truncate string to specified length"""
    if len(value) > length:
        return value[:length] + '...'
    return value
