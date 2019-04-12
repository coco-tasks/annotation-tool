import json
from django.core.management.base import BaseCommand
from pathlib import Path

from annotpreferred.models import Task, Category


class Command(BaseCommand):
    help = 'Creates the initial tasks (without description).'

    def add_arguments(self, parser):
        parser.add_argument('tasks_file_path', type=str)

    def handle(self, *args, **options):
        tasks_file_path = Path(options['tasks_file_path'])
        assert tasks_file_path.exists()
        with open(str(tasks_file_path)) as f:  # Because of python 3.5
            tasks_file = json.load(f)

        for task_number_str in tasks_file:
            t = Task(name=tasks_file[task_number_str]['name'], number=int(task_number_str))
            t.save()
            self.stdout.write(self.style.SUCCESS(task_number_str))
