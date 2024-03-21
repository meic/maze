from django.contrib import admin

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Maze)
class MazeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Step)
class StepAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("difficulty", "category", "description")
