from django.contrib import admin

from . import models


@admin.register(models.AccessCode)
class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ("access_code",)
