from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse

from .models import Maze


def index(request):
    return render(request, "bookmaze/index.html")


def maze(request, maze_id, clear=True):
    maze = get_object_or_404(Maze, pk=maze_id)
    context = {
        "maze": maze,
        "ajax_url": maze.get_ajax_url(clear=clear),
    }
    return render(request, "maze/maze.html", context)


def ajax_maze(request, maze_id, clear=False):
    if clear:
        # TODO permissions check
        pass
    maze = get_object_or_404(Maze, pk=maze_id)
    data = {
        "height": maze.height,
        "width": maze.width,
        "current_x": maze.current_x,
        "current_y": maze.current_y,
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
