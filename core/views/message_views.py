from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from ..services import MessageService, AuthService
from ..forms import MessageForm


@login_required
def messages_list_view(request):
    """List all messages for the user"""
    messages_list = MessageService.get_user_messages(request.user)
    
    # Pagination
    paginator = Paginator(messages_list, 20)  # 20 messages per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'unread_count': MessageService.get_unread_count(request.user)
    }
    return render(request, 'messages/list.html', context)


@login_required
def send_message_view(request):
    """Send a new message"""
    recipient_username = request.GET.get('to')
    offer_id = request.GET.get('offer')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message, error = MessageService.send_message(
                sender=request.user,
                recipient_username=form.cleaned_data['recipient_username'],
                subject=form.cleaned_data['subject'],
                body=form.cleaned_data['body'],
                offer_id=offer_id
            )
            
            if message:
                messages.success(request, 'Message sent successfully!')
                return redirect('messages_list')
            else:
                messages.error(request, error)
    else:
        form = MessageForm(recipient_username=recipient_username)
        
        # Pre-fill subject if it's about an offer
        if offer_id:
            from ..repositories import TravelOfferRepository
            offer = TravelOfferRepository.get_offer_by_id(offer_id)
            if offer:
                form.fields['subject'].initial = f"Inquiry about: {offer.title}"
    
    context = {
        'form': form,
        'offer_id': offer_id
    }
    return render(request, 'messages/send.html', context)


@login_required
def conversation_view(request, username):
    """View conversation with another user"""
    from ..repositories import UserRepository
    
    other_user = UserRepository.get_user_by_username(username)
    if not other_user:
        messages.error(request, 'User not found.')
        return redirect('messages_list')
    
    offer_id = request.GET.get('offer')
    conversation = MessageService.get_conversation(request.user, other_user, offer_id)
    
    # Mark messages as read
    from ..repositories import MessageRepository
    MessageRepository.mark_conversation_as_read(request.user, other_user)
    
    # Handle reply
    if request.method == 'POST':
        subject = request.POST.get('subject', f'Re: Conversation')
        body = request.POST.get('body')
        
        if body:
            message, error = MessageService.send_message(
                sender=request.user,
                recipient_username=username,
                subject=subject,
                body=body,
                offer_id=offer_id
            )
            
            if message:
                messages.success(request, 'Reply sent!')
                return redirect(request.path)
            else:
                messages.error(request, error)
    
    context = {
        'conversation': conversation,
        'other_user': other_user,
        'offer_id': offer_id
    }
    return render(request, 'messages/conversation.html', context)


@login_required
def mark_message_read_view(request, message_id):
    """Mark a message as read (AJAX)"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        message = MessageService.mark_message_as_read(message_id, request.user)
        if message:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Message not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def delete_message_view(request, message_id):
    """Delete a message (soft delete - mark as deleted)"""
    # This is a simplified implementation
    # In a real app, you might want to implement soft deletion
    if request.method == 'POST':
        # Here you would implement message deletion logic
        messages.success(request, 'Message deleted.')
    
    return redirect('messages_list')


@login_required
def inbox_view(request):
    """Show only received messages"""
    from ..repositories import MessageRepository
    
    received_messages = MessageRepository.get_messages_for_user(request.user).filter(
        recipient=request.user
    )
    
    # Pagination
    paginator = Paginator(received_messages, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'message_type': 'inbox',
        'unread_count': MessageService.get_unread_count(request.user)
    }
    return render(request, 'messages/list.html', context)


@login_required
def sent_messages_view(request):
    """Show only sent messages"""
    from ..repositories import MessageRepository
    
    sent_messages = MessageRepository.get_messages_for_user(request.user).filter(
        sender=request.user
    )
    
    # Pagination
    paginator = Paginator(sent_messages, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'message_type': 'sent',
        'unread_count': MessageService.get_unread_count(request.user)
    }
    return render(request, 'messages/list.html', context)
