from django.db import models
from django.conf import settings
from shared.models import BaseModel

class Notification(BaseModel):
    NOTIF_TYPE = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('mention', 'Mention'),
    )

    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPE)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    post = models.ForeignKey(
        'posts.Post', on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.ForeignKey(
        'posts.Comment', on_delete=models.CASCADE, null=True, blank=True
    )
    is_read = models.BooleanField(default=False)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.sender} -> {self.recipient} ({self.notif_type})"
