from gauntlet.base import Room, TungstenCarbideException


class Trapzonar(Room):
    """Room 5: Leo - Attention-seeking malware, loud DDoS"""

    def verify(self, payload):
        if payload.get("requests_per_second", 0) > 1000:
            raise TungstenCarbideException("trapzonar", "Log-spamming DDoS: wants fame")
        return True
