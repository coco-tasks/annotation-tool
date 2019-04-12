import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from markdownx.utils import markdownify

from .models import Task, Job, Annot, PreferredAnnot, AnnotationPolicy, Image
from .forms import AddJobsForm


@login_required
def index(request):
    all_count = Count('job', filter=Q(job__user=request.user))
    remaining_count = Count('job', filter=Q(job__user=request.user, job__is_done=False))
    done_count = Count('job', filter=Q(job__user=request.user, job__is_done=True))
    task_jobs = Task.objects.annotate(all_count=all_count, remaining_count=remaining_count,
                                      done_count=done_count).order_by('number')

    hiwis = User.objects.filter()

    for hiwi in hiwis:
        all_count = Count('job', filter=Q(job__user=hiwi))
        remaining_count = Count('job', filter=Q(job__user=hiwi, job__is_done=False))
        done_count = Count('job', filter=Q(job__user=hiwi, job__is_done=True))
        hiwi_tasks = Task.objects.annotate(all_count=all_count, remaining_count=remaining_count,
                                           done_count=done_count).order_by('number')
        hiwi.tasks = hiwi_tasks

    context = {'is_superuser': request.user.is_superuser, 'to_annotate': task_jobs, 'hiwis': hiwis}
    return render(request, 'home.html', context)


@login_required
def annotate_next(request, task_number):
    # get the jobs of the current user for task_number
    # sort by job_id and select the first one.
    job = Job.objects.filter(user=request.user, task__number=task_number, is_done=False).order_by('?').first()
    if job:
        # redirect to that url.
        return redirect('edit_job', job_id=job.id)
    else:
        # no more jobs left
        return redirect('home')


@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if job.user != request.user:
        return HttpResponseForbidden('This is not your job.')
    annots = []
    all_annots = job.image.annot_set.all()

    sorted_annots = sorted(all_annots, key=lambda x: (x.bbox_h * x.bbox_w), reverse=True)
    for annot in sorted_annots:
        segments = annot.segmentation
        try:
            segments = json.loads(segments)
        except json.decoder.JSONDecodeError:
            continue
        annot.segmentation = []
        for segment in segments:
            current_segment = ["{},{}".format(segment[0], segment[1])]
            # The following for loop is because of a relatively crazy format of the coco annotations.
            for m in range(0, len(segment) - 2, 2):
                current_segment.append("{},{}".format(segment[m + 2], segment[m + 3]))
            annot.segmentation.append(" ".join(current_segment))
        annots.append(annot)

    if request.method == "GET":
        pacoco_ids = []
        if job.is_done:
            pas = PreferredAnnot.objects.filter(job=job)
            for pa in pas:
                pacoco_ids.append('{}'.format(pa.annot.coco_id))

        skip_job = Job.objects.filter(~Q(id=job.id), user=request.user, task__number=job.task.number,
                                      is_done=False).order_by('?').first()
        if skip_job:
            skip_job_id = skip_job.id
        else:
            skip_job_id = None
        context = {'job': job, 'annots': annots, 'preferred_objects': ",".join(pacoco_ids), 'is_done': job.is_done,
                   'skip_job': skip_job_id}
        return render(request, 'annotate/edit_job.html', context=context)
    elif request.method == "POST":
        if "save" in request.POST.keys():
            tocontinue = False
        elif "save-and-continue" in request.POST.keys():
            tocontinue = True
        else:
            return HttpResponseBadRequest()
        # first I have to remove all previously saved preferred objects.
        pas = PreferredAnnot.objects.filter(job=job)
        pas.delete()

        if len(request.POST.get('preferred-object-input')) > 0:
            preferred_objects = [int(x) for x in request.POST.get('preferred-object-input').split(',')]
            for po in preferred_objects:
                a = Annot.objects.get(coco_id=po)

                pa = PreferredAnnot(job=job, annot=a)
                pa.save()
                job.is_done = True
                job.save()
        else:
            is_empty = request.POST.get('is-empty') == 'on'
            if is_empty:
                job.is_done = True
                job.save()
            else:
                return HttpResponseBadRequest()
        if tocontinue:
            return redirect('annotate_next', job.task.number)
        else:
            return redirect('edit_job', job.id)


class EditJobsView(ListView, LoginRequiredMixin):
    paginate_by = 25
    template_name = 'annotate/edit_list.html'
    model = Job

    def get_queryset(self):
        task_number = self.kwargs['task_number']
        user = self.request.user
        return Job.objects.filter(user=user, task__number=task_number, is_done=True).order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_name'] = Task.objects.get(number=self.kwargs['task_number']).name
        return context


@login_required
def show_policy(request):
    policy = AnnotationPolicy.objects.get()
    policy_text = markdownify(policy.policy)

    return render(request, 'annotate/policy.html', {'policy': policy_text})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_jobs(request):
    if request.method == 'POST':
        form = AddJobsForm(request.POST)

        if form.is_valid():
            if "submit-all" in request.POST.keys():
                do_all = True
            elif "submit-test" in request.POST.keys():
                do_all = False
            else:
                return HttpResponseBadRequest()
            t = 0
            for user in form.cleaned_data['users']:
                for task in form.cleaned_data['tasks']:
                    it = 0
                    for img in Image.objects.filter(related_tasks=task):
                        t += 1
                        it += 1
                        j = Job(user=user, task=task, image=img)
                        j.save()
                        if not do_all and it >= 10:
                            break
            my_response = '{} Jobs added!'.format(t)
            form = AddJobsForm()
        else:
            my_response = 'There are problems!'
    else:
        my_response = None
        form = AddJobsForm()

    return render(request, 'add_jobs.html', {'form': form, 'my_response': my_response})
