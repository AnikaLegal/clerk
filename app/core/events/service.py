import logging

from accounts.models import User
from core.services.service import ServiceChangeType, ServiceDict, update_timeline
from django_q.tasks import async_task, result

logger = logging.getLogger(__name__)


def on_service_create(service: ServiceDict, user: User):
    handle_service_change(
        type=ServiceChangeType.CREATE,
        service=service,
        user=user,
    )


def on_service_update(service: ServiceDict, user: User):
    handle_service_change(
        type=ServiceChangeType.UPDATE,
        service=service,
        user=user,
    )


def on_service_delete(service: ServiceDict, user: User):
    handle_service_change(
        type=ServiceChangeType.DELETE,
        service=service,
        user=user,
    )


def handle_service_change(type: ServiceChangeType, service: ServiceDict, user: User):
    # Wait on the result for a little bit so we can update the frontend UI
    # immediately. We could, of course, just run the task synchronously, i.e.
    # without using async_task, but then if the task fails it is difficult to
    # rerun the same task again.
    task_id = async_task(update_timeline, type, service, user.pk)
    result(task_id, wait=2000)
