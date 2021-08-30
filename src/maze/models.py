from django.db import models

from mazelib import Maze as MazeGenerator
from mazelib.generate.Prims import Prims


class Directions:
    NORTH = 10
    EAST = 20
    SOUTH = 30
    WEST = 40

    meta = {
        NORTH: {
            "step": (0, -1),
            "authority": "north",
        },
        EAST: {
            "step": (1, 0),
            "authority": "east",
        },
        SOUTH: {
            "step": (0, 1),
            "authority": "south",
        },
        WEST: {
            "step": (-1, 0),
            "authority": "west",
        },
    }


class Cell(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()
    seen = models.BooleanField(default=False)
    path_north = models.BooleanField(default=False)
    path_south = models.BooleanField(default=False)
    path_east = models.BooleanField(default=False)
    path_west = models.BooleanField(default=False)

    maze = models.ForeignKey("Maze", on_delete=models.CASCADE)


class Maze(models.Model):
    height = models.IntegerField()
    width = models.IntegerField()

    @classmethod
    def create(cls, width, height):
        maze = cls.objects.create(width=width, height=height)
        maze_gen = MazeGenerator()
        maze_gen.generator = Prims(height, width)
        maze_gen.generate()
        for x in range(maze.width):
            for y in range(maze.height):
                cell = Cell(x=x, y=y, maze=maze)
                for dir_meta in Directions.meta.values():
                    dx, dy = dir_meta["step"]
                    if maze_gen.grid[y * 2 + 1 + dy][x * 2 + 1 + dx] == 0:
                        setattr(cell, "path_{}".format(dir_meta["authority"]), True)
                cell.save()
