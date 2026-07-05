#!/usr/bin/env python3
"""
Research/Educational - SIMULADO mode only - No destructive operations - Hidden file audit only
Protocol 2: Alighostest v0.2 - Hidden File Detection
"""
import os
import stat
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))
from esperanto_engine import EsperantoProtokolo

def assess_risk(path: Path, mode: int, size: int) -> str:
    if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
        if path.suffix in ['.sh', '.py']:
            return "high"
        return "med"
    if size > 1048576:
        return "med"
    return "low"

def scan_hidden(target: Path) -> List[Dict[str, Any]]:
    results = []
    exclude = {'.git', '.DS_Store', '.env.example'}
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in exclude]
        for name in files:
            if not name.startswith('.') or name in exclude:
                continue
            fpath = Path(root) / name
            try:
                st = fpath.stat()
                risk = assess_risk(fpath, st.st_mode, st.st_size)
                results.append({"path": str(fpath), "size": st.st_size, "mode": oct(st.st_mode), "risk": risk})
            except Exception:
                continue
    return results

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--simulado', action='store_true', default=True)
    parser.add_argument('--target', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not args.simulado:
        print("ERROR: Only SIMULADO mode supported", file=sys.stderr)
        return 2
    esp = EsperantoProtokolo()
    esp.log("ALIGHOSTEST_START", {"target": str(args.target)})
    try:
        hidden = scan_hidden(args.target)
        med_high = [h for h in hidden if h["risk"] in ["med", "high"]]
        verdict = "ALARMO" if med_high else "PURA"
        exit_code = 1 if med_high else 0
        result = {"protocol": "alighostest_v0.2", "target": str(args.target), "hidden_files": hidden, "verdict": verdict}
        esp.log("ALIGHOSTEST_END", {"verdict": verdict, "count": len(hidden)})
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))
        return exit_code
    except Exception as e:
        esp.log("ALIGHOSTEST_ERROR", {"error": str(e)})
        return 1

if __name__ == "__main__":
    sys.exit(main())
