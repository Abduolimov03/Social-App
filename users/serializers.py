from ckeditor_uploader.views import upload
from django.core.validators import FileExtensionValidator
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from urllib3.util.connection import allowed_gai_family

from shared.utility import check_email_or_phone_number, valid_username
from .models import CustomUser, CodeVerified, VIA_EMAIL, VIA_PHONE, CODE_VERIFIED, DONE, PHOTO_DONE
from django.core.mail import send_mail
from django.conf import settings

class SignUnSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_type = serializers.CharField(required=False, read_only=True)
    auth_status = serializers.CharField(required=False, read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'auth_type', 'auth_status']

    def create(self, validated_data):
        user = super(SignUnSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_mail(
                subject="Tasdiqlash kodi",
                message=f"Sizning tasdiqlash kodingiz: {code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"VIA_EMAIL CODE: {code}")
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            # send_phone(user.phone, code)
            print(f"VIA_PHONE CODE: {code}")
        user.save()
        return user

    def validate(self, data):
        super().validate(data)
        data = self.auth_validate(data)
        return data

    def validate_email_phone_number(self, data):
        if data and CustomUser.objects.filter(email=data).exists():
            raise ValidationError("Bu email mavjud")
        elif data and CustomUser.objects.filter(phone_number=data).exists():
            raise ValidationError('Bu telefon raqam mavjud')
        return data

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_phone_number')).lower()
        auth_type = check_email_or_phone_number(user_input)

        if auth_type == 'email':
            data = {
                'auth_type' : VIA_EMAIL,
                'email' : user_input
            }
        elif auth_type == 'phone_number':
            data = {
                'auth_type' : VIA_PHONE,
                'phone_number' : user_input
            }
        else:
            data = {
                'succes' : False,
                'msg' : 'siz telefon raqam yoki email kiritishingiz kerak'
            }
            raise ValidationError(data)
        return data

    def to_representation(self, instance):
        data = super(SignUnSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data


class ChangeInfoUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise ValidationError('parollar mos emas')

        # current_user = CustomUser.objects.filter(username=data.get('username')).exists()
        #
        # if current_user:
        #     raise ValidationError('Bu username mavjud!')

        if not valid_username(data.get("username")):
            raise ValidationError("Username mukamal emas")


        return data



    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username')
        instance.password = validated_data.get('password', None)
        if instance.password:
            instance.set_password(validated_data.get('password'))

        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance

class CreatePhotoUserSerializer(serializers.Serializer):
    photo = serializers.ImageField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    def update(self, instance, validated_data):
        photo = validated_data.get("photo")
        if photo and instance.auth_status in [DONE, PHOTO_DONE]:
            instance.photo = photo
            instance.auth_status = PHOTO_DONE
            instance.save()
        else:
            raise ValidationError(
                {
                    'msg': 'Siz hali toliq ro‘yxatdan o‘tmadingiz',
                    'status': status.HTTP_400_BAD_REQUEST
                }
            )
        return instance


