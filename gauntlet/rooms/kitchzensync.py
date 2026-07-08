from gauntlet.base import Room, TungstenCarbideException


class Kitchzensync(Room):
    """Room 6: Virgo - Supply chain attacks hidden in clean code"""

    def verify(self, payload):
        manifest = payload.get("dependency_manifest", {})
        for dep in manifest.get("dependencies", []):
            if dep.get("version") == "latest" or "*" in dep.get("version", ""):
                raise TungstenCarbideException("kitchzensync", "Linter blind spot: wildcard version")
        return True
