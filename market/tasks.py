from datetime import timedelta

from django.utils import timezone

from elk.celery import app as celery
from .models import Subscription
from .signals import subscription_notice


@celery.task
def notify_student_subscription():
    today = timezone.now()
    week_passed = today - timedelta(weeks=1)
    buy_date = today - timedelta(weeks=6)
    for item in Subscription.objects.filter(
         is_fully_used=False, last_lesson_date__lte=week_passed, buy_date__gte=buy_date):
        subscription_notice.send(sender=notify_student_subscription, instance=item)
