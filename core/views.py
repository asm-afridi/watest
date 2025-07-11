from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from .models import Message
from .serializers import MessageSerializer
from .whatsapp import WhatsAppClient
from django.conf import settings

@csrf_exempt
@require_POST
def whatsapp_webhook(request):
    """
    Handle incoming WhatsApp messages and webhook verification.
    """
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == settings.WHATSAPP_VERIFY_TOKEN:
            return HttpResponse(challenge, content_type='text/plain')
        return HttpResponse('Verification token mismatch', status=403)

    try:
        data = json.loads(request.body.decode('utf-8'))
        if 'entry' in data and len(data['entry']) > 0:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        for message in change['value'].get('messages', []):
                            msg = Message(
                                message_id=message.get('id'),
                                from_number=message.get('from'),
                                to_number=change['value']['metadata']['display_phone_number'],
                                message_type=message.get('type'),
                                content=message.get('text', {}).get('body', '') if message.get('type') == 'text' else 'Media',
                                direction='inbound'
                            )
                            msg.save()

        return JsonResponse({'status': 'success'}, status=200)
    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON', status=400)
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)
    
class SendMessageView(APIView):
    """
    API endpoint to send WhatsApp messages.
    """
    def post(self, request):
        to_number = request.data.get('to_number')
        message_body = request.data.get('message_body')

        if not to_number or not message_body:
            return Response({'error': 'to_number and message_body are required'}, status=status.HTTP_400_BAD_REQUEST)

        client = WhatsAppClient()
        response = client.send_text_message(to_number, message_body)

        if 'messages' in response:
            msg = Message(
                message_id=response['messages'][0]['id'],
                from_number=settings.WHATSAPP_PHONE_NUMBER_ID,
                to_number=to_number,
                message_type='text',
                content=message_body,
                direction='outbound'
            )
            msg.save()
            return Response({'status': 'Message sent', 'message_id': msg.message_id}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to send message', 'details': response}, status=status.HTTP_400_BAD_REQUEST)

class MessageListView(APIView):
    """
    API endpoint to list all messages.
    """
    def get(self, request):
        messages = Message.objects.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)