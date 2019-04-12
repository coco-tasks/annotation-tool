import sys

import os
from contextlib import redirect_stdout
from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path
from tqdm import tqdm

from annotpreferred.models import Task, Image

p = Path(settings.BASE_DIR).parent / 'external' / 'coco' / 'PythonAPI'
sys.path.append(str(p))
from pycocotools.coco import COCO


class Command(BaseCommand):
    help = 'Creates the images.'
    sets = ['train', 'test']
    images_root = Path(settings.IMAGES_DIRECTORY)

    def add_arguments(self, parser):
        parser.add_argument('image_list_directory', type=str)
        parser.add_argument('coco_root', type=str)

    def handle(self, *args, **options):
        image_list_directory = Path(options['image_list_directory'])
        coco_root = Path(options['coco_root'])
        assert image_list_directory.exists()
        assert coco_root.exists()

        coco_annot_directory = coco_root / 'annotations'

        for set_name in self.sets:
            coco_dir_name = "train" if set_name == "train" else "val"
            coco_images_directory = coco_root / "{}2014".format(coco_dir_name)
            with redirect_stdout(open(os.devnull, 'w')):
                coco = COCO(str(coco_annot_directory / 'instances_{}2014.json'.format(coco_dir_name)))
            for task in Task.objects.all():
                file_name = image_list_directory / "{}_task_nr_{}_ImgIds.txt".format(set_name, task.number)
                assert file_name.exists()
                with open(str(file_name)) as f:  # Because of python 3.5
                    image_ids = [int(x[:-1]) for x in f.readlines()]

                for iid in tqdm(image_ids):
                    img = coco.loadImgs(iid)[0]

                    coco_image_path = coco_images_directory / img['file_name']
                    assert coco_image_path.exists()
                    image_path = self.images_root / img['file_name']

                    if len(Image.objects.filter(coco_id=iid)) > 0:
                        the_old_image = Image.objects.get(coco_id=iid)
                        the_old_image.related_tasks.add(task)
                    else:
                        # create a symlik to the image in images folder.
                        os.symlink(str(coco_image_path), str(Path(settings.BASE_DIR) / image_path))

                        i = Image(coco_id=iid, path=str(image_path), width=img['width'], height=img['height'],
                                  set_name=set_name)
                        i.save()
                        i.related_tasks.add(task)
