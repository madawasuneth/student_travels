from django.contrib import admin
from .models import UserProfile, Category, TravelOffer, Booking, Message, Favourite, Review


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)


@admin.register(TravelOffer)
class TravelOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'advertiser', 'category', 'price', 'status', 'featured', 'available_spots', 'start_date', 'created_at')
    list_filter = ('status', 'category', 'featured', 'created_at')
    search_fields = ('title', 'destination', 'advertiser__username')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status', 'featured')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'advertiser')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price', 'discount_percentage')
        }),
        ('Details', {
            'fields': ('destination', 'start_date', 'end_date', 'available_spots', 'image')
        }),
        ('Status', {
            'fields': ('status', 'featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'offer', 'status', 'price_paid', 'booking_date')
    list_filter = ('status', 'booking_date')
    search_fields = ('student__username', 'offer__title', 'contact_email')
    readonly_fields = ('booking_date', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('student', 'offer', 'status', 'price_paid')
        }),
        ('Contact Details', {
            'fields': ('contact_phone', 'contact_email', 'special_requests')
        }),
        ('Timestamps', {
            'fields': ('booking_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'subject')
    readonly_fields = ('created_at',)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('student', 'offer', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('student__username', 'offer__title')
    readonly_fields = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('booking__student__username', 'booking__offer__title')
    readonly_fields = ('created_at',)
