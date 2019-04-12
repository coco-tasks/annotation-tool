import json
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from tqdm import tqdm

from annotpreferred.models import Image, Task, Job, Annot, PreferredAnnot


class Command(BaseCommand):
    help = 'Create raw JSON files for evaluation.'

    def add_arguments(self, parser):
        parser.add_argument('usernames', nargs='+', type=str)
        parser.add_argument('--signature', type=str)

    def handle(self, *args, **options):
        usernames = options['usernames']
        signature = options['signature']

        if not signature:
            date_joined = datetime.now()
            formatted_datetime = date_joined.strftime("%Y-%m-%d-%H-%M-%S")
            signature = "{}_{}".format("_".join(usernames), formatted_datetime)

        users = []
        for un in usernames:
            users.append(User.objects.get(username=un))

        task_numbers = Job.objects.filter(user__in=users).values_list('task__number', flat=True).distinct()

        labels_per_task = {}

        for tn in tqdm(task_numbers):
            task = Task.objects.get(number=tn)
            # find the list of images that are annotated by all users
            image_sets = []

            for u in users:
                done_jobs = Job.objects.filter(user=u, task=task, is_done=True)
                img_set = set([j.image.coco_id for j in done_jobs])
                image_sets.append(img_set)

            images_annotated_by_all = set.intersection(*image_sets)
            labels_per_image = {}

            # for each image find the annotations and whether they are first choice or not.
            for img_coco_id in images_annotated_by_all:
                img = Image.objects.get(coco_id=img_coco_id)

                img_annots = Annot.objects.filter(image=img, iscrowd=False)

                user_preferred_annots = []
                # find preferred_annots for each user
                for u in users:
                    this_users_preferred_annots = []

                    this_users_job_for_this_image = Job.objects.get(user=u, task=task, image=img)
                    tupa = PreferredAnnot.objects.filter(job=this_users_job_for_this_image).all()
                    this_users_preferred_annots.extend([pa.annot.coco_id for pa in tupa])

                    user_preferred_annots.append(this_users_preferred_annots)

                annot_labels_per_user = {}

                for i in range(len(users)):
                    current_label = {}
                    for ia in img_annots:
                        if ia.coco_id in user_preferred_annots[i]:
                            current_label[ia.coco_id] = 1
                        else:
                            current_label[ia.coco_id] = 0
                    annot_labels_per_user[users[i].username] = current_label

                labels_per_image[img_coco_id] = annot_labels_per_user
            labels_per_task[tn] = labels_per_image

        with open('raw_json_file_{}.json'.format(signature), 'w') as f:
            json.dump(labels_per_task, f)
