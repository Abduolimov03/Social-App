from notifications.utils import create_notification

# Like qilingan joyda
if like_obj:
    like_obj.delete()
    return Response({"liked": False, "message": "Unliked"}, status=200)
else:
    PostLike.objects.create(post=post, user=user)
    create_notification(
        sender=user,
        recipient=post.user,
        notif_type='like',
        post=post,
        message=f"{user.username} sizning postingizni like qildi"
    )
    return Response({"liked": True, "message": "Liked"}, status=201)
