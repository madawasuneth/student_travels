from django.db.models import Q, Count, Avg
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    UserProfile, TravelOffer, Booking, Message, 
    Favourite, Review, Category
)


class UserRepository:
    """Repository for user-related data operations"""
    
    @staticmethod
    def get_user_by_username(username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_profile(user):
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile
    
    @staticmethod
    def create_user_with_profile(username, email, password, role='student', **profile_data):
        user = User.objects.create_user(username=username, email=email, password=password)
        profile = UserProfile.objects.create(user=user, role=role, **profile_data)
        return user, profile
    
    @staticmethod
    def get_users_by_role(role):
        return User.objects.filter(userprofile__role=role)


class TravelOfferRepository:
    """Repository for travel offer data operations"""
    
    @staticmethod
    def get_all_approved_offers():
        return TravelOffer.objects.filter(status='approved').select_related('advertiser', 'category')
    
    @staticmethod
    def get_featured_offers():
        return TravelOffer.objects.filter(
            status='approved', 
            featured=True
        ).select_related('advertiser', 'category')[:6]
    
    @staticmethod
    def get_offers_by_category(category_id):
        return TravelOffer.objects.filter(
            category_id=category_id, 
            status='approved'
        ).select_related('advertiser', 'category')
    
    @staticmethod
    def get_offers_by_advertiser(advertiser):
        return TravelOffer.objects.filter(advertiser=advertiser).select_related('category')
    
    @staticmethod
    def get_offer_by_id(offer_id):
        try:
            return TravelOffer.objects.select_related('advertiser', 'category').get(id=offer_id)
        except TravelOffer.DoesNotExist:
            return None
    
    @staticmethod
    def search_offers(query):
        return TravelOffer.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) | 
            Q(destination__icontains=query),
            status='approved'
        ).select_related('advertiser', 'category')
    
    @staticmethod
    def get_offers_by_price_range(min_price, max_price):
        return TravelOffer.objects.filter(
            price__gte=min_price,
            price__lte=max_price,
            status='approved'
        ).select_related('advertiser', 'category')
    
    @staticmethod
    def get_offers_by_date_range(start_date, end_date):
        return TravelOffer.objects.filter(
            start_date__gte=start_date,
            end_date__lte=end_date,
            status='approved'
        ).select_related('advertiser', 'category')
    
    @staticmethod
    def get_pending_offers():
        return TravelOffer.objects.filter(status='pending').select_related('advertiser', 'category')
    
    @staticmethod
    def create_offer(advertiser, **offer_data):
        return TravelOffer.objects.create(advertiser=advertiser, **offer_data)
    
    @staticmethod
    def update_offer_status(offer_id, status):
        try:
            offer = TravelOffer.objects.get(id=offer_id)
            offer.status = status
            offer.save()
            return offer
        except TravelOffer.DoesNotExist:
            return None


class BookingRepository:
    """Repository for booking data operations"""
    
    @staticmethod
    def get_bookings_by_student(student):
        return Booking.objects.filter(student=student).select_related('offer', 'offer__advertiser')
    
    @staticmethod
    def get_bookings_by_advertiser(advertiser):
        return Booking.objects.filter(
            offer__advertiser=advertiser
        ).select_related('student', 'offer')
    
    @staticmethod
    def get_booking_by_id(booking_id):
        try:
            return Booking.objects.select_related('student', 'offer', 'offer__advertiser').get(id=booking_id)
        except Booking.DoesNotExist:
            return None
    
    @staticmethod
    def create_booking(student, offer, contact_phone, contact_email, special_requests=''):
        # Check if user already booked this offer
        existing_booking = Booking.objects.filter(student=student, offer=offer).first()
        if existing_booking:
            return None, "You have already booked this offer"
        
        # Check availability
        if offer.available_spots <= 0:
            return None, "No spots available"
        
        # Create booking
        booking = Booking.objects.create(
            student=student,
            offer=offer,
            contact_phone=contact_phone,
            contact_email=contact_email,
            special_requests=special_requests,
            price_paid=offer.price
        )
        
        # Decrease available spots
        offer.available_spots -= 1
        offer.save()
        
        return booking, None
    
    @staticmethod
    def update_booking_status(booking_id, status):
        try:
            booking = Booking.objects.get(id=booking_id)
            old_status = booking.status
            booking.status = status
            booking.save()
            
            # If cancelling, return spot to offer
            if status == 'cancelled' and old_status != 'cancelled':
                booking.offer.available_spots += 1
                booking.offer.save()
            
            return booking
        except Booking.DoesNotExist:
            return None
    
    @staticmethod
    def get_booking_stats():
        """Get booking statistics for admin dashboard"""
        total_bookings = Booking.objects.count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()
        
        return {
            'total': total_bookings,
            'pending': pending_bookings,
            'confirmed': confirmed_bookings
        }


