# core/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Skill

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)

class ProfileForm(forms.ModelForm):
    # Choices for our new availability checkboxes
    AVAILABILITY_CHOICES = [
        ('mornings', 'Mornings'),
        ('afternoons', 'Afternoons'),
        ('evenings', 'Evenings'),
        ('weekdays', 'Weekdays'),
        ('weekends', 'Weekends'),
    ]

    # Override the default text field with a set of checkboxes
    availability = forms.MultipleChoiceField(
        choices=AVAILABILITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Your General Availability"
    )

    # Add a datalist to the location input for autocomplete suggestions
    location = forms.CharField(
        widget=forms.TextInput(attrs={'list': 'city-suggestions'}),
        required=False
    )
    
    skills_wanted = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Profile
        fields = ['location', 'availability', 'skills_wanted', 'is_public']

# core/forms.py

# ... (keep your existing CustomUserCreationForm and ProfileForm)
from .models import Review

# --- ADD THIS NEW FORM CLASS ---
class ReviewForm(forms.ModelForm):
    # Make the rating a more attractive set of radio buttons
    rating = forms.ChoiceField(
        choices=[(i, f'{i} Stars') for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Overall Rating"
    )

    class Meta:
        model = Review
        # We only want the user to fill out these two fields
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'placeholder': 'Share your experience... How was the communication? Was the skill exchange helpful?',
                    'rows': 4
                }
            ),
        }


class AddSkillForm(forms.Form):
    # We query all skills and show them in a dropdown.
    skill = forms.ModelChoiceField(
        queryset=Skill.objects.all(),
        label="Select a skill to offer",
        widget=forms.Select(attrs={'class': 'form-select'})
    )