from django.db import models
from django.urls import reverse

from mazelib import Maze as MazeGenerator
from mazelib.generate.Prims import Prims


class Directions:
    NORTH = 10
    EAST = 20
    SOUTH = 30
    WEST = 40

    CHOICES = (
        (NORTH, "North"),
        (EAST, "East"),
        (SOUTH, "South"),
        (WEST, "West"),
    )

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

    maze = models.ForeignKey("Maze", on_delete=models.CASCADE, related_name="cells")

    def can_move(self, direction):
        attr = "path_{}".format(Directions.meta[direction]["authority"])
        return getattr(self, attr)

    def reduce_choices(self, choices):
        reduced_choices = []
        for direction, label in choices:
            if not direction or self.can_move(direction):
                reduced_choices.append((direction, label))
        return reduced_choices


class Maze(models.Model):
    height = models.IntegerField()
    width = models.IntegerField()

    current_x = models.IntegerField(default=0)
    current_y = models.IntegerField(default=0)

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
        return maze

    def get_absolute_url(self):
        return reverse("maze:maze", kwargs={"maze_id": self.id})

    def get_ajax_url(self, clear=False):
        if clear:
            name = "maze:ajax_maze_clear"
        else:
            name = "maze:ajax_maze"
        return reverse(name, kwargs={"maze_id": self.id})

    def get_current_cell(self):
        return self.cells.get(x=self.current_x, y=self.current_y)

    def can_move(self, direction):
        cell = self.get_current_cell()
        return cell.can_move(direction)

    def move(self, direction):
        dx, dy = Directions.meta[direction]["step"]
        self.current_x = self.current_x + dx
        self.current_y = self.current_y + dy
        self.save()


class Step(models.Model):
    direction = models.IntegerField(
        choices=Directions.CHOICES, blank=False, default=None
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    maze = models.ForeignKey(Maze, on_delete=models.CASCADE)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
