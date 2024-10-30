from core.models import ServiceEvent
from core.services.service import update_timeline
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task, result


@receiver(post_save, sender=ServiceEvent)
def post_save_service_event(sender, instance: ServiceEvent, **kwargs):
    # Wait on the result for a little bit so we can update the frontend UI
    # immediately. We could, of course, just run the task synchronously, i.e.
    # without using async_task, but then if the task fails it is difficult to
    # rerun the same task again.
    task_id = async_task(update_timeline, instance.pk)
    result(task_id, wait=2000)
