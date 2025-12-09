from rest_framework import serializers
from .models import Post, PostMedia, PostLike, Comment


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



class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'file_type']


class PostListSerializer(serializers.ModelSerializer):
    media = PostMediaSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    user = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'caption',
            'location',
            'is_active',
            'created_at',
            'media',
            'likes_count',
            'comments_count'
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()


