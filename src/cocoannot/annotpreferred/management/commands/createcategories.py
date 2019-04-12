import json
from django.core.management.base import BaseCommand
from pathlib import Path

from annotpreferred.models import Category


class Command(BaseCommand):
    help = 'Creates the initial categories from a coco annotations file.'

    def add_arguments(self, parser):
        parser.add_argument('coco_annot_path', type=str)

    def handle(self, *args, **options):
        coco_annot_path = Path(options['coco_annot_path'])
        assert coco_annot_path.exists()
        with open(str(coco_annot_path)) as f:  # Because of python 3.5
            coco_annot = json.load(f)

        for cat in coco_annot['categories']:
            c = Category(coco_id=str(cat['id']), name=cat['name'], supercategory=cat['supercategory'])
            c.save()
            self.stdout.write(self.style.SUCCESS(cat['name']))
