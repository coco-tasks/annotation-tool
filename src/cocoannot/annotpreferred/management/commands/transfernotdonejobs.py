from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from tqdm import tqdm

from annotpreferred.models import Job, Task


class Command(BaseCommand):
    help = 'Transfer not done jobs of a user to another user.'

    def add_arguments(self, parser):
        parser.add_argument('task_number', type=int)
        parser.add_argument('from_user', type=str)
        parser.add_argument('to_user', type=str)

    def handle(self, *args, **options):
        task_number = options['task_number']
        from_username = options['from_user']
        to_username = options['to_user']

        from_user = User.objects.get(username=from_username)
        to_user = User.objects.get(username=to_username)
        task = Task.objects.get(number=task_number)

        for j in tqdm(Job.objects.filter(user=from_user, task=task, is_done=False)):
            j.user = to_user
            j.save()
