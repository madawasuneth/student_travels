from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import UserProfile, TravelOffer, Booking, Message, Review, Category


class CustomUserCreationForm(UserCreationForm):
    """Extended user registration form"""
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, initial='student')
    phone = forms.CharField(max_length=20, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Set placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email Address'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['phone'].widget.attrs['placeholder'] = 'Phone Number'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                phone=self.cleaned_data.get('phone', ''),
                date_of_birth=self.cleaned_data.get('date_of_birth')
            )
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'date_of_birth', 'profile_picture']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'})
        }


class TravelOfferForm(forms.ModelForm):
    """Form for creating/editing travel offers"""
    
    class Meta:
        model = TravelOffer
        fields = [
            'title', 'description', 'category', 'price', 'original_price', 
            'discount_percentage', 'available_spots', 'destination', 
            'start_date', 'end_date', 'image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Offer Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your travel offer...'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Price'}),
            'original_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Original Price (optional)'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'placeholder': 'Discount %'}),
            'available_spots': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Available Spots'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make original_price and discount_percentage not required
        self.fields['original_price'].required = False
        self.fields['discount_percentage'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        original_price = cleaned_data.get('original_price')
        discount_percentage = cleaned_data.get('discount_percentage')
        
        # Validate date range
        if start_date and end_date:
            if start_date >= end_date:
                raise ValidationError("End date must be after start date.")
        
        # Validate discount logic
        if discount_percentage and not original_price:
            raise ValidationError("Original price is required when discount percentage is provided.")
        
        if original_price and discount_percentage:
            if discount_percentage < 0 or discount_percentage > 100:
                raise ValidationError("Discount percentage must be between 0 and 100.")
        
        return cleaned_data


class BookingForm(forms.ModelForm):
    """Form for creating bookings"""
    
    class Meta:
        model = Booking
        fields = ['contact_phone', 'contact_email', 'special_requests']
        widgets = {
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special requests or notes...'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill with user data if available
        if user:
            self.fields['contact_email'].initial = user.email
            profile = getattr(user, 'userprofile', None)
            if profile and profile.phone:
                self.fields['contact_phone'].initial = profile.phone


class MessageForm(forms.ModelForm):
    """Form for sending messages"""
    recipient_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recipient Username'})
    )
    
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Message content...'})
        }
    
    def __init__(self, *args, **kwargs):
        recipient_username = kwargs.pop('recipient_username', None)
        super().__init__(*args, **kwargs)
        
        if recipient_username:
            self.fields['recipient_username'].initial = recipient_username
            self.fields['recipient_username'].widget.attrs['readonly'] = True


class ReviewForm(forms.ModelForm):
    """Form for creating reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f"{i} Star{'s' if i != 1 else ''}") for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your experience...'})
        }


class SearchForm(forms.Form):
    """Form for searching offers"""
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search destinations, titles...'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Price', 'step': '0.01'})
    )
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Price', 'step': '0.01'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


class OfferStatusForm(forms.Form):
    """Form for updating offer status (admin/moderator)"""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for status change (optional)...'})
    )


class BookingStatusForm(forms.Form):
    """Form for updating booking status"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Category description...'})
        }
