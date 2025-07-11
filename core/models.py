from django.db import models

class Message(models.Model):
    message_id = models.CharField(max_length=100, unique=True)
    from_number = models.CharField(max_length=20)
    to_number = models.CharField(max_length=20)
    message_type = models.CharField(max_length=20)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    direction = models.CharField(max_length=10)  # 'inbound' or 'outbound'

    def __str__(self):
        return f"{self.direction}: {self.from_number} -> {self.to_number}"