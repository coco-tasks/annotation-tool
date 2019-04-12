# Generated by Django 2.0.5 on 2018-06-07 13:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Annot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coco_id', models.IntegerField(db_index=True, unique=True)),
                ('area', models.FloatField()),
                ('iscrowd', models.BooleanField()),
                ('bbox_x', models.FloatField()),
                ('bbox_y', models.FloatField()),
                ('bbox_w', models.FloatField()),
                ('bbox_h', models.FloatField()),
                ('segmentation', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coco_id', models.IntegerField(db_index=True, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('supercategory', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coco_id', models.IntegerField(db_index=True, unique=True)),
                ('path', models.CharField(max_length=200)),
                ('set_name', models.CharField(max_length=10)),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_example', models.BooleanField(db_index=True, default=False)),
                ('is_done', models.BooleanField(db_index=True, default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotpreferred.Image')),
            ],
        ),
        migrations.CreateModel(
            name='PreferredAnnot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotpreferred.Annot')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotpreferred.Job')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(db_index=True, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('desc', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='job',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotpreferred.Task'),
        ),
        migrations.AddField(
            model_name='job',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='image',
            name='related_tasks',
            field=models.ManyToManyField(to='annotpreferred.Task'),
        ),
        migrations.AddField(
            model_name='annot',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotpreferred.Category'),
        ),
        migrations.AddField(
            model_name='annot',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotpreferred.Image'),
        ),
    ]