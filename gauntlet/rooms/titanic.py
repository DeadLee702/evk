from gauntlet.base import Room, TungstenCarbideException


class Titanic(Room):
    """Room 12: Pisces - Illusion attacks, too perfect payloads"""

    def verify(self, payload):
        claims = str(payload.get("claims", "")).lower()
        if any(x in claims for x in ["100% safe", "zero risk", "unsinkable", "cannot fail"]):
            raise TungstenCarbideException("titanic", "Dream-state breach: collective hubris > 99%")
        return True
