from django.contrib import admin
from .models import CommunityReview

@admin.register(CommunityReview)
class CommunityReviewAdmin(admin.ModelAdmin):
    list_display = (
        "instagram",
        "title",
    )
