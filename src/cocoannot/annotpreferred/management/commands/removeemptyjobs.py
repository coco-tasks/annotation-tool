from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from tqdm import tqdm

from annotpreferred.models import Image, Task, Job


class Command(BaseCommand):
    def handle(self, *args, **options):
        s = 0
        for job in tqdm(Job.objects.filter(is_done=True)):
            img: Image = job.image
            len_annots = len(img.annot_set.all())
            if len_annots == 0:
                job.is_done = False
                job.save()
                s += 1
        print(s)
