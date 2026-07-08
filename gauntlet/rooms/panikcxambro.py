from gauntlet.base import Room, TungstenCarbideException


class Panikcxambro(Room):
    """Room 11: Aquarius - Chaos injection, break to save it logic bombs"""

    def verify(self, payload):
        if payload.get("action") == "restart_all" and not payload.get("approval"):
            raise TungstenCarbideException("panikcxambro", "Revolutionary logic bomb: unapproved restart")
        return True
