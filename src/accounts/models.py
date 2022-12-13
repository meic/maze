from django.db import models


class AccessCode(models.Model):
    access_code = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField("auth.User", blank=True)
