from django.urls import path
from .views import auth_views, offer_views, booking_views, message_views, dashboard_views

urlpatterns = [
    # Home
    path('', auth_views.home_view, name='home'),
    
    # Authentication
    path('login/', auth_views.login_view, name='login'),
    path('register/', auth_views.register_view, name='register'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('profile/', auth_views.profile_view, name='profile'),
    
    # AJAX Authentication
    path('auth/ajax/login/', auth_views.ajax_login, name='ajax_login'),
    path('auth/ajax/register/', auth_views.ajax_register, name='ajax_register'),
    
    # Offers
    path('offers/', offer_views.offers_list_view, name='offers_list'),
    path('offers/<int:offer_id>/', offer_views.offer_detail_view, name='offer_detail'),
    path('offers/create/', offer_views.create_offer_view, name='create_offer'),
    path('offers/<int:offer_id>/edit/', offer_views.edit_offer_view, name='edit_offer'),
    path('offers/my-offers/', offer_views.my_offers_view, name='my_offers'),
    path('offers/category/<int:category_id>/', offer_views.offers_by_category_view, name='offers_by_category'),
    
    # Favourites
    path('favourites/<int:offer_id>/toggle/', offer_views.toggle_favourite_view, name='toggle_favourite'),
    path('favourites/', dashboard_views.favourites_view, name='favourites'),
    
    # Bookings
    path('bookings/create/<int:offer_id>/', booking_views.create_booking_view, name='create_booking'),
    path('bookings/<int:booking_id>/', booking_views.booking_detail_view, name='booking_detail'),
    path('bookings/<int:booking_id>/update-status/', booking_views.update_booking_status_view, name='update_booking_status'),
    path('bookings/<int:booking_id>/cancel/', booking_views.cancel_booking_view, name='cancel_booking'),
    path('bookings/my-bookings/', booking_views.my_bookings_view, name='my_bookings'),
    path('bookings/received/', booking_views.received_bookings_view, name='received_bookings'),
    
    # Messages
    path('messages/', message_views.messages_list_view, name='messages_list'),
    path('messages/send/', message_views.send_message_view, name='send_message'),
    path('messages/conversation/<str:username>/', message_views.conversation_view, name='conversation'),
    path('messages/<int:message_id>/mark-read/', message_views.mark_message_read_view, name='mark_message_read'),
    path('messages/<int:message_id>/delete/', message_views.delete_message_view, name='delete_message'),
    path('messages/inbox/', message_views.inbox_view, name='inbox'),
    path('messages/sent/', message_views.sent_messages_view, name='sent_messages'),
    
    # Dashboards
    path('dashboard/', dashboard_views.dashboard_redirect_view, name='dashboard'),
    path('dashboard/student/', dashboard_views.student_dashboard_view, name='student_dashboard'),
    path('dashboard/advertiser/', dashboard_views.advertiser_dashboard_view, name='advertiser_dashboard'),
    path('dashboard/moderator/', dashboard_views.moderator_dashboard_view, name='moderator_dashboard'),
    path('dashboard/admin/', dashboard_views.admin_dashboard_view, name='admin_dashboard'),
]
