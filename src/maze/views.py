from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.generic import TemplateView

from .models import Maze


def index(request):
    return render(request, "bookmaze/index.html")


class MazeView(TemplateView):
    template_name = "maze.html"


def ajax_maze(request, maze_id, clear=False):
    if clear:
        # TODO permissions check
        pass
    maze = get_object_or_404(Maze, pk=maze_id)
    data = {
        "height": maze.height,
        "width": maze.width,
        "cells": [],
    }
    for cell in maze.cell_set.all().order_by("y", "x"):

        data["cells"].append(
            {
                "x": cell.x,
                "y": cell.y,
                "seen": cell.seen,
            }
        )
        if cell.seen or clear:
            data["cells"][-1].update(
                {
                    "path_north": cell.path_north,
                    "path_east": cell.path_east,
                    "path_south": cell.path_south,
                    "path_west": cell.path_west,
                }
            )
    return JsonResponse(data)
