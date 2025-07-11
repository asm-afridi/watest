import requests
from django.conf import settings

class WhatsAppClient:
    def __init__(self):
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.base_url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages"

    def send_text_message(self, to_number, message_body):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        data = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message_body},
        }
        response = requests.post(self.base_url, headers=headers, json=data)
        return response.json()