from django.contrib import admin

from . import models


class CellInline(admin.TabularInline):
    model = models.Cell


@admin.register(models.Maze)
class MazeAdmin(admin.ModelAdmin):
    inlines = [
        CellInline,
    ]


@admin.register(models.Step)
class StepAdmin(admin.ModelAdmin):
    pass
