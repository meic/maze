from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from easy_select2 import Select2Multiple

from .models import Category, Directions, Maze, Step, Task


class MazeCreateForm(forms.ModelForm):
    class Meta:
        model = Maze
        fields = ["title", "height", "width", "users", "task_difficulty", "category"]
        widgets = {
            "users": Select2Multiple(select2attrs={"width": "100%"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["users"].queryset = User.objects.exclude(is_superuser=True)
        for field in ("title", "task_difficulty", "category"):
            self.fields[field].required = True
        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Create"))

    def save(self, commit=True):
        maze = super().save(commit=commit)
        if commit:
            maze.generate_cells()
            maze.set_next_task()
        return maze


class MyMazeCreateForm(forms.Form):
    size = forms.IntegerField(required=True, min_value=5, max_value=15, initial=10)
    task_difficulity = forms.ChoiceField(choices=Task.DIFFICULTIES)
    category = forms.ModelChoiceField(queryset=Category.objects)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Create"))

    def save(self, user, commit=True):
        maze = Maze(
            title=user.username,
            height=self.cleaned_data["size"],
            width=self.cleaned_data["size"],
            task_difficulty=self.cleaned_data["task_difficulity"],
            category=self.cleaned_data["category"],
        )
        if commit:
            maze.save()
            maze.users.add(user)
            maze.generate_cells()
            maze.set_next_task()
        return maze


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ["title", "author", "reader", "pages", "direction"]
        widgets = {
            "direction": forms.RadioSelect(),
        }

    def __init__(self, *args, maze=None, user=None, **kwargs):
        self.maze = maze
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["author"].required = True
        self.fields["reader"].required = True
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Move"))
        cell = self.maze.get_current_cell()
        self.fields["direction"].choices = cell.get_direction_choices()

    def clean(self):
        cleaned_data = super().clean()
        direction = cleaned_data["direction"]
        direction_authority = Directions.meta[direction]["authority"]
        if hasattr(Directions, f"validate_move_{direction_authority}"):
            getattr(Directions, f"validate_move_{direction_authority}")(cleaned_data)

    def clean_direction(self):
        direction = self.cleaned_data["direction"]
        if not self.maze.can_move(direction):
            raise ValidationError("You cant go that way!", code="invaid_direction")
        return direction

    def save(self, commit=True):
        step = super().save(commit=False)
        step.maze = self.maze
        step.user = self.user
        step.task = self.maze.next_task
        if commit:
            step.save()
        self.maze.move(step.direction)
        return step
