from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .repositories import (
    UserRepository, TravelOfferRepository, BookingRepository,
    MessageRepository, FavouriteRepository, ReviewRepository,
    CategoryRepository
)
from .models import UserProfile, TravelOffer, Booking


class AuthService:
    """Service for authentication and user management"""
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user with username and password"""
        user = authenticate(username=username, password=password)
        return user
    
    @staticmethod
    def register_user(username, email, password, role='student', **profile_data):
        """Register a new user with profile"""
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return None, "Username already exists"
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return None, "Email already exists"
        
        try:
            user, profile = UserRepository.create_user_with_profile(
                username=username,
                email=email,
                password=password,
                role=role,
                **profile_data
            )
            return user, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_user_role(user):
        """Get user role from profile"""
        profile = UserRepository.get_user_profile(user)
        return profile.role
    
    @staticmethod
    def update_user_profile(user, **profile_data):
        """Update user profile data"""
        profile = UserRepository.get_user_profile(user)
        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.save()
        return profile


class OfferService:
    """Service for travel offer management"""
    
    @staticmethod
    def get_all_offers():
        """Get all approved offers"""
        return TravelOfferRepository.get_all_approved_offers()
    
    @staticmethod
    def get_featured_offers():
        """Get featured offers for homepage"""
        return TravelOfferRepository.get_featured_offers()
    
    @staticmethod
    def get_offer_details(offer_id, user=None):
        """Get detailed offer information with user-specific data"""
        offer = TravelOfferRepository.get_offer_by_id(offer_id)
        if not offer:
            return None
        
        # Add user-specific information
        offer_data = {
            'offer': offer,
            'is_favourite': False,
            'user_booking': None,
            'reviews': ReviewRepository.get_reviews_for_offer(offer),
            'rating_data': ReviewRepository.get_offer_rating(offer)
        }
        
        if user and user.is_authenticated:
            offer_data['is_favourite'] = FavouriteRepository.is_favourite(user, offer)
            # Check if user has booked this offer
            user_bookings = BookingRepository.get_bookings_by_student(user)
            for booking in user_bookings:
                if booking.offer.id == offer.id:
                    offer_data['user_booking'] = booking
                    break
        
        return offer_data
    
    @staticmethod
    def search_offers(query=None, category_id=None, min_price=None, max_price=None, start_date=None, end_date=None):
        """Search offers with various filters"""
        offers = TravelOfferRepository.get_all_approved_offers()
        
        if query:
            offers = TravelOfferRepository.search_offers(query)
        
        if category_id:
            offers = offers.filter(category_id=category_id)
        
        if min_price is not None:
            offers = offers.filter(price__gte=min_price)
        
        if max_price is not None:
            offers = offers.filter(price__lte=max_price)
        
        if start_date:
            offers = offers.filter(start_date__gte=start_date)
        
        if end_date:
            offers = offers.filter(end_date__lte=end_date)
        
        return offers
    
    @staticmethod
    def create_offer(advertiser, offer_data):
        """Create a new travel offer"""
        try:
            offer = TravelOfferRepository.create_offer(advertiser, **offer_data)
            return offer, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_advertiser_offers(advertiser):
        """Get all offers by advertiser"""
        return TravelOfferRepository.get_offers_by_advertiser(advertiser)
    
    @staticmethod
    def update_offer_status(offer_id, status, user):
        """Update offer status (admin/moderator only)"""
        user_role = AuthService.get_user_role(user)
        if user_role not in ['admin', 'moderator']:
            return None, "Insufficient permissions"
        
        offer = TravelOfferRepository.update_offer_status(offer_id, status)
        if not offer:
            return None, "Offer not found"
        
        # Send notification to advertiser
        if status in ['approved', 'rejected']:
            MessageService.send_system_message(
                recipient=offer.advertiser,
                subject=f"Offer {status.title()}",
                body=f"Your offer '{offer.title}' has been {status}."
            )
        
        return offer, None


class BookingService:
    """Service for booking management"""
    
    @staticmethod
    def create_booking(student, offer_id, contact_phone, contact_email, special_requests=''):
        """Create a new booking"""
        offer = TravelOfferRepository.get_offer_by_id(offer_id)
        if not offer:
            return None, "Offer not found"
        
        if not offer.is_available:
            return None, "Offer is not available for booking"
        
        booking, error = BookingRepository.create_booking(
            student=student,
            offer=offer,
            contact_phone=contact_phone,
            contact_email=contact_email,
            special_requests=special_requests
        )
        
        if error:
            return None, error
        
        # Send confirmation messages
        MessageService.send_system_message(
            recipient=student,
            subject="Booking Confirmation",
            body=f"Your booking for '{offer.title}' has been submitted and is pending confirmation."
        )
        
        MessageService.send_system_message(
            recipient=offer.advertiser,
            subject="New Booking",
            body=f"You have a new booking for '{offer.title}' from {student.username}."
        )
        
        return booking, None
    
    @staticmethod
    def get_student_bookings(student):
        """Get all bookings for a student"""
        return BookingRepository.get_bookings_by_student(student)
    
    @staticmethod
    def get_advertiser_bookings(advertiser):
        """Get all bookings for an advertiser's offers"""
        return BookingRepository.get_bookings_by_advertiser(advertiser)
    
    @staticmethod
    def update_booking_status(booking_id, status, user):
        """Update booking status"""
        booking = BookingRepository.get_booking_by_id(booking_id)
        if not booking:
            return None, "Booking not found"
        
        # Check permissions
        user_role = AuthService.get_user_role(user)
        if user != booking.offer.advertiser and user_role not in ['admin', 'moderator']:
            return None, "Insufficient permissions"
        
        updated_booking = BookingRepository.update_booking_status(booking_id, status)
        
        # Send notification to student
        MessageService.send_system_message(
            recipient=booking.student,
            subject="Booking Status Update",
            body=f"Your booking for '{booking.offer.title}' has been {status}."
        )
        
        return updated_booking, None


