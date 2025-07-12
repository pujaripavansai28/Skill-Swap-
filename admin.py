# core/admin.py

from django.contrib import admin
from .models import Profile, Skill, SwapRequest, Review

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