from django.contrib.auth.models import User
from django.db import models
from markdownx.models import MarkdownxField


class Category(models.Model):
    """
    Represents a COCO category
    """
    coco_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=50)
    supercategory = models.CharField(max_length=50)

    def __str__(self):
        return "Category {}: {} ({})".format(self.coco_id, self.name, self.supercategory)


class Task(models.Model):
    """
    Represents a Task
    """
    number = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=50)
    desc = models.TextField(blank=True, null=True)
    desc_image = models.ImageField(upload_to='task_images', blank=True, default=None, null=True)

    def __str__(self):
        return "Task {}: {}".format(self.number, self.name)


class Image(models.Model):
    """
    Represents an image in the dataset
    """
    coco_id = models.IntegerField(unique=True, db_index=True)
    path = models.CharField(max_length=200)
    set_name = models.CharField(max_length=10)
    width = models.IntegerField()
    height = models.IntegerField()
    related_tasks = models.ManyToManyField(Task)

    def __str__(self):
        return "Image {}".format(self.coco_id)


class Annot(models.Model):
    """
    Represents a COCO annotation for instances.
    """
    coco_id = models.IntegerField(unique=True, db_index=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    area = models.FloatField()
    iscrowd = models.BooleanField()
    bbox_x = models.FloatField()
    bbox_y = models.FloatField()
    bbox_w = models.FloatField()
    bbox_h = models.FloatField()
    segmentation = models.TextField()  # I am going to store the segmentation as a text field.

    # I will convert it into json on demand.

    def __str__(self):
        return "Annot {} ({})".format(self.coco_id, self.category)

    def get_bbox(self):
        return [self.bbox_x, self.bbox_y, self.bbox_w, self.bbox_h]

    def set_bbox(self, bbox):
        bbox = tuple(bbox)
        self.bbox_x, self.bbox_y, self.bbox_w, self.bbox_h = bbox


class Job(models.Model):
    """
    Represents a job (an annotation of the preferred objects) for an image by a user.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, db_index=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    is_example = models.BooleanField(default=False, db_index=True)
    is_done = models.BooleanField(default=False, db_index=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Job[task={}, image={}, user={}]".format(self.task.name, self.image_id, self.user.first_name)


class PreferredAnnot(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, db_index=True)
    annot = models.ForeignKey(Annot, on_delete=models.CASCADE, db_index=True)


class AnnotationPolicy(models.Model):
    policy = MarkdownxField()
