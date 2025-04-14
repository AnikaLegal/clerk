from accounts.models import User
from core.models import Service
from core.models.service_event import ServiceEvent, EventType


def on_service_create(service: Service, user: User):
    ServiceEvent.objects.create(event_type=EventType.CREATE, service=service, user=user)


def on_service_update(service: Service, user: User):
    ServiceEvent.objects.create(event_type=EventType.UPDATE, service=service, user=user)


def on_service_delete(service: Service, user: User):
    ServiceEvent.objects.create(event_type=EventType.DELETE, service=service, user=user)
