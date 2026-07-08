from gauntlet.base import Room, TungstenCarbideException


class Oracle(Room):
    """Room 1: Aries - Brute force, head-first exploits, ship-it-broken"""

    def verify(self, payload):
        caller = payload.get("caller_identity", "anonymous")
        if payload.get("force_push_main"):
            raise TungstenCarbideException("oracle", f"Impulsive main push blocked: {caller}")
        return True
