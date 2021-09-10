from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from .models import Maze
from .forms import MazeCreateForm, StepForm


class MazeCreateView(PermissionRequiredMixin, CreateView):
    model = Maze
    form_class = MazeCreateForm
    success_url = reverse_lazy("maze:index")
    permission_required = ("maze.add_maze",)
    template_name = "bookmaze/form_view.html"
    extra_context = {"title": "Create Maze"}


def index(request):
    context = {
        "mazes": Maze.objects.all().order_by("id"),
    }
    return render(request, "maze/index.html", context)


def maze(request, maze_id, clear=False):
    maze = get_object_or_404(Maze, pk=maze_id)

    form = None
    if request.user.is_authenticated and not maze.finished:
        # TODO permissions check
        if request.method == "POST":
            form = StepForm(request.POST, maze=maze, user=request.user)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(request.path_info)
        else:
            form = StepForm(maze=maze, user=request.user)

    context = {
        "form": form,
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
        "end_x": maze.end_x,
        "end_y": maze.end_y,
        "cells": [],
    }
    cells = {}
    for cell in maze.cells.all().order_by("y", "x"):
        cells[(cell.x, cell.y)] = cell

    for cell in cells.values():
        cell_data = {
            "x": cell.x,
            "y": cell.y,
            "seen": cell.seen or clear,
        }
        if cell.seen or clear:
            cell_data.update(
                {
                    "path_north": cell.path_north,
                    "path_east": cell.path_east,
                    "path_south": cell.path_south,
                    "path_west": cell.path_west,
                }
            )
        data["cells"].append(cell_data)
    return JsonResponse(data)
