from rest_framework import serializers
from .models import Post, PostMedia


class PostCreateSerializer(serializers.ModelSerializer):
    media = serializers.ListField(
        child=serializers.FileField(),
        write_only=True
    )

    class Meta:
        model = Post
        fields = ['caption', 'location', 'media']

    def create(self, validated_data):
        media_files = validated_data.pop('media', [])
        user = self.context['request'].user

        post = Post.objects.create(user=user, **validated_data)

        for file in media_files:
            ext = file.name.split('.')[-1].lower()
            file_type = "video" if ext in ["mp4", "mov"] else "image"

            PostMedia.objects.create(
                post=post,
                file=file,
                file_type=file_type
            )

        return post
