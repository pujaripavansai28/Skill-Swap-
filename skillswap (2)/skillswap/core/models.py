# core/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator



# A master list of all possible skills on the platform
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserSkill(models.Model):
    user_profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        # Ensure a user can only have a skill once in their offered list
        unique_together = ('user_profile', 'skill')

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.skill.name} ({'Verified' if self.is_verified else 'Not Verified'})"


# Extends Django's built-in User to add our custom fields
class Profile(models.Model):
    # Links this profile to a specific user. If the user is deleted, the profile is also deleted.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Optional fields
    location = models.CharField(max_length=255, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    availability = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., 'Weekends', 'Evenings after 7 PM'")
    
    # User's privacy setting
    is_public = models.BooleanField(default=True)
    skills_offered = models.ManyToManyField(
        Skill, 
        through=UserSkill,  # Use our new model to manage the relationship
        related_name='offered_by', 
        blank=True
    )
    
    
    skills_wanted = models.ManyToManyField(Skill, related_name='wanted_by', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Represents a single request from one user to another
class SwapRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'), # User can cancel a sent request
    ]

    requester = models.ForeignKey(User, related_name='sent_swap_requests', on_delete=models.CASCADE)
    responder = models.ForeignKey(User, related_name='received_swap_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requester_reviewed = models.BooleanField(default=False)
    responder_reviewed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Swap from {self.requester.username} to {self.responder.username} ({self.status})"

# Represents feedback left after a swap is completed
class Review(models.Model):
    swap = models.ForeignKey(SwapRequest, on_delete=models.CASCADE) # One review per swap
    reviewer = models.ForeignKey(User, related_name='given_reviews', on_delete=models.CASCADE)
    reviewee = models.ForeignKey(User, related_name='received_reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewee.username}"


