class ActionType:
    """
    Action / matter type names
    """

    GENERAL = "General"
    REPAIRS = "Residential Repairs"
    BONDS = "Bonds Recovery"
    EVICTION = "Eviction"
    COVID = "COVID Rent Reduction"


class Participant:
    """
    Participant name fields
    """

    CLIENT = "Client"


class ActionFolder:
    """
    A folder where documents go in a matter.
    """

    CLIENT = "Client"
    PRECENDENTS = "Precedents"
    RESOURCES = "Resources"
