from django.db import models

# Create your models here.

class CommunityReview(models.Model):
    photo = models.ImageField(upload_to="community/")
    instagram = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()

    rating = models.PositiveSmallIntegerField(
        default=5,
        choices=[
            (1, "1 estrela"),
            (2, "2 estrelas"),
            (3, "3 estrelas"),
            (4, "4 estrelas"),
            (5, "5 estrelas"),
        ]
    )

    def __str__(self):
        return self.instagram

class NewsletterLead(models.Model):
    email = models.EmailField(unique=True)
    coupon_code = models.CharField(max_length=50, default="RISK15")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Email da newsletter"
        verbose_name_plural = "Emails da newsletter"

    def __str__(self):
        return self.email