from itertools import zip_longest

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
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
    mazes = Maze.objects.all().order_by("id")
    user_mazes = []
    show_user_mazes = False
    if request.user.is_authenticated:
        user_mazes = Maze.objects.filter(users=request.user).order_by("id")
        show_user_mazes = user_mazes.exists()
    context = {
        "maze_rows": zip_longest(*[iter(mazes)] * 3),
        "show_user_mazes": show_user_mazes,
        "user_maze_rows": zip_longest(*[iter(user_mazes)] * 3),
    }
    return render(request, "maze/index.html", context)


def maze(request, maze_id, clear=False):
    if clear:
        if not request.user.is_superuser:
            raise PermissionDenied
    maze = get_object_or_404(Maze, pk=maze_id)

    form = None
    if request.user.is_authenticated and maze.user_can_navigate(request.user):
        if request.method == "POST":
            form = StepForm(request.POST, maze=maze, user=request.user)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(request.path_info)
        else:
            form = StepForm(maze=maze, user=request.user)

    all_steps = maze.step_set.all().order_by("-timestamp")
    step_paginator = Paginator(all_steps, 5)
    page_number = request.GET.get("page", 1)
    step_page = step_paginator.page(page_number)

    context = {
        "form": form,
        "maze": maze,
        "step_page": step_page,
        "ajax_url": maze.get_ajax_url(clear=clear),
    }
    return render(request, "maze/maze.html", context)


def ajax_maze(request, maze_id, clear=False):
    if clear:
        if not request.user.is_superuser:
            raise PermissionDenied
    maze = get_object_or_404(Maze, pk=maze_id)
    data = {
        "height": maze.height,
        "width": maze.width,
        "current_x": maze.current_x,
        "current_y": maze.current_y,
        "end_x": maze.end_x,
        "end_y": maze.end_y,
        "finished": maze.finished,
        "cells": [],
    }
    cells = {}
    for cell in maze.cells.all().order_by("y", "x"):
        cells[(cell.x, cell.y)] = cell

    for cell in cells.values():
        cell_data = {
            "x": cell.x,
            "y": cell.y,
            "seen": cell.seen,
        }
        if cell.seen or clear or maze.finished:
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
