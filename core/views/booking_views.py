from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from ..services import BookingService, AuthService
from ..forms import BookingForm, BookingStatusForm
from ..models import TravelOffer, Booking


@login_required
def create_booking_view(request, offer_id):
    """Create a new booking for a travel offer"""
    offer = get_object_or_404(TravelOffer, id=offer_id)
    
    if not offer.is_available:
        messages.error(request, 'This offer is not available for booking.')
        return redirect('offer_detail', offer_id=offer_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking, error = BookingService.create_booking(
                student=request.user,
                offer_id=offer_id,
                contact_phone=form.cleaned_data['contact_phone'],
                contact_email=form.cleaned_data['contact_email'],
                special_requests=form.cleaned_data['special_requests']
            )
            
            if booking:
                messages.success(request, 'Booking submitted successfully! You will receive a confirmation soon.')
                return redirect('student_dashboard')
            else:
                messages.error(request, error)
    else:
        form = BookingForm(user=request.user)
    
    context = {
        'form': form,
        'offer': offer
    }
    return render(request, 'bookings/create.html', context)


@login_required
def booking_detail_view(request, booking_id):
    """View booking details"""
    from ..repositories import BookingRepository
    
    booking = BookingRepository.get_booking_by_id(booking_id)
    if not booking:
        messages.error(request, 'Booking not found.')
        return redirect('student_dashboard')
    
    # Check permissions
    user_role = AuthService.get_user_role(request.user)
    if (booking.student != request.user and 
        booking.offer.advertiser != request.user and 
        user_role not in ['admin', 'moderator']):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    context = {
        'booking': booking,
        'user_role': user_role
    }
    return render(request, 'bookings/detail.html', context)


@login_required
def update_booking_status_view(request, booking_id):
    """Update booking status (advertiser/admin only)"""
    if request.method == 'POST':
        form = BookingStatusForm(request.POST)
        if form.is_valid():
            booking, error = BookingService.update_booking_status(
                booking_id=booking_id,
                status=form.cleaned_data['status'],
                user=request.user
            )
            
            if booking:
                messages.success(request, f'Booking status updated to {form.cleaned_data["status"]}.')
            else:
                messages.error(request, error)
    
    return redirect('booking_detail', booking_id=booking_id)


@login_required
def my_bookings_view(request):
    """List user's bookings (students)"""
    user_role = AuthService.get_user_role(request.user)
    if user_role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    bookings = BookingService.get_student_bookings(request.user)
    
    context = {
        'bookings': bookings
    }
    return render(request, 'bookings/my_bookings.html', context)


@login_required
def received_bookings_view(request):
    """List bookings for advertiser's offers"""
    user_role = AuthService.get_user_role(request.user)
    if user_role != 'advertiser':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    bookings = BookingService.get_advertiser_bookings(request.user)
    
    context = {
        'bookings': bookings
    }
    return render(request, 'bookings/received_bookings.html', context)


@login_required
def cancel_booking_view(request, booking_id):
    """Cancel a booking (student only, own bookings)"""
    from ..repositories import BookingRepository
    
    booking = BookingRepository.get_booking_by_id(booking_id)
    if not booking:
        messages.error(request, 'Booking not found.')
        return redirect('my_bookings')
    
    if booking.student != request.user:
        messages.error(request, 'You can only cancel your own bookings.')
        return redirect('my_bookings')
    
    if booking.status in ['cancelled', 'completed']:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        booking, error = BookingService.update_booking_status(
            booking_id=booking_id,
            status='cancelled',
            user=request.user
        )
        
        if booking:
            messages.success(request, 'Booking cancelled successfully.')
        else:
            messages.error(request, error)
    
    return redirect('my_bookings')
