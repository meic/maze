from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Step


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ["direction"]

    def __init__(self, *args, maze=None, user=None, **kwargs):
        self.maze = maze
        self.user = user
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Move"))
        cell = self.maze.get_current_cell()
        self.fields["direction"].choices = cell.reduce_choices(
            self.fields["direction"].choices
        )

    def clean_direction(self):
        direction = self.cleaned_data["direction"]
        if not self.maze.can_move(direction):
            raise ValidationError("You cant go that way!", code="invaid_direction")
        return direction

    def save(self, commit=True):
        step = super().save(commit=False)
        step.maze = self.maze
        step.user = self.user
        if commit:
            step.save()
        self.maze.move(step.direction)
        return step
