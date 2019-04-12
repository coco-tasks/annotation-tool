import os
import sys

from contextlib import redirect_stdout
from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path
from tqdm import tqdm

from annotpreferred.models import Annot, Image, Category

p = Path(settings.BASE_DIR).parent / 'external' / 'coco' / 'PythonAPI'
sys.path.append(str(p))
from pycocotools.coco import COCO


class Command(BaseCommand):
    help = 'Creates the initial annotations.'
    sets = ['train', 'test']

    def add_arguments(self, parser):
        parser.add_argument('coco_root', type=str)

    def handle(self, *args, **options):
        coco_root = Path(options['coco_root'])
        assert coco_root.exists()

        coco_annot_directory = coco_root / 'annotations'

        s = 0
        for set_name in self.sets:
            coco_dir_name = "train" if set_name == "train" else "val"
            with redirect_stdout(open(os.devnull, 'w')):
                coco = COCO(str(coco_annot_directory / 'instances_{}2014.json'.format(coco_dir_name)))

            for img in tqdm(Image.objects.filter(set_name=set_name)):
                iid = img.coco_id
                if len(img.annot_set.all()) == 0:
                    s += 1
                    for coco_annot in coco.loadAnns(coco.getAnnIds(imgIds=iid)):
                        cat = Category.objects.get(coco_id=int(coco_annot['category_id']))
                        iscrowd = True if coco_annot['iscrowd'] else False
                        a = Annot(coco_id=int(coco_annot['id']), image=img, category=cat,
                                  area=float(coco_annot['area']), iscrowd=iscrowd,
                                  segmentation=str(coco_annot['segmentation']))
                        a.set_bbox(coco_annot['bbox'])
                        a.save()
        print(s)
