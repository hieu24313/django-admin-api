import uuid

from django.db import models

from apps.user.models import CustomUser


# Create your models here.
class Interaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    STATUS_CHOICES = (
        (0, 'LIKE'),
        (1, 'PENDING'),
        (2, 'UNLIKE'),
    )
    status = models.CharField(max_length=7, default='PENDING')

    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='from_user_interaction')
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='to_user_interaction')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_status(self,status):
        self.status = status
        self.save()