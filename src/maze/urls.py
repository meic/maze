from django.urls import path

from . import views

app_name = "maze"

urlpatterns = [
    path("", views.index, name="index"),
    path("maze/create/", views.MazeCreateView.as_view(), name="maze_create"),
    path("maze/my/create/", views.MyMazeCreateView.as_view(), name="my_maze_create"),
    path(
        "maze/<slug:maze_id>/clear/",
        views.maze,
        name="maze",
        kwargs={"clear": True},
    ),
    path("maze/<slug:maze_id>/", views.maze, name="maze"),
    path("ajax/maze/<slug:maze_id>/", views.ajax_maze, name="ajax_maze"),
    path(
        "ajax/maze/<slug:maze_id>/clear/",
        views.ajax_maze,
        name="ajax_maze_clear",
        kwargs={"clear": True},
    ),
]
