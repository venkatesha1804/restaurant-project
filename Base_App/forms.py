# Base_App/forms.py - COMPLETE FIXED VERSION

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from Base_App.models import (
    BookTable, Feedback, ItemRating
)

# ============================================================================
# USER AUTHENTICATION FORMS
# ============================================================================

class SignUpForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username',
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter password',
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirm password',
            }),
        }


# ============================================================================
# BOOKING FORM
# ============================================================================

class BookTableForm(forms.ModelForm):
    """Form for booking a table"""
    
    class Meta:
        model = BookTable
        fields = ['name', 'email', 'phone_number', 'total_persons', 'booking_date', 'booking_time', 'special_requests']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
            }),
            'total_persons': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20',
            }),
            'booking_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'booking_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requests? (allergies, high chair, etc.)',
            }),
        }


# ============================================================================
# FEEDBACK FORM
# ============================================================================

class FeedbackForm(forms.ModelForm):
    """Form for customer feedback"""
    
    class Meta:
        model = Feedback
        fields = ['user_name', 'email', 'rating', 'description', 'image']
        widgets = {
            'user_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email',
            }),
            'rating': forms.RadioSelect(attrs={
                'class': 'form-check-input',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about your experience...',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }


# ============================================================================
# CONTACT FORM
# ============================================================================

class ContactForm(forms.Form):
    """Form for contact messages"""
    
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
            'placeholder': 'Your email',
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your phone number',
        })
    )
    
    subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject',
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your message...',
        })
    )


# ============================================================================
# ITEM RATING FORM
# ============================================================================

class ItemRatingForm(forms.ModelForm):
    """Form for rating items"""
    
    class Meta:
        model = ItemRating
        fields = ['customer_name', 'customer_email', 'rating', 'review']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': True
            }),
            'rating': forms.RadioSelect(attrs={
                'class': 'form-check-input',
            }),
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience (optional)',
                'rows': 4
            }),
        }
