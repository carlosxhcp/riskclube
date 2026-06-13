from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from orders.models import Order

User = get_user_model()


@receiver(post_save, sender=User)
def link_orders_by_email(sender, instance, created, **kwargs):
    if not instance.email:
        return

    email = instance.email.strip().lower()

    Order.objects.filter(
        user__isnull=True,
        email__iexact=email
    ).update(user=instance)