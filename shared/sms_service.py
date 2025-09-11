import requests
from django.conf import settings

def send_phone(phone_number, code):
    try:
        url = "https://notify.eskiz.uz/api/message/sms/send"
        headers = {
            "Authorization": f"Bearer {settings.ESKIZ_TOKEN}"
        }
        data = {
            "mobile_phone": phone_number,
            "message": f"Sizning tasdiqlash kodingiz: {code}",
            "from": "4546"  # Eskizning default FROM raqami
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code != 200:
            print("SMS yuborishda xatolik:", response.text)
        else:
            print(f"SMS yuborildi -> {phone_number}, code: {code}")

        return response.json()
    except Exception as e:
        print("SMS yuborishda xatolik:", e)
        return None
