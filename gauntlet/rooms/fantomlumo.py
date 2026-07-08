from gauntlet.base import Room, TungstenCarbideException


class Fantomlumo(Room):
    """Room 9: Sagittarius - Over-scoping, explore everything recon"""

    def verify(self, payload):
        perms = payload.get("permissions", [])
        if "*" in perms or "admin" in perms:
            raise TungstenCarbideException("fantomlumo", "Wildcard permissions: over-scoped recon")
        return True
