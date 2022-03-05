from django.core.exceptions import ValidationError
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
            "rule_label": "Title starts with A-M",
        },
        EAST: {
            "step": (1, 0),
            "authority": "east",
            "rule_label": "Even Number of Pages",
        },
        SOUTH: {
            "step": (0, 1),
            "authority": "south",
            "rule_label": "Title starts with N-Z",
        },
        WEST: {
            "step": (-1, 0),
            "authority": "west",
            "rule_label": "Odd Number of pages",
        },
    }

    @classmethod
    def validate_move_north(cls, cleaned_data):
        title = cleaned_data["title"]
        title_start = title[0].lower()
        if ord(title_start) < ord("a") or ord(title_start) > ord("m"):
            raise ValidationError(
                "Title must start with A-M to move North", code="invalid_north"
            )

    @classmethod
    def validate_move_south(cls, cleaned_data):
        title = cleaned_data["title"]
        title_start = title[0].lower()
        if ord(title_start) < ord("n") or ord(title_start) > ord("z"):
            raise ValidationError(
                "Title must start with N-Z to move South", code="invalid_south"
            )

    @classmethod
    def validate_move_east(cls, cleaned_data):
        pages = cleaned_data["pages"]
        if pages % 2 != 0:
            raise ValidationError(
                "Pages must be even to move East", code="invalid_east"
            )

    @classmethod
    def validate_move_west(cls, cleaned_data):
        pages = cleaned_data["pages"]
        if pages % 2 != 1:
            raise ValidationError("Pages must be odd to move West", code="invalid_west")


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

    def get_direction_choices(self):
        reduced_choices = []
        for direction, label in Directions.CHOICES:
            if not direction or self.can_move(direction):
                rule = Directions.meta[direction]["rule_label"]
                reduced_choices.append((direction, f"{label} ({rule})"))
        return reduced_choices


class Task(models.Model):
    EASY = 10
    MEDIUM = 20
    HARD = 30

    DIFFICULTIES = (
        (EASY, "Easy"),
        (MEDIUM, "Medium"),
        (HARD, "Hard"),
    )

    difficulty = models.IntegerField(choices=DIFFICULTIES, default=EASY)
    description = models.CharField(max_length=1000)


class Maze(models.Model):
    title = models.CharField(max_length=1000, blank=True)
    height = models.IntegerField(default=10)
    width = models.IntegerField(default=10)

    current_x = models.IntegerField(default=0)
    current_y = models.IntegerField(default=0)

    end_x = models.IntegerField(default=0)
    end_y = models.IntegerField(default=0)

    task_difficulty = models.IntegerField(
        choices=Task.DIFFICULTIES, null=True, blank=True, default=None
    )
    next_task = models.ForeignKey(
        Task, on_delete=models.SET_NULL, null=True, blank=True
    )

    finished = models.BooleanField(default=False)
    users = models.ManyToManyField("auth.User")

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
        if cell.x == self.end_x and cell.y == self.end_y:
            self.finished = True
            self.save()

    def user_can_navigate(self, user):
        if self.finished:
            return False
        return self.users.filter(id=user.id).exists()


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
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