class MessageRepository:
    """Repository for message data operations"""
    
    @staticmethod
    def get_messages_for_user(user):
        return Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related('sender', 'recipient', 'offer').order_by('-created_at')
    
    @staticmethod
    def get_unread_messages_count(user):
        return Message.objects.filter(recipient=user, read=False).count()
    
    @staticmethod
    def get_conversation(user1, user2, offer=None):
        messages = Message.objects.filter(
            Q(sender=user1, recipient=user2) | Q(sender=user2, recipient=user1)
        )
        if offer:
            messages = messages.filter(offer=offer)
        return messages.select_related('sender', 'recipient', 'offer').order_by('created_at')
    
    @staticmethod
    def create_message(sender, recipient, subject, body, offer=None):
        return Message.objects.create(
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            offer=offer
        )
    
    @staticmethod
    def mark_message_as_read(message_id):
        try:
            message = Message.objects.get(id=message_id)
            message.read = True
            message.save()
            return message
        except Message.DoesNotExist:
            return None
    
    @staticmethod
    def mark_conversation_as_read(user, other_user):
        Message.objects.filter(sender=other_user, recipient=user, read=False).update(read=True)


class FavouriteRepository:
    """Repository for favourite data operations"""
    
    @staticmethod
    def get_user_favourites(user):
        return Favourite.objects.filter(student=user).select_related('offer', 'offer__advertiser')
    
    @staticmethod
    def add_favourite(student, offer):
        favourite, created = Favourite.objects.get_or_create(student=student, offer=offer)
        return favourite, created
    
    @staticmethod
    def remove_favourite(student, offer):
        try:
            favourite = Favourite.objects.get(student=student, offer=offer)
            favourite.delete()
            return True
        except Favourite.DoesNotExist:
            return False
    
    @staticmethod
    def is_favourite(student, offer):
        return Favourite.objects.filter(student=student, offer=offer).exists()
    
    @staticmethod
    def toggle_favourite(student, offer):
        favourite = Favourite.objects.filter(student=student, offer=offer).first()
        if favourite:
            favourite.delete()
            return False  # Removed from favourites
        else:
            Favourite.objects.create(student=student, offer=offer)
            return True  # Added to favourites


class ReviewRepository:
    """Repository for review data operations"""
    
    @staticmethod
    def get_reviews_for_offer(offer):
        return Review.objects.filter(booking__offer=offer).select_related('booking__student')
    
    @staticmethod
    def get_review_by_booking(booking):
        try:
            return Review.objects.get(booking=booking)
        except Review.DoesNotExist:
            return None
    
    @staticmethod
    def create_review(booking, rating, comment=''):
        return Review.objects.create(booking=booking, rating=rating, comment=comment)
    
    @staticmethod
    def get_offer_rating(offer):
        """Get average rating for an offer"""
        result = Review.objects.filter(booking__offer=offer).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        return result


class CategoryRepository:
    """Repository for category data operations"""
    
    @staticmethod
    def get_all_categories():
        return Category.objects.all().order_by('name')
    
    @staticmethod
    def get_category_by_id(category_id):
        try:
            return Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return None
    
    @staticmethod
    def create_category(name, description=''):
        return Category.objects.create(name=name, description=description)
    
    @staticmethod
    def get_categories_with_offer_count():
        """Get categories with their offer counts"""
        return Category.objects.annotate(
            offer_count=Count('traveloffer', filter=Q(traveloffer__status='approved'))
        ).order_by('name')
