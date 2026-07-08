class TungstenCarbideException(Exception):
    def __init__(self, room: str, message: str):
        self.room = room
        super().__init__(f"[{room.upper()}] {message}")


class Room:
    def verify(self, payload):
        raise NotImplementedError
