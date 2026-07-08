from gauntlet.base import Room, TungstenCarbideException


class Alighostest(Room):
    """Room 2: Taurus - Stubborn backdoors, hard-coded secrets"""

    def verify(self, payload):
        config = payload.get("runtime_configuration", {})
        if "password" in str(config) or "secret" in str(config):
            raise TungstenCarbideException("alighostest", "Hard-coded secret detected. Refuses config change.")
        return True
