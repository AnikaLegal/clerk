import os
import sys
from concurrent.futures import wait, ThreadPoolExecutor, FIRST_EXCEPTION
import traceback

from django.core.management.base import BaseCommand
from django.conf import settings

from actionstep.api import ActionstepAPI
from actionstep.constants import ActionType, Participant
from questions.models import Submission

PREFIX_LOOKUP = {"REPAIRS": "R", "COVID": "C"}
ACTION_TYPE_LOOKUP = {"REPAIRS": ActionType.REPAIRS, "COVID": ActionType.COVID}


class Command(BaseCommand):
    help = "Map documents to users in Actionstep database"

    # Change this to the directory of the files
    base_dir = "legacy_data"

    # Change this to be right before first entry on Actionstep
    timestamp = "2020-04-14T15:00:00+00:00"

    def handle(self, *args, **options):
        thread_args = []
        for case_type in ["REPAIRS", "COVID"]:
            subpath = os.path.join(self.base_dir, case_type)
            for item in sorted(os.listdir(subpath), key=lambda s: s.split()[0]):
                thread_args.append([case_type, item])

        # for thread_arg in thread_args:
        #     self._upload(*thread_arg)

        # return

        with ThreadPoolExecutor(max_workers=24) as executor:
            futures = []
            for thread_arg in thread_args:
                print("Dispatching", *thread_arg)
                future = executor.submit(self.upload, *thread_arg)
                futures.append(future)

            print("All upload tasks dispatched")
            wait(futures, timeout=3600, return_when=FIRST_EXCEPTION)
            print("All upload tasks finished")
            for idx, future in enumerate(futures):
                thread_arg = thread_args[idx]
                try:
                    future.result()
                    print("Success for", *thread_arg)
                except Exception as e:
                    print("Exception for", *thread_arg, "\n", e)

    def upload(self, case_type, item):
        try:
            self._upload(case_type, item)
        except Exception:
            # raise StandardError(f"Error occurred. Original traceback is\n{trace_str}\n")
            raise sys.exc_info()[0](traceback.format_exc())

    def _upload(self, case_type, item):
        api = ActionstepAPI()
        path = os.path.join(self.base_dir, case_type, item)
        assert os.path.isdir(path), path

        # Grab important metadata from directory name
        print(f"Uploading data from {item}...")
        tokens = item.split()
        fileref_name, (firstname, lastname) = tokens[0], tokens[2:4]
        if not fileref_name and firstname and lastname:
            print("Skipping case record incomplete data in folder name:", item)
            return

        # Retrieve matching client data from clerk submissions
        submission, client_data = self.get_submission(firstname, lastname, case_type)
        if not submission:
            print(f"Can't find submission for {firstname} {lastname}!")
            participant_data = api.participants.get_by_name(firstname, lastname)
            if participant_data:
                print(f"Found existing client for {firstname} {lastname}")
            else:
                print(f"Creating new client for {firstname} {lastname}")
                participant_data = api.participants.create(firstname, lastname, "", "")
        else:
            # Check that we haven't already synced this submission.
            if submission.is_case_sent:
                print(f"Submission {submission.pk} has already been synced to Actionstep.")
                return

            # Test if the participant exists in Actionstep
            participant_data, created = api.participants.get_or_create(
                firstname, lastname, client_data["CLIENT_EMAIL"], client_data["CLIENT_PHONE"]
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

        action_data = api.actions.get_by_ref(fileref_name)
        if not action_data:
            action_data = api.actions.create(
                submission_id=submission_id,
                action_type_id=action_type_id,
                action_name=f"{firstname} {lastname}",
                file_reference=fileref_name,
                participant_id=owner_data["id"],
                timestamp=self.timestamp,
            )

        action_id = action_data["id"]
        client_id = participant_data["id"]

        existing_participants = api.participants.action_participants.list_for_action(action_id)
        is_participant_present = False
        for existing_participant in existing_participants:
            if str(client_id) == str(existing_participant["links"]["participant"]):
                is_participant_present = True
                break

        if not is_participant_present:
            api.participants.set_action_participant(action_id, client_id, Participant.CLIENT)

        FILENAMES_TO_IGNORE = [
            "Student Manual.docx",
            "Precedent -",
            "Practical Legal Training Guide",
            "[R####]",
            "R[####]",
            "[RXXXX]",
        ]

        # Load all the bytes of files that need to be uploaded
        all_files_data = []
        for root, folders, files in os.walk(path):
            for filename in files:
                if any([f in filename for f in FILENAMES_TO_IGNORE]):
                    continue

                subpath = os.path.join(root, filename)
                with open(subpath, "rb") as file:
                    file_data = {"name": filename, "bytes": file.read(), "target_folder": "Client"}
                    all_files_data.append(file_data)

        # Upload and attach files to the matter
        for f in all_files_data:
            file_data = api.files.upload(f["name"], f["bytes"])
            api.files.attach(f["name"], file_data["id"], action_id, f["target_folder"])

        # Update existing submission
        if submission:
            Submission.objects.filter(pk=submission.pk).update(is_case_sent=True)

    def get_submission(self, firstname, lastname, case_topic):
        all_submissions = Submission.objects.filter(complete=True, is_case_sent=False)
        client_data = {}
        for s in all_submissions:
            if s.topic != case_topic:
                continue

            for field in s.answers:
                field_match = field["name"] == "CLIENT_NAME"
                if field_match:
                    answer_match = field.get("answer").lower() == f"{firstname} {lastname}".lower()
                    if answer_match:
                        for d in s.answers:
                            client_data[d["name"]] = d.get("answer")
                        return s, client_data

        return None, client_data
