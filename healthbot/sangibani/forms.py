from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile
from django.core.exceptions import ValidationError
import re

class UserRegisterForm(UserCreationForm):
    # Personal Information
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your first name',
            'autocomplete': 'given-name'
        }),
        error_messages={
            'required': 'First name is required.',
            'max_length': 'First name cannot exceed 30 characters.'
        }
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your last name',
            'autocomplete': 'family-name'
        }),
        error_messages={
            'required': 'Last name is required.',
            'max_length': 'Last name cannot exceed 30 characters.'
        }
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        }),
        error_messages={
            'required': 'Email address is required.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    # Health Information (Optional)
    age = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Your age',
            'min': '1',
            'max': '120'
        }),
        error_messages={
            'min_value': 'Age must be at least 1.',
            'max_value': 'Age cannot exceed 120.'
        }
    )
    
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+91 9876543210',
            'autocomplete': 'tel'
        }),
        error_messages={
            'max_length': 'Phone number cannot exceed 15 characters.'
        }
    )
    
    HEALTH_CONDITION_CHOICES = [
        ('', 'Select a condition (optional)'),
        ('none', 'None'),
        ('pregnancy', 'Pregnancy'),
        ('diabetes', 'Diabetes'),
        ('hypertension', 'Hypertension'),
        ('asthma', 'Asthma'),
        ('heart_disease', 'Heart Disease'),
        ('other', 'Other'),
    ]
    
    health_condition = forms.ChoiceField(
        choices=HEALTH_CONDITION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    
    medications = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'List any current medications (optional)',
            'rows': '3'
        }),
        help_text='Separate medications with commas.'
    )
    
    # Terms and Conditions
    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'terms-checkbox'
        }),
        error_messages={
            'required': 'You must agree to the terms and conditions.'
        }
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Choose a username',
                'autocomplete': 'username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'Create a password',
                'autocomplete': 'new-password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'Confirm your password',
                'autocomplete': 'new-password'
            }),
        }
        
        error_messages = {
            'username': {
                'required': 'Username is required.',
                'max_length': 'Username cannot exceed 150 characters.',
                'unique': 'This username is already taken.'
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize help texts
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = [
            'Your password must contain at least 8 characters.',
            'Your password can\'t be too similar to your other personal information.',
            'Your password can\'t be a commonly used password.',
            'Your password can\'t be entirely numeric.'
        ]
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Check if username contains only allowed characters
            if not re.match(r'^[\w.@+-]+\Z', username):
                raise ValidationError(
                    'Username can only contain letters, numbers, and @/./+/-/_ characters.'
                )
            # Check if username already exists
            if User.objects.filter(username__iexact=username).exists():
                raise ValidationError('This username is already taken. Please choose a different one.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError('This email address is already registered. Please use a different one.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Basic phone number validation
            phone = phone.strip()
            # Remove any non-digit characters except +
            cleaned_phone = re.sub(r'[^\d+]', '', phone)
            if not re.match(r'^\+?\d{10,15}$', cleaned_phone):
                raise ValidationError('Please enter a valid phone number with country code (e.g., +91 9876543210).')
            return cleaned_phone
        return phone

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and (age < 1 or age > 120):
            raise ValidationError('Please enter a valid age between 1 and 120.')
        return age

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError({
                'password2': ValidationError('Passwords do not match.', code='password_mismatch')
            })

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your username or email',
            'autocomplete': 'username'
        }),
        error_messages={
            'required': 'Please enter your username or email.'
        }
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        }),
        error_messages={
            'required': 'Please enter your password.'
        }
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'remember-me'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages.update({
            'invalid_login': 'Please enter a correct username/email and password. Note that both fields may be case-sensitive.',
            'inactive': 'This account is inactive.',
        })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            return username.strip()
        return username

class UserProfileForm(forms.ModelForm):
    # Personal Information
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'placeholder': 'YYYY-MM-DD'
        }),
        error_messages={
            'invalid': 'Please enter a valid date in YYYY-MM-DD format.'
        }
    )
    
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+91 9876543210',
            'autocomplete': 'tel'
        }),
        error_messages={
            'max_length': 'Phone number cannot exceed 15 characters.'
        }
    )
    
    age = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Your age',
            'min': '1',
            'max': '120'
        }),
        error_messages={
            'min_value': 'Age must be at least 1.',
            'max_value': 'Age cannot exceed 120.'
        }
    )
    
    HEALTH_CONDITION_CHOICES = [
        ('', 'Select a condition (optional)'),
        ('none', 'None'),
        ('pregnancy', 'Pregnancy'),
        ('diabetes', 'Diabetes'),
        ('hypertension', 'Hypertension'),
        ('asthma', 'Asthma'),
        ('heart_disease', 'Heart Disease'),
        ('other', 'Other'),
    ]
    
    health_condition = forms.ChoiceField(
        choices=HEALTH_CONDITION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    
    medications = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'List any current medications (optional)',
            'rows': '3'
        }),
        help_text='Separate medications with commas.'
    )
    
    # Additional profile fields
    GENDER_CHOICES = [
        ('', 'Select gender (optional)'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your address (optional)',
            'rows': '2'
        }),
        max_length=255
    )
    
    emergency_contact = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Emergency contact number'
        }),
        help_text='Phone number of emergency contact person.'
    )
    
    blood_group = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g., A+'
        }),
        help_text='Your blood group (optional).'
    )
    
    allergies = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'List any allergies (optional)',
            'rows': '2'
        }),
        help_text='Separate allergies with commas.'
    )

    class Meta:
        model = UserProfile
        fields = [
            'date_of_birth', 'phone', 'age', 'gender', 'health_condition', 
            'medications', 'address', 'emergency_contact', 'blood_group', 'allergies'
        ]
        
        error_messages = {
            'phone': {
                'max_length': 'Phone number cannot exceed 15 characters.',
            },
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Basic phone number validation
            phone = phone.strip()
            # Remove any non-digit characters except +
            cleaned_phone = re.sub(r'[^\d+]', '', phone)
            if not re.match(r'^\+?\d{10,15}$', cleaned_phone):
                raise ValidationError('Please enter a valid phone number with country code (e.g., +91 9876543210).')
            return cleaned_phone
        return phone

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and (age < 1 or age > 120):
            raise ValidationError('Please enter a valid age between 1 and 120.')
        return age

    def clean_emergency_contact(self):
        emergency_contact = self.cleaned_data.get('emergency_contact')
        if emergency_contact:
            # Basic phone number validation
            emergency_contact = emergency_contact.strip()
            cleaned_contact = re.sub(r'[^\d+]', '', emergency_contact)
            if not re.match(r'^\+?\d{10,15}$', cleaned_contact):
                raise ValidationError('Please enter a valid emergency contact number.')
            return cleaned_contact
        return emergency_contact

class UserUpdateForm(forms.ModelForm):
    """Form for updating user basic information"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your last name'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists (excluding current user)
            if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError('This email address is already registered. Please use a different one.')
        return email

class PasswordChangeForm(forms.Form):
    """Form for changing password"""
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter current password'
        }),
        error_messages={
            'required': 'Please enter your current password.'
        }
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter new password'
        }),
        error_messages={
            'required': 'Please enter a new password.'
        }
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm new password'
        }),
        error_messages={
            'required': 'Please confirm your new password.'
        }
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError('Your current password was entered incorrectly. Please enter it again.')
        return current_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('The two password fields didn\'t match.')
        
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user