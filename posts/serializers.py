from rest_framework import serializers
from .models import Post, PostMedia, PostLike, Comment
from rest_framework import serializers


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


class CommentCreateSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField(write_only=True)
    parent_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Comment
        fields = ['post_id', 'parent_id', 'text']

    def validate(self, attrs):
        # Post mavjudligini tekshiramiz
        try:
            post = Post.objects.get(id=attrs['post_id'])
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post topilmadi")

        parent_id = attrs.get('parent_id')
        if parent_id:
            parent = Comment.objects.filter(id=parent_id, post=post).first()
            if not parent:
                raise serializers.ValidationError("Parent comment noto‘g‘ri")

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        post = Post.objects.get(id=validated_data['post_id'])

        parent = None
        parent_id = validated_data.get('parent_id')
        if parent_id:
            parent = Comment.objects.get(id=parent_id)

        comment = Comment.objects.create(
            user=user,
            post=post,
            text=validated_data['text'],
            parent=parent
        )
        return comment



class CommentReplySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at']


class CommentListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    replies = CommentReplySerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'text',
            'created_at',
            'likes_count',
            'replies'
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()
