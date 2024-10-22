import logging

from accounts.models import User
from core.services.service import ServiceChangeType, ServiceDict, update_timeline

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
    update_timeline(type, service, user)
