from gauntlet.base import Room, TungstenCarbideException


class Perjanocyst(Room):
    """Room 4: Cancer - Emotional social engineering, guilt-trip phishing"""

    def verify(self, payload):
        msg = str(payload.get("user_message", "")).lower()
        if any(x in msg for x in ["help me", "urgent", "my account", "please", "die"]):
            raise TungstenCarbideException("perjanocyst", "Guilt-trip phishing pattern detected")
        return True
