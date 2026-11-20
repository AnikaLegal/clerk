import factory

from core.factories import TimestampedModelFactory
from core.models.issue import CaseTopic
from enquiry.models import Callback, Enquiry, EnquirySource


class CallEnquiryFactory(TimestampedModelFactory):
    class Meta:
        model = Enquiry

    source = EnquirySource.CALL
    phone = factory.Faker("numerify", text="+614########")
    topic = factory.Iterator([value for value, _ in CaseTopic.CHOICES])


class ContactEnquiryFactory(TimestampedModelFactory):
    class Meta:
        model = Enquiry

    source = EnquirySource.CONTACT_FORM
    name = factory.Faker("name")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    requires_callback = True


class CallbackFactory(TimestampedModelFactory):
    class Meta:
        model = Callback

    enquiry = factory.SubFactory(CallEnquiryFactory)
    is_answered = True
    purpose = factory.Faker("sentence")
    summary = factory.Faker("sentence")
