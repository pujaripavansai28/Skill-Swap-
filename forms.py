# core/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Skill

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)

class ProfileForm(forms.ModelForm):
    # We use a special widget to make selecting skills more user-friendly
    skills_offered = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    skills_wanted = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Profile
        # These are the fields from our Profile model that the user can edit
        fields = ['location', 'availability', 'skills_offered', 'skills_wanted', 'is_public']
        help_texts = {
            'is_public': 'Check this box to make your profile visible to other users for skill swapping.'
        }