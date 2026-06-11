from django.contrib import admin
from .models import CommunityReview
from .models import NewsletterLead


@admin.register(CommunityReview)
class CommunityReviewAdmin(admin.ModelAdmin):
    list_display = (
        "instagram",
        "title",
    )


@admin.register(NewsletterLead)
class NewsletterLeadAdmin(admin.ModelAdmin):
    list_display = ("email", "coupon_code", "created_at")
    search_fields = ("email",)
    list_filter = ("created_at",)