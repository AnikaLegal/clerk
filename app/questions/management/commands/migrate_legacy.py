import os

from django.core.management.base import BaseCommand
from django.conf import settings

from actionstep.api import ActionstepAPI
from actionstep.constants import ActionType, Participant
from questions.models import Submission

PREFIX_LOOKUP = {"REPAIRS": "R", "COVID": "C"}
ACTION_TYPE_LOOKUP = {"REPAIRS": ActionType.REPAIRS, "COVID": ActionType.COVID}


class Command(BaseCommand):
    help = 'Map documents to users in Actionstep database'

    # Change this to the directory of the files
    base_dir = "./questions/management/commands/legacy_data"

    # Change this to be right before first entry on Actionstep
    timestamp = "2000-11-21T15:01:36+13:00"

    def get_submission(self, firstname, lastname, case_topic):
        all_submissions = Submission.objects.filter(complete=True, is_case_sent=False)
        client_data = {}
        for s in all_submissions:
            if s.topic != case_topic:
                continue

            for field in s.answers:
                field_match = (field['name'] == "CLIENT_NAME")
                answer_match = (field["answer"] == f"{firstname} {lastname}")

                if field_match and answer_match:
                    for d in s.answers:
                        client_data[d['name']] = d['answer']
                    return s, client_data
        return None, client_data


    def upload(self, case_type, item):
        api = ActionstepAPI()
        path = os.path.join(self.base_dir, case_type, item)
        if not os.path.isdir(path):
            return

        # Grab important metadata from directory name
        print(f"Uploading data from {item}...")
        tokens = item.split()
        fileref_name, (firstname, lastname) = tokens[0], tokens[2:4]
    
        # Retrieve matching client data from clerk submissions
        submission, client_data = self.get_submission(
            firstname, lastname, case_type
        )
        if not submission:
            print(f"Can't find submission for {firstname} {lastname}!")
            print(f"Creating new client...")
            participant_data = api.participants.create(firstname, lastname, "", "")
        else:
            # Test if the participant exists in Actionstep
            participant_data, created = api.participants.get_or_create(
                firstname, lastname, client_data['CLIENT_EMAIL'], client_data['CLIENT_PHONE']
            )
            if created:
                print(f"Created participant {client_data['CLIENT_NAME']}.")
            else:
                print(f"{client_data['CLIENT_NAME']} already exists.")

        # Procedures from _send_submission_actionstep() function
        owner_email = settings.ACTIONSTEP_SETUP_OWNERS[case_type]
        owner_data = api.participants.get_by_email(owner_email)
        
        # Create a new matter for the participant
        submission_id = "LEGACYCASE"
        if submission:
            submission_id = submission.pk

        action_type_name = ACTION_TYPE_LOOKUP[case_type]
        action_type_data = api.actions.action_types.get_for_name(action_type_name)
        action_type_id = action_type_data["id"]
        action_data = api.actions.create(
            submission_id=submission_id,
            action_type_id=action_type_id,
            action_name=f"{firstname} {lastname}",
            file_reference=fileref_name,
            participant_id=owner_data["id"],
            timestamp=self.timestamp
        )
        action_id = action_data["id"]
        client_id = participant_data["id"]
        api.participants.set_action_participant(action_id, client_id, Participant.CLIENT)

        # Load all the bytes of files that need to be uploaded
        all_files = []
        for root, folders, files in os.walk(path):
            for filename in files:
                subpath = os.path.join(root, filename)
                with open(subpath, 'rb') as file:
                    # TODO: Test if API creates folders on Actionstep
                    # to preserve file hierarchy    
                    all_files.append({
                        "name" : filename,
                        "bytes" : file.read(),
                        "target_folder" : "Client"
                    })

        # Upload and attach files to the matter
        for f in all_files:
            file_data = api.files.upload(f["name"], f["bytes"])
            api.files.attach(f["name"], file_data["id"], action_id, f["target_folder"])
        
        # Update existing submission
        if submission:
            Submission.objects.filter(pk=submission.pk).update(is_case_sent=True)

        
    def handle(self, *args, **options):
        for case_type in os.listdir(self.base_dir):
            # case_type should match a CaseTopic
            subpath = os.path.join(self.base_dir, case_type)
            for item in sorted(os.listdir(subpath), key=lambda s: s.split()[0]):
                self.upload(case_type, item)