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
    title = models.CharField(max_length=1000, blank=True)
    height = models.IntegerField(default=10)
    width = models.IntegerField(default=10)

    current_x = models.IntegerField(default=0)
    current_y = models.IntegerField(default=0)

    end_x = models.IntegerField(default=0)
    end_y = models.IntegerField(default=0)

    finished = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}: {self.title}"

    def generate_cells(self):
        maze_gen = MazeGenerator()
        maze_gen.generator = Prims(self.height, self.width)
        maze_gen.generate()
        for x in range(self.width):
            for y in range(self.height):
                cell = Cell(x=x, y=y, maze=self)
                for dir_meta in Directions.meta.values():
                    dx, dy = dir_meta["step"]
                    if maze_gen.grid[y * 2 + 1 + dy][x * 2 + 1 + dx] == 0:
                        setattr(cell, "path_{}".format(dir_meta["authority"]), True)
                if cell.x == self.current_x and cell.y == self.current_y:
                    cell.seen = True
                cell.save()
        self.set_end()

    def set_end(self):
        self.end_x = self.width - 1
        self.end_y = self.height - 1
        self.save()

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
        cell = self.get_current_cell()
        cell.seen = True
        cell.save()


class Step(models.Model):
    direction = models.IntegerField(
        choices=Directions.CHOICES, blank=False, default=None
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    title = models.CharField(max_length=1000, blank=True)
    author = models.CharField(max_length=1000, blank=True)
    reader = models.CharField(max_length=1000, blank=True)
    pages = models.IntegerField(null=True)

    maze = models.ForeignKey(Maze, on_delete=models.CASCADE)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
