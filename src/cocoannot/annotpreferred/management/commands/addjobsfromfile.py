from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from tqdm import tqdm
from pathlib import Path

from annotpreferred.models import Image, Task, Job


class Command(BaseCommand):
    help = 'Add jobs for a specific user to annotate a task.'

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str)

    def handle(self, *args, **options):
        file_name = Path(options['file_name'])

        assert file_name.exists()

        with open(str(file_name)) as f:
            for line in tqdm(f):
                parts = line.split()
                assert len(parts) == 3

                username = parts[0]
                image_coco_id = int(parts[1])
                task_number = int(parts[2])

                user = User.objects.get(username=username)
                image = Image.objects.get(coco_id=image_coco_id)
                task = Task.objects.get(number=task_number)

                assert task in image.related_tasks.all()

                job = Job(task=task, image=image, user=user)
                job.save()
