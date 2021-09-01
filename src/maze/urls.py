from django.urls import path

from . import views

app_name = "maze"

urlpatterns = [
    path("", views.index, name="index"),
    path("maze/<slug:maze_id>/", views.maze, name="maze"),
    path("ajax/maze/<slug:maze_id>/", views.ajax_maze, name="ajax_maze"),
    path(
        "ajax/maze/<slug:maze_id>/clear/",
        views.ajax_maze,
        name="ajax_maze_clear",
        kwargs={"clear": True},
    ),
]
