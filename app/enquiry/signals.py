import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver

from blacklist.service import is_blacklisted
from enquiry.models import Enquiry, EnquirySource

BLACKLIST_COMMENT = "The contact's email and/or phone number are blacklisted."

logger = logging.getLogger(__name__)


# Calls are checked in the Twilio views, once the caller picks an option.
@receiver(pre_save, sender=Enquiry)
def pre_save_enquiry(sender, instance, **kwargs):
    enquiry = instance
    if enquiry.source != EnquirySource.CONTACT_FORM:
        return

    if is_blacklisted(email=enquiry.email, phone=enquiry.phone):
        logger.info("Enquiry<%s> is blacklisted", enquiry.id)
        enquiry.requires_callback = False
        enquiry.comments = BLACKLIST_COMMENT
