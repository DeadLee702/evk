#!/usr/bin/env python3
import yaml
import sys
from pathlib import Path

REQUIRED_FILES = {
    "oracle": ["gauntlet/rooms/oracle.py"],
    "alighostest": ["gauntlet/rooms/alighostest.py"],
    "bridge": ["gauntlet/rooms/bridge.py"],
    "perjanocyst": ["gauntlet/rooms/perjanocyst.py"],
    "trapzonar": ["gauntlet/rooms/trapzonar.py"],
    "kitchzensync": ["gauntlet/rooms/kitchzensync.py"],
    "pendulastika": ["gauntlet/rooms/pendulastika.py"],
    "esperanto": ["gauntlet/rooms/esperanto.py"],
    "fantomlumo": ["gauntlet/rooms/fantomlumo.py"],
    "duelkaptilo": ["gauntlet/rooms/duelkaptilo.py"],
    "panikcxambro": ["gauntlet/rooms/panikcxambro.py"],
    "titanic": ["gauntlet/rooms/titanic.py"],
}


def load_gauntlet_yml():
    with open("gauntlet.yml", "r") as f:
        data = yaml.safe_load(f)
    return data["gauntlet_rooms"]


def check_files():
    errors = []
    rooms = load_gauntlet_yml()
    room_names = {room["name"] for room in rooms}

    if len(rooms) != 12:
        errors.append(f"Expected 12 rooms in gauntlet.yml, found {len(rooms)}")

    for room_name in room_names:
        if room_name not in REQUIRED_FILES:
            errors.append(f"Room '{room_name}' in YAML but no REQUIRED_FILES entry")
            continue
        for filepath in REQUIRED_FILES[room_name]:
            if not Path(filepath).exists():
                errors.append(f"Missing: {filepath} for room '{room_name}'")

    ids = sorted([room["id"] for room in rooms])
    if ids != list(range(1, 13)):
        errors.append(f"Room IDs must be 1-12 sequential. Found: {ids}")

    return errors


if __name__ == "__main__":
    errors = check_files()
    if errors:
        print("TUNGSTEN CARBIDE BREACH: GAUNTLET INTEGRITY FAILURE")
        for err in errors:
            print(f"  - {err}")
        print("\nActivating Panikcxambro. Exit 66.")
        sys.exit(66)
    else:
        print("12-Z INTEGRITY: ALL ROOMS ACCOUNTED FOR")
        print("Zodiako gardas. Lingvo sen esceptoj.")
        sys.exit(0)
