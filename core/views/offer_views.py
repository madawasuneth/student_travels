from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods

from ..services import OfferService, FavouriteService, CategoryService
from ..forms import TravelOfferForm, SearchForm
from ..models import TravelOffer


def offers_list_view(request):
    """List all offers with search and filtering"""
    form = SearchForm(request.GET)
    offers = OfferService.get_all_offers()
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        
        offers = OfferService.search_offers(
            query=query,
            category_id=category.id if category else None,
            min_price=min_price,
            max_price=max_price,
            start_date=start_date,
            end_date=end_date
        )
    
    # Pagination
    paginator = Paginator(offers, 12)  # Show 12 offers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'categories': CategoryService.get_all_categories()
    }
    return render(request, 'offers.html', context)


def offer_detail_view(request, offer_id):
    """Detailed view of a single offer"""
    offer_data = OfferService.get_offer_details(offer_id, request.user)
    if not offer_data:
        messages.error(request, 'Offer not found.')
        return redirect('offers_list')
    
    context = offer_data
    return render(request, 'offer_detail.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_favourite_view(request, offer_id):
    """AJAX endpoint to toggle favourite status"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    is_favourite, error = FavouriteService.toggle_favourite(request.user, offer_id)
    
    if error:
        return JsonResponse({'error': error}, status=400)
    
    return JsonResponse({
        'is_favourite': is_favourite,
        'message': 'Added to favourites' if is_favourite else 'Removed from favourites'
    })


@login_required
def create_offer_view(request):
    """Create a new travel offer (advertisers only)"""
    from ..services import AuthService
    
    user_role = AuthService.get_user_role(request.user)
    if user_role != 'advertiser':
        messages.error(request, 'Only advertisers can create offers.')
        return redirect('home')
    
    if request.method == 'POST':
        form = TravelOfferForm(request.POST, request.FILES)
        if form.is_valid():
            offer, error = OfferService.create_offer(request.user, form.cleaned_data)
            if offer:
                messages.success(request, 'Offer created successfully! It will be reviewed before publication.')
                return redirect('advertiser_dashboard')
            else:
                messages.error(request, error)
    else:
        form = TravelOfferForm()
    
    return render(request, 'offers/create.html', {'form': form})


@login_required
def edit_offer_view(request, offer_id):
    """Edit an existing offer (advertiser only, own offers)"""
    from ..services import AuthService
    from ..repositories import TravelOfferRepository
    
    offer = get_object_or_404(TravelOffer, id=offer_id)
    
    # Check permissions
    if offer.advertiser != request.user:
        messages.error(request, 'You can only edit your own offers.')
        return redirect('advertiser_dashboard')
    
    if request.method == 'POST':
        form = TravelOfferForm(request.POST, request.FILES, instance=offer)
        if form.is_valid():
            updated_offer = form.save()
            # Reset status to pending if offer was rejected
            if updated_offer.status == 'rejected':
                updated_offer.status = 'pending'
                updated_offer.save()
            messages.success(request, 'Offer updated successfully!')
            return redirect('advertiser_dashboard')
    else:
        form = TravelOfferForm(instance=offer)
    
    return render(request, 'offers/edit.html', {'form': form, 'offer': offer})


@login_required
def my_offers_view(request):
    """List advertiser's own offers"""
    from ..services import AuthService
    
    user_role = AuthService.get_user_role(request.user)
    if user_role != 'advertiser':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    offers = OfferService.get_advertiser_offers(request.user)
    
    context = {
        'offers': offers,
        'user_role': user_role
    }
    return render(request, 'offers/my_offers.html', context)


@login_required
def offers_by_category_view(request, category_id):
    """List offers by category"""
    from ..repositories import CategoryRepository, TravelOfferRepository
    
    category = get_object_or_404(CategoryRepository.get_category_by_id(category_id))
    if not category:
        messages.error(request, 'Category not found.')
        return redirect('offers_list')
    
    offers = TravelOfferRepository.get_offers_by_category(category_id)
    
    # Pagination
    paginator = Paginator(offers, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category': category,
        'categories': CategoryService.get_all_categories()
    }
    return render(request, 'offers/by_category.html', context)
