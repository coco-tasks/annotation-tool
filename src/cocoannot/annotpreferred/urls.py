from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('edit/task/<int:task_number>', views.EditJobsView.as_view(), name='edit_list'),
    path('annotate/task/<int:task_number>', views.annotate_next, name='annotate_next'),
    path('annotate/job/<int:job_id>', views.edit_job, name='edit_job'),
    path('annotate/policy/', views.show_policy, name='policy'),
    path('add/jobs/', views.add_jobs, name='add_jobs'),
]
