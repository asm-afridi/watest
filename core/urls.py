from django.urls import path
from .views import whatsapp_webhook, SendMessageView, MessageListView

app_name = 'core'

urlpatterns = [
    path('webhook/', whatsapp_webhook, name='whatsapp_webhook'),
    path('send-message/', SendMessageView.as_view(), name='send_message'),
    path('messages/', MessageListView.as_view(), name='message_list'),
]