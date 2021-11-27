from freezegun import freeze_time

from django.core import mail

from elk.utils.testing import TestCase, create_customer
from market.models import Subscription
from market.tasks import notify_student_subscription
from products.models import Product1


@freeze_time('2021-11-26 12:00')
class TestSubscriptionNotice(TestCase):
    fixtures = ('lessons', 'products')

    @classmethod
    def setUpTestData(cls):
        cls.customer = create_customer()
        cls.product = Product1.objects.get(pk=1)

    def setUp(self):
        self.sub = Subscription(
            customer=self.customer,
            product=self.product,
            buy_price=5
        )
        self.sub.save()

    def test_update_last_lesson_date(self):
        with freeze_time('2032-12-01 12:00'):
            self.sub.update_last_lesson_date()
            self.assertEqual(self.sub.last_lesson_date, self.tzdatetime(2032, 12, 1, 12, 0))

    def test_notify_student_subscription(self):
        self.sub.last_lesson_date = self.tzdatetime(2032, 12, 1, 12, 0)
        self.sub.buy_date = self.tzdatetime(2032, 12, 1, 12, 0)
        self.sub.save()

        # week forward
        with freeze_time('2032-12-08 12:00'):
            notify_student_subscription()

            self.assertEqual(len(mail.outbox), 1)
