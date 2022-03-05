import argparse
import csv

from django.core.management.base import BaseCommand, CommandError

from maze.models import Task


class Command(BaseCommand):
    help = "Import Tasks from CSV"

    DIFFICULTY_MAP = {
        "easy": Task.EASY,
        "medium": Task.MEDIUM,
        "hard": Task.HARD,
    }

    def add_arguments(self, parser):
        parser.add_argument("input_file", type=argparse.FileType("r"))

    def handle(self, *args, **options):
        reader = csv.DictReader(options["input_file"])
        for row in reader:
            try:
                difficulty_str = row["difficulty"]
                description = row["task"]
            except KeyError:
                raise CommandError("CSV columns 'task' or 'difficulty' not found.")
            difficulty = self.DIFFICULTY_MAP.get(difficulty_str.lower())
            if not difficulty:
                raise CommandError(f"Difficulty not recognised {difficulty_str}")
            Task.objects.update_or_create(
                description=description, defaults={"difficulty": difficulty}
            )
