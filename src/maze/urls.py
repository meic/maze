from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("ajax/maze/<slug:maze_id>/", views.ajax_maze, name="ajax_maze"),
    path(
        "ajax/maze/<slug:maze_id>/clear/",
        views.ajax_maze,
        name="ajax_maze",
        kwargs={"clear": True},
    ),
]
