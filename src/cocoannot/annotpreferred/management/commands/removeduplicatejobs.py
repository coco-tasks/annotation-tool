from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from tqdm import tqdm
from collections import defaultdict

from annotpreferred.models import Image, Task, Job


class Command(BaseCommand):
    help = 'remove duplicate jobs of a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        username = options['username']
        user = User.objects.get(username=username)

        all_tasks = Task.objects.all()

        for task in tqdm(all_tasks):
            user_task_jobs = Job.objects.filter(user=user, task=task)
            user_task_jobs_per_image = defaultdict(list)
            if len(user_task_jobs) > 0:
                for job in user_task_jobs:
                    user_task_jobs_per_image[job.image].append(job)

                for image in user_task_jobs_per_image:
                    current_jobs = user_task_jobs_per_image[image]

                    if len(current_jobs) > 1:
                        if current_jobs[0].is_done and current_jobs[1].is_done:
                            current_jobs[1].delete()
                        elif current_jobs[0].is_done:
                            current_jobs[1].delete()
                        elif current_jobs[1].is_done:
                            current_jobs[0].delete()
                        elif not current_jobs[0].is_done and not current_jobs[1].is_done:
                            current_jobs[0].delete()
                        else:
                            raise Exception("Something is wrong!")
