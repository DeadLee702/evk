#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import os
import hashlib
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from esperanto.esperanto_v0_1 import EsperantoProtokolo

class VualrompiloGhostest:
    def __init__(self):
        self.lang = EsperantoProtokolo()
        self.nomo = "Vualrompilo Ghostest"
        self.celo = "Shadow/anomaly detection - veil breaker"
        self.ombroj = ["shadow_process", "hidden_thread", "masked_pid"]
        self.raporto = {
            "modulo": "vualrompilo",
            "timestamp": datetime.now().isoformat(),
            "statuso": "pura",
            "detektitaj_ombroj": [],
            "hash_check": ""
        }

    def skani_ombrojn(self, sistemo="clean"):
        # Simulate shadow process detection
        for ombro in self.ombroj:
            if ombro in sistemo.lower():
                self.raporto["detektitaj_ombroj"].append(ombro)

        # Hash integrity check
        hash_val = hashlib.sha256(sistemo.encode()).hexdigest()[:8]
        self.raporto["hash_check"] = f"sha256:{hash_val}"

        if self.raporto["detektitaj_ombroj"]:
            self.raporto["statuso"] = "malpura"
            print(self.lang.log("malpura", f"Ghostest: Ombroj detektitaj - {self.raporto['detektitaj_ombroj']}"))
            return False
        else:
            self.raporto["statuso"] = "pura"
            print(self.lang.log("pura", f"Ghostest: Neniuj ombroj - Hash {hash_val}"))
            return True

    def konservi_raporton(self):
        with open("ghostest_report.json", "w", encoding="utf-8") as f:
            json.dump(self.raporto, f, indent=2, ensure_ascii=False)
        print(self.lang.log("kompleta", "Raporto: ghostest_report.json"))

if __name__ == "__main__":
    ghost = VualrompiloGhostest()
    rezulto = ghost.skani_ombrojn(sys.argv[1] if len(sys.argv) > 1 else "clean")
    ghost.konservi_raporton()
    sys.exit(0 if rezulto else 1)
