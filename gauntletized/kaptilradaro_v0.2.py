#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from esperanto.esperanto_v0_1 import EsperantoProtokolo

class KaptilradaroTrapzonar:
    def __init__(self):
        self.lang = EsperantoProtokolo()
        self.nomo = "Kaptilradaro Trapzonar"
        self.celo = "Radar - tripwire monitoring"
        self.tripdratoj = ["env_poison", "hook_injection", "memory_leak"]
        self.raporto = {
            "modulo": "kaptilradaro",
            "timestamp": datetime.now().isoformat(),
            "statuso": "pura",
            "aktivigitaj": []
        }

    def skani_tripdratojn(self, medio="safe"):
        for drato in self.tripdratoj:
            if drato in medio.lower():
                self.raporto["aktivigitaj"].append(drato)

        if self.raporto["aktivigitaj"]:
            self.raporto["statuso"] = "malpura"
            print(self.lang.log("malpura", f"Trapzonar: Tripdratoj aktivigitaj - {self.raporto['aktivigitaj']}"))
            return False
        else:
            self.raporto["statuso"] = "pura"
            print(self.lang.log("pura", "Trapzonar: Ĉiuj tripdratoj sekuraj"))
            return True

    def konservi_raporton(self):
        with open("trapzonar_report.json", "w", encoding="utf-8") as f:
            json.dump(self.raporto, f, indent=2, ensure_ascii=False)
        print(self.lang.log("kompleta", "Raporto: trapzonar_report.json"))

if __name__ == "__main__":
    trap = KaptilradaroTrapzonar()
    rezulto = trap.skani_tripdratojn(sys.argv[1] if len(sys.argv) > 1 else "safe")
    trap.konservi_raporton()
    sys.exit(0 if rezulto else 1)
