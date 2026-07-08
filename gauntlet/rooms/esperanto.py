from gauntlet.base import Room, TungstenCarbideException
import re
import base64
import json


class Esperanto(Room):
    """Room 8: Scorpio - Silent, deep, poisoned dependencies"""

    def __init__(self):
        self.poison_patterns = [
            r"cron\s*:\s*.*\/5\s+\*\s+\*\s+\*\s+\*",
            r"sleep\s+\d{3,}",
            r"at\s+now\s+\+\s+\d+\s+(days|weeks)",
        ]
        self.exec_primitives = ["exec", "eval", "os.", "subprocess", "curl", "wget", "system"]

    def _has_obfuscated_entropy(self, text_string: str) -> bool:
        b64_pattern = r"(?:[A-Za-z0-9+/]{4}){8,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?"
        matches = re.findall(b64_pattern, text_string)
        for match in matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8', errors='strict')
                if any(term in decoded for term in self.exec_primitives):
                    return True
            except Exception:
                continue
        return False

    def verify(self, payload):
        manifest_data = json.dumps(payload.get("dependency_manifest", {}))
        config_strings = json.dumps(payload.get("runtime_configuration", {}))
        combined = manifest_data + config_strings
        for pattern in self.poison_patterns:
            if re.search(pattern, combined):
                raise TungstenCarbideException(
                    "esperanto", "Latent Logic Vector: Dormant scheduling parameters or time-bomb sequences detected."
                )
        if self._has_obfuscated_entropy(combined):
            raise TungstenCarbideException(
                "esperanto", "Obfuscated Poison Vector: High-entropy base64 block containing system executable primitives detected."
            )
        return True
