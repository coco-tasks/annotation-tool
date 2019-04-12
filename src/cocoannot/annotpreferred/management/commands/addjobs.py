from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from tqdm import tqdm

from annotpreferred.models import Image, Task, Job


class Command(BaseCommand):
    help = 'Add jobs for a specific user to annotate a task.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('task_number', type=int)

    def handle(self, *args, **options):
        username = options['username']
        user = User.objects.get(username=username)

        task_number = options['task_number']
        task = Task.objects.get(number=task_number)

        for img in tqdm(Image.objects.filter(related_tasks=task)):
            j = Job(task=task, image=img, user=user)
            j.save()
