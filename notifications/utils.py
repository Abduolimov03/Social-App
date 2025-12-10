from .models import Notification
import re
from django.contrib.auth import get_user_model


def create_notification(sender, recipient, notif_type, post=None, comment=None, message=None):
    if sender == recipient:
        return None  # o‘ziga notification kerak emas

    notif = Notification.objects.create(
        sender=sender,
        recipient=recipient,
        notif_type=notif_type,
        post=post,
        comment=comment,
        message=message
    )
    return notif



User = get_user_model()

def create_mentions(sender, text, post=None, comment=None):
    pattern = r'@(\w+)'  # @username
    usernames = re.findall(pattern, text)

    for username in usernames:
        try:
            user = User.objects.get(username=username)
            create_notification(
                sender=sender,
                recipient=user,
                notif_type='mention',
                post=post,
                comment=comment,
                message=f"{sender.username} sizni mention qildi"
            )
        except User.DoesNotExist:
            continue
