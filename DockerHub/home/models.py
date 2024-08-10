from django.db import models
from uuid import uuid4
from django.contrib.auth.models import User


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    port = models.CharField(max_length=10, blank=True, null=True)
    code_server_port = models.CharField(max_length=10, blank=True, null=True)
    container_id = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=10, choices=[('ESP32', 'ESP32'), ('RP2040', 'RP2040')])
    language = models.CharField(max_length=10, choices=[('C', 'C'), ('Python', 'Python')])
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
