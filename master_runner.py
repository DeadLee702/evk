from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import importlib

app = FastAPI(title="Gauntletized Z-12")

# Map zodiac rooms to their modules + attack types
ROOMS = [
    {"zodiac": "Aries", "module": "gauntlet.oracle", "attack": "Brute Force"},
    {"zodiac": "Taurus", "module": "gauntlet.taurus", "attack": "DoS"},
    {"zodiac": "Gemini", "module": "gauntlet.gemini", "attack": "Session Hijack"},
    {"zodiac": "Cancer", "module": "gauntlet.cancer", "attack": "Rollback"},
    {"zodiac": "Leo", "module": "gauntlet.leo", "attack": "Privilege Escalation"},
    {"zodiac": "Virgo", "module": "gauntlet.virgo", "attack": "Sanitization Bypass"},
    {"zodiac": "Libra", "module": "gauntlet.libra", "attack": "CSRF"},
    {"zodiac": "Scorpio", "module": "gauntlet.scorpio", "attack": "Data Poisoning"},
    {"zodiac": "Sagittarius", "module": "gauntlet.sagittarius", "attack": "Scope Creep"},
    {"zodiac": "Capricorn", "module": "gauntlet.capricorn", "attack": "Logic Bypass"},
    {"zodiac": "Aquarius", "module": "gauntlet.aquarius", "attack": "SSRF"},
    {"zodiac": "Pisces", "module": "gauntlet.titanic", "attack": "Zero-Day"},
]


def scan_room(room):
    """Call each room's scan() function. Returns PURA/VIGLA/POLUITA"""
    try:
        mod = importlib.import_module(room["module"])
        return mod.scan()  # Each room implements scan()
    except:
        return "VIGLA"  # Default if module missing


@app.get("/api/health")
def get_health():
    results = []
    for room in ROOMS:
        status = scan_room(room)
        results.append({
            "zodiac": room["zodiac"],
            "attack": room["attack"],
            "status": status,
            "last_check": datetime.utcnow().isoformat()
        })
    
    health = sum(1 for r in results if r["status"] == "PURA") / 12 * 100
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "edition": "Gauntletized Z-12 v1.0",
        "total_rooms": 12,
        "health_score": round(health, 1),
        "gauntlet_status": "ZODIAKO_GARDAS" if health == 100 else "BREACH_DETECTED",
        "reports": results
    }


# Serve the dashboard
app.mount("/static", StaticFiles(directory="dashboard"), name="static")


@app.get("/")
def serve_dashboard():
    return FileResponse("dashboard/index.html")
