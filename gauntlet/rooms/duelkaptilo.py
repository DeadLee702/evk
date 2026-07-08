from gauntlet.base import Room, TungstenCarbideException


class Duelkaptilo(Room):
    """Room 10: Capricorn - Slow, patient privilege escalation"""

    def verify(self, payload):
        if payload.get("role") == "user" and payload.get("access") == "admin":
            raise TungstenCarbideException("duelkaptilo", "Vertical climb detected: earns trust then root")
        return True
