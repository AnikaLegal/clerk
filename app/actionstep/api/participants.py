from .base import BaseEndpoint


class ParticipantEndpoint(BaseEndpoint):
    """
    Endpoint for participants.
    https://actionstep.atlassian.net/wiki/spaces/API/pages/12648551/Participants
    {
        'id': 11,
        'displayName': 'Segal, Matt',
        'firstName': 'Matt',
        'lastName': 'Segal',
        'phone1Number': None, # Business
        'phone2Number': None, # Mobile
        'phone3Number': None, # Home
        'email': 'matt@anikalegal.com',
    }
    """

    resource = "participants"

    def __init__(self, *args, **kwargs):
        self.participant_types = ParticipantTypeEndpoint(*args, **kwargs)
        self.action_participants = ActionParticipantEndpoint(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def get_or_create(self, first: str, last: str, email: str, phone: str):
        """
        Get participant based on email, or create a new one.
        Returns a participant (see schema above).
        """
        created = False
        client = self.get_by_email(email)
        if not client:
            created = True
            client = self.create(first, last, email, phone)

        return client, created

    def get_by_name(self, first: str, last: str):
        """
        Look up a participant by name.
        Returns a participant (see schema above) or None.
        """
        return super().get({"firstName": first, "lastName": last})

    def get_by_email(self, email: str):
        """
        Look up a participant by email.
        Returns a participant (see schema above) or None.
        """
        return super().get({"email": email})

    def get(self, id: int):
        """
        Look up a participant by id.
        Returns a participant (see schema above) or None.
        """
        return super().get({"id": id})

    def create(self, first: str, last: str, email: str, phone: str):
        """
        Create a new participant.
        Returns a participant (see schema above).
        """
        data = {
            "isCompany": "F",
            "firstName": first,
            "lastName": last,
            "phone2Number": phone,
            "email": email,
        }
        return super().create(data)

    def set_action_participant(
        self, action_id: int, client_id: int, participant_name: str
    ):
        """
        Set a user as a type of participant on an action.
        Returns an "Action participant" (see ActionParticipantEndpoint schema)
        """
        participant_type = self.participant_types.get_for_name(participant_name)
        participant_type_id = participant_type["id"]
        resp_data = self.action_participants.create(
            action_id, client_id, participant_type_id
        )
        return resp_data


class ParticipantTypeEndpoint(BaseEndpoint):
    """
    Endpoint for participant types.
    https://actionstep.atlassian.net/wiki/spaces/API/pages/21135513/Participant+Types
    {
        'id': 60,
        'name': 'Purchasers_Conveyancer',
        'displayName': 'Purchasers Conveyancer',
        'description': 'Solicitor or conveyancer acting for the purchaser',
        'isBaseParticipantType': 'F',
        'companyFlag': None,
        'taxNumberAlias': None
    }
    """

    resource = "participanttypes"

    def get_for_name(self, name: str):
        """
        Gets a participant type by name.
        Returns a participant type (see schema above) or None
        """
        return super().get({"name": name})

    def get(self, id: int):
        """
        Gets a participant type by id.
        Returns a participant type (see schema above) or None
        """
        return super().get({"id": id})


class ActionParticipantEndpoint(BaseEndpoint):
    """
    Endpoint for action participants.
    https://actionstep.atlassian.net/wiki/spaces/API/pages/21135482/Action+Participants
    {
        # actionId--participantTypeId--participantId
        'id': '2--27--11',
        'participantNumber': 1,
        'links': {'action': '2', 'participant': '11'}
    }
    NB key "type" added into "links"
    """

    resource = "actionparticipants"

    def create(self, action_id: str, participant_id: int, participant_type_id: int):
        """
        Creates an action participant.
        Returns an action participant (see schema above)
        """
        data = {
            "links": {
                "action": action_id,
                "participant": participant_id,
                "participantType": participant_type_id,
            }
        }
        return super().create(data)

    def list_for_action(self, action_id: int):
        """
        Lists all action participants present on an action.
        Returns list of action participants (see schema above)
        """

        data = super().list({"action": action_id})
        return [self.parse_participant_type(act_p) for act_p in data]

    def parse_participant_type(self, act_p: dict):
        p_type_id = act_p["id"].split("-")[2]
        return {**act_p, "links": {**act_p["links"], "type": p_type_id}}
