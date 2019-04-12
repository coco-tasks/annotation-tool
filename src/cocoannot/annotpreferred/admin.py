from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from .models import *


def undo_job(modeladmin, request, queryset):
    for obj in queryset:  # type: Job
        obj.is_done = False
        for pa in obj.preferredannot_set.all():  # type: PreferredAnnot
            pa.delete()
        obj.save()


undo_job.short_discription = "Undo Job"


class JobAdmin(admin.ModelAdmin):
    def get_username(self, obj: Job):
        return obj.user.username

    get_username.short_description = "HiWi"
    get_username.admin_order_field = 'user'

    def get_image_coco_id(self, obj: Job):
        return obj.image.coco_id

    get_image_coco_id.short_description = "Image ID"
    get_image_coco_id.admin_order_field = 'image'

    def get_task_number(self, obj: Job):
        return obj.task.number

    get_task_number.short_description = "Task Number"
    get_task_number.admin_order_field = 'task'

    list_display = ('id', 'get_username', 'get_task_number', 'get_image_coco_id', 'is_done', 'is_example')
    list_filter = ['is_done', 'task', 'user', 'is_example']
    actions = [undo_job]

    def get_search_results(self, request, queryset, search_term):
        # queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        try:
            search_term_as_int = int(search_term)
        except ValueError:
            pass
        else:
            queryset = self.model.objects.filter(image__coco_id=search_term_as_int)
        return queryset, False

    search_fields = ['id']


admin.site.register(Category)
admin.site.register(Task)
admin.site.register(Image)
admin.site.register(Annot)
admin.site.register(Job, JobAdmin)
admin.site.register(PreferredAnnot)
admin.site.register(AnnotationPolicy, MarkdownxModelAdmin)
