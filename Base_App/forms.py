from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, time
from .models import BookTable, Feedback


# ============================================================================
# BOOKING TABLE FORM
# ============================================================================

class BookTableForm(forms.ModelForm):
    """Form for table booking with comprehensive validation"""
    
    # Custom field for better UX
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat(),
        }),
        help_text="Select a date (today or later)",
        label="Booking Date"
    )
    
    booking_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
            'min': '10:00',
            'max': '22:00',
        }),
        help_text="Select time between 10:00 AM - 10:00 PM",
        label="Booking Time"
    )

    class Meta:
        model = BookTable
        fields = ['name', 'email', 'phone_number', 'total_persons', 'booking_date', 'booking_time', 'special_requests']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True,
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 XXXXX XXXXX',
                'required': True,
            }),
            'total_persons': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20',
                'placeholder': 'Number of people',
                'required': True,
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requirements? (high chair, allergies, occasion, etc.)',
            }),
        }

    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')
        
        if not name:
            raise ValidationError("Name is required.")
        
        # Check minimum length
        if len(name) < 2:
            raise ValidationError("Name must be at least 2 characters long.")
        
        # Check maximum length
        if len(name) > 100:
            raise ValidationError("Name cannot exceed 100 characters.")
        
        # Check for valid characters (letters, spaces, hyphens only)
        import re
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            raise ValidationError("Name can only contain letters, spaces, hyphens, and apostrophes.")
        
        return name

    def clean_email(self):
        """Validate email field"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError("Email is required.")
        
        # Check if email format is valid (basic check)
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Please enter a valid email address.")
        
        return email

    def clean_phone_number(self):
        """Validate phone number"""
        phone_number = self.cleaned_data.get('phone_number')
        
        if not phone_number:
            raise ValidationError("Phone number is required.")
        
        # Remove common separators
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # Check if it's a valid phone number (10-15 digits)
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValidationError("Please enter a valid phone number (10-15 digits).")
        
        # For Indian numbers specifically
        if len(cleaned) == 10:
            # Valid Indian mobile number
            if not cleaned.startswith(('6', '7', '8', '9')):
                raise ValidationError("Please enter a valid Indian phone number.")
        
        return phone_number

    def clean_total_persons(self):
        """Validate number of persons"""
        total_persons = self.cleaned_data.get('total_persons')
        
        if not total_persons:
            raise ValidationError("Number of persons is required.")
        
        if total_persons < 1 or total_persons > 20:
            raise ValidationError("Number of persons must be between 1 and 20.")
        
        return total_persons

    def clean_booking_date(self):
        """Validate booking date"""
        booking_date = self.cleaned_data.get('booking_date')
        
        if not booking_date:
            raise ValidationError("Booking date is required.")
        
        # Check if date is not in the past
        if booking_date < timezone.now().date():
            raise ValidationError("Booking date cannot be in the past.")
        
        # Check if date is not too far in the future (max 90 days)
        max_date = timezone.now().date() + timedelta(days=90)
        if booking_date > max_date:
            raise ValidationError("Bookings can only be made up to 90 days in advance.")
        
        # Check if restaurant is open on that day (optional - customize as needed)
        # For now, we allow all days. You can add logic to block certain days (e.g., Mondays)
        
        return booking_date

    def clean_booking_time(self):
        """Validate booking time"""
        booking_time = self.cleaned_data.get('booking_time')
        
        if not booking_time:
            raise ValidationError("Booking time is required.")
        
        # Define opening hours
        opening_time = time(10, 0)  # 10:00 AM
        closing_time = time(22, 0)  # 10:00 PM
        
        # Check if booking time is within operating hours
        if booking_time < opening_time or booking_time > closing_time:
            raise ValidationError("Booking time must be between 10:00 AM and 10:00 PM.")
        
        return booking_time

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        booking_time = cleaned_data.get('booking_time')
        
        # Check if booking is too soon (at least 30 minutes from now)
        if booking_date and booking_time:
            from datetime import datetime
            booking_datetime = datetime.combine(booking_date, booking_time)
            booking_datetime = timezone.make_aware(booking_datetime)
            time_until_booking = booking_datetime - timezone.now()
            
            if time_until_booking < timedelta(minutes=30):
                raise ValidationError(
                    "Booking must be at least 30 minutes from now. "
                    "For urgent bookings, please call us directly."
                )
        
        return cleaned_data

    def clean_special_requests(self):
        """Validate special requests field"""
        special_requests = self.cleaned_data.get('special_requests')
        
        if special_requests and len(special_requests) > 500:
            raise ValidationError("Special requests cannot exceed 500 characters.")
        
        return special_requests


# ============================================================================
# FEEDBACK FORM
# ============================================================================

class FeedbackForm(forms.ModelForm):
    """Form for customer feedback and reviews"""
    
    class Meta:
        model = Feedback
        fields = ['user_name', 'email', 'rating', 'description', 'image']
        widgets = {
            'user_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name',
                'max_length': 100,
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True,
            }),
            'rating': forms.RadioSelect(attrs={
                'class': 'form-check-input',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with us. What did you love? What could we improve?',
                'required': True,
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'help_text': 'Optional: Upload a photo from your visit',
            }),
        }

    def clean_user_name(self):
        """Validate user name"""
        user_name = self.cleaned_data.get('user_name')
        
        if not user_name:
            raise ValidationError("Name is required.")
        
        if len(user_name) < 2:
            raise ValidationError("Name must be at least 2 characters long.")
        
        if len(user_name) > 100:
            raise ValidationError("Name cannot exceed 100 characters.")
        
        return user_name

    def clean_email(self):
        """Validate email"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError("Email is required.")
        
        return email

    def clean_rating(self):
        """Validate rating"""
        rating = self.cleaned_data.get('rating')
        
        if not rating:
            raise ValidationError("Please select a rating.")
        
        if rating < 1 or rating > 5:
            raise ValidationError("Rating must be between 1 and 5.")
        
        return rating

    def clean_description(self):
        """Validate feedback description"""
        description = self.cleaned_data.get('description')
        
        if not description:
            raise ValidationError("Please share your feedback.")
        
        if len(description) < 10:
            raise ValidationError("Feedback must be at least 10 characters long.")
        
        if len(description) > 1000:
            raise ValidationError("Feedback cannot exceed 1000 characters.")
        
        # Check for spam/inappropriate content (basic check)
        spam_words = ['casino', 'lottery', 'viagra', 'forex']
        description_lower = description.lower()
        for word in spam_words:
            if word in description_lower:
                raise ValidationError("Your feedback contains inappropriate content.")
        
        return description

    def clean_image(self):
        """Validate image file"""
        image = self.cleaned_data.get('image')
        
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image size must not exceed 5MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_types:
                raise ValidationError(
                    "Only JPG, PNG, GIF, and WebP images are allowed. "
                    f"You uploaded {image.content_type}."
                )
        
        return image

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        
        # All fields are individually validated above
        # Add any cross-field validation here if needed
        
        return cleaned_data


# ============================================================================
# OPTIONAL: CONTACT FORM (Bonus)
# ============================================================================

class ContactForm(forms.Form):
    """Simple contact form for inquiries"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name',
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your phone number (optional)',
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject',
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your message',
        })
    )

    def clean_name(self):
        """Validate name"""
        name = self.cleaned_data.get('name')
        
        if len(name) < 2:
            raise ValidationError("Name must be at least 2 characters.")
        
        return name

    def clean_message(self):
        """Validate message"""
        message = self.cleaned_data.get('message')
        
        if len(message) < 10:
            raise ValidationError("Message must be at least 10 characters.")
        
        return message