class MessageService:
    """Service for messaging functionality"""
    
    @staticmethod
    def send_message(sender, recipient_username, subject, body, offer_id=None):
        """Send a message between users"""
        recipient = UserRepository.get_user_by_username(recipient_username)
        if not recipient:
            return None, "Recipient not found"
        
        offer = None
        if offer_id:
            offer = TravelOfferRepository.get_offer_by_id(offer_id)
        
        message = MessageRepository.create_message(
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            offer=offer
        )
        
        return message, None
    
    @staticmethod
    def send_system_message(recipient, subject, body):
        """Send a system message"""
        try:
            # Get or create system user
            system_user, created = User.objects.get_or_create(
                username='system',
                defaults={'email': 'system@studenttravels.com', 'is_staff': True}
            )
            
            return MessageRepository.create_message(
                sender=system_user,
                recipient=recipient,
                subject=subject,
                body=body
            )
        except Exception as e:
            print(f"Error sending system message: {e}")
            return None
    
    @staticmethod
    def get_user_messages(user):
        """Get all messages for a user"""
        return MessageRepository.get_messages_for_user(user)
    
    @staticmethod
    def get_conversation(user1, user2, offer_id=None):
        """Get conversation between two users"""
        offer = None
        if offer_id:
            offer = TravelOfferRepository.get_offer_by_id(offer_id)
        
        return MessageRepository.get_conversation(user1, user2, offer)
    
    @staticmethod
    def mark_message_as_read(message_id, user):
        """Mark a message as read"""
        message = MessageRepository.mark_message_as_read(message_id)
        return message
    
    @staticmethod
    def get_unread_count(user):
        """Get unread message count for user"""
        return MessageRepository.get_unread_messages_count(user)


class FavouriteService:
    """Service for favourite functionality"""
    
    @staticmethod
    def toggle_favourite(student, offer_id):
        """Toggle favourite status for an offer"""
        offer = TravelOfferRepository.get_offer_by_id(offer_id)
        if not offer:
            return None, "Offer not found"
        
        is_favourite = FavouriteRepository.toggle_favourite(student, offer)
        return is_favourite, None
    
    @staticmethod
    def get_user_favourites(user):
        """Get all favourites for a user"""
        return FavouriteRepository.get_user_favourites(user)


class ReviewService:
    """Service for review functionality"""
    
    @staticmethod
    def create_review(booking_id, rating, comment, user):
        """Create a review for a completed booking"""
        booking = BookingRepository.get_booking_by_id(booking_id)
        if not booking:
            return None, "Booking not found"
        
        if booking.student != user:
            return None, "You can only review your own bookings"
        
        if booking.status != 'completed':
            return None, "You can only review completed bookings"
        
        # Check if review already exists
        existing_review = ReviewRepository.get_review_by_booking(booking)
        if existing_review:
            return None, "You have already reviewed this booking"
        
        review = ReviewRepository.create_review(booking, rating, comment)
        return review, None
    
    @staticmethod
    def get_offer_reviews(offer_id):
        """Get all reviews for an offer"""
        offer = TravelOfferRepository.get_offer_by_id(offer_id)
        if not offer:
            return []
        
        return ReviewRepository.get_reviews_for_offer(offer)


class DashboardService:
    """Service for dashboard data"""
    
    @staticmethod
    def get_student_dashboard_data(student):
        """Get dashboard data for student"""
        bookings = BookingRepository.get_bookings_by_student(student)
        favourites = FavouriteRepository.get_user_favourites(student)
        unread_messages = MessageRepository.get_unread_messages_count(student)
        
        return {
            'recent_bookings': bookings[:5],
            'favourites': favourites[:5],
            'unread_messages': unread_messages,
            'total_bookings': bookings.count() if hasattr(bookings, 'count') else len(bookings)
        }
    
    @staticmethod
    def get_advertiser_dashboard_data(advertiser):
        """Get dashboard data for advertiser"""
        offers = TravelOfferRepository.get_offers_by_advertiser(advertiser)
        bookings = BookingRepository.get_bookings_by_advertiser(advertiser)
        unread_messages = MessageRepository.get_unread_messages_count(advertiser)
        
        return {
            'total_offers': offers.count() if hasattr(offers, 'count') else len(offers),
            'recent_bookings': bookings[:5],
            'unread_messages': unread_messages,
            'pending_offers': offers.filter(status='pending').count() if hasattr(offers, 'filter') else 0
        }
    
    @staticmethod
    def get_admin_dashboard_data():
        """Get dashboard data for admin"""
        pending_offers = TravelOfferRepository.get_pending_offers()
        booking_stats = BookingRepository.get_booking_stats()
        
        return {
            'pending_offers': pending_offers.count() if hasattr(pending_offers, 'count') else len(pending_offers),
            'booking_stats': booking_stats,
            'total_users': User.objects.count(),
            'total_offers': TravelOffer.objects.count(),
        }


class CategoryService:
    """Service for category management"""
    
    @staticmethod
    def get_all_categories():
        """Get all categories"""
        return CategoryRepository.get_all_categories()
    
    @staticmethod
    def get_categories_with_counts():
        """Get categories with offer counts"""
        return CategoryRepository.get_categories_with_offer_count()
    
    @staticmethod
    def create_category(name, description=''):
        """Create a new category"""
        try:
            category = CategoryRepository.create_category(name, description)
            return category, None
        except Exception as e:
            return None, str(e)
