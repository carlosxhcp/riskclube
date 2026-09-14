from django.contrib import admin
from .models import CommunityReview
from .models import NewsletterLead
from .models import Category

@admin.register(CommunityReview)
class CommunityReviewAdmin(admin.ModelAdmin):
    list_display = (
        "instagram",
        "title",
    )

