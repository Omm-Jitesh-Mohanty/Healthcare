from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Personal Information
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ])
    
    # Health Information
    health_condition = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('none', 'None'),
        ('pregnancy', 'Pregnancy'),
        ('diabetes', 'Diabetes'),
        ('hypertension', 'Hypertension'),
        ('asthma', 'Asthma'),
        ('heart_disease', 'Heart Disease'),
        ('other', 'Other'),
    ])
    medications = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    
    # Emergency Contact
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to create user profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()