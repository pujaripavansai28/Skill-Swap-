# core/admin.py

from django.contrib import admin
from .models import Profile, Skill, SwapRequest, Review, UserSkill # <-- ADD UserSkill to the import

# Simple registrations
admin.site.register(Skill)
admin.site.register(Review)

# Customizing the admin view for better usability
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'is_public')
    search_fields = ('user__username', 'location')

@admin.register(SwapRequest)
class SwapRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'responder', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('requester__username', 'responder__username')


# --- ADD THIS ENTIRE NEW CLASS ---
@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    # Display these columns in the admin list view
    list_display = ('user_profile', 'skill', 'is_verified')
    # Allow filtering by verification status
    list_filter = ('is_verified',)
    # Allow searching by username or skill name
    search_fields = ('user_profile__user__username', 'skill__name')
# --- END OF NEW CLASS ---