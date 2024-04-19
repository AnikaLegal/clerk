import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_q.tasks import async_task

from core.models import Issue
from task.models.trigger import TaskTrigger, TaskTriggerEvent


logger = logging.getLogger(__name__)
