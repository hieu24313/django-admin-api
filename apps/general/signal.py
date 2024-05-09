from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.general.models import Report
from ultis.socket_friend_helper import send_noti_report_to_user


@receiver(post_save, sender=Report)
def product_saved(sender, instance, created, **kwargs):
    if instance.is_verified:
        count_report = Report.objects.filter(direct_user=instance.direct_user, is_verified=True).count()
        if count_report < 4:
            send_noti_report_to_user(instance.direct_user, count_report)
        else:  # band
            ...