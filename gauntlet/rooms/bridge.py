from gauntlet.base import Room, TungstenCarbideException


class Bridge(Room):
    """Room 3: Gemini - MITM, dual-personality APIs"""

    def verify(self, payload):
        req = payload.get("request", {})
        if req.get("client_ip") != req.get("forwarded_for"):
            raise TungstenCarbideException("bridge", "Two-faced protocol: client_ip != forwarded_for")
        return True
