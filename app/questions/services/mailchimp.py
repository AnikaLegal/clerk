from mailchimp3 import MailChimp

from django.conf import settings
from django.utils import timezone

from questions.models import Submission


def remind_incomplete():
    """master function finding clients and sending reminder emails to them"""

    # find COVID clients and send reminder
    covid_clients = find_clients(topic='COVID')
    send_email(clients=covid_clients, list_id='', workflow_id='', email_id='')

    # find REPAIRS clients and send reminder
    repairs_clients = find_clients(topic='REPAIRS')
    send_email(clients=repairs_clients, list_id='', workflow_id='', email_id='')


def find_clients(topic):
    """find and return list of clients according to business criteria"""
    
    # define the boundaries of our time range
    two_days_ago = timezone.now() - timezone.timedelta(days=2)
    two_weeks_ago = timezone.now() - timezone.timedelta(days=14)

    # find submissions according to conditions specified
    submissions = Submission.objects.filter(complete=False, is_reminder_sent=False, topic=topic,
                            created_at__gt=two_weeks_ago, created_at__lt=two_days_ago)
    
    # generate list of clients with emails inside of submissions
    clients = []

    for submission in submissions:
        for answer in submission.answers:
            if answer["name"] == 'CLIENT_EMAIL' and answer["answer"]:
                client = (submission, answer["answer"])
                clients.append(client)
    
    return clients

            
def send_email(clients, list_id, workflow_id, email_id):
    """send reminder email via MailChimp API"""
    
    mailchimp = MailChimp(settings.MAILCHIMP_API_KEY)

    for submission, email in clients:
        # mark as sent reminder
        submission.is_reminder_sent = True
        submission.save()
        # add formatting
        person = {'email_address': email, 'status': 'subscribed'}
        # add person to list
        mailchimp.lists.members.create(list_id=list_id, data=person)
        # send person email
        mailchimp.automations.emails.queues.create(workflow_id=workflow_id,
                            email_id=email_id, data=person)