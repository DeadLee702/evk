from gauntlet.base import Room, TungstenCarbideException


class Pendulastika(Room):
    """Room 7: Libra - Balance attacks, race conditions"""

    def verify(self, payload):
        if payload.get("concurrent_writes", 0) > 1 and payload.get("no_lock"):
            raise TungstenCarbideException("pendulastika", "Race condition: scales tipping under load")
        return True
