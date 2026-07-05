#!/usr/bin/env python3
"""
Protocol 1: Pendulastika Oracle
DEC FORCE v2.2 Entropy Analysis

Research/Educational - SIMULADO mode only - No destructive operations - Entropy analysis only

Recursively scans target directory/file for high-entropy content (potential
compression, encryption, or obfuscation). Uses Shannon entropy calculation.

All operations are read-only. No files are modified, deleted, or exfiltrated.
"""

import sys
import json
import argparse
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import uuid


class Verdict(Enum):
    """DEC FORCE verdict system"""
    PURA = "PURA"  # Clear, no anomalies
    ALARMO = "ALARMO"  # Alert condition detected
    PERJURO_DETEKTITA = "PERJURO_DETEKTITA"  # Perjury/deepfake detected


class EsperantoProtokolo:
    """
    Minimal EsperantoProtokolo logger for protocol use.
    """

    def __init__(self, protocol_name: str, run_id: Optional[str] = None):
        """Initialize Esperanto logger."""
        self.protocol_name = protocol_name
        self.run_id = run_id or str(uuid.uuid4())[:8]
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.logs: List[Dict[str, Any]] = []
        self.verdict = Verdict.PURA

    def log(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log an event with timestamp and data."""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": event,
            "run_id": self.run_id,
            "data": data or {}
        }
        self.logs.append(entry)

    def set_verdict(self, verdict: Verdict) -> None:
        """Set the protocol verdict."""
        self.verdict = verdict
        self.log("VERDICT_SET", {"verdict": verdict.value})

    def generate_report(self) -> Dict[str, Any]:
        """Generate JSON report."""
        return {
            "protocol_name": self.protocol_name,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "verdict": self.verdict.value,
            "logs": self.logs,
            "closure": "Relenthol engaĝita."
        }


class PendulastikaOracle:
    """
    Protocol 1: Pendulastika Oracle
    
    Entropy analysis for detecting high-entropy files (compression,
    encryption, obfuscation, or potential anomalies).
    """

    HIGH_ENTROPY_THRESHOLD = 7.5  # bits/byte
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    CHUNK_SIZE = 64 * 1024  # 64KB for streaming

    def __init__(
        self,
        target_path: str,
        output_file: Optional[str] = None,
        simulado: bool = True
    ):
        """
        Initialize Oracle.
        
        Args:
            target_path: Directory or file to analyze
            output_file: Optional JSON output file
            simulado: Run in simulator mode (read-only)
        """
        self.target_path = Path(target_path)
        self.output_file = Path(output_file) if output_file else None
        self.simulado = simulado
        self.logger = EsperantoProtokolo("Pendulastika Oracle")
        self.files_scanned = 0
        self.high_entropy_files: List[Dict[str, Any]] = []

    def validate_simulado(self) -> bool:
        """Validate that SIMULADO mode is enabled."""
        if not self.simulado:
            self.logger.set_verdict(Verdict.PERJURO_DETEKTITA)
            self.logger.log("SIMULADO_DISABLED", {
                "error": "SIMULADO mode is required. Use --simulado or set to True."
            })
            return False
        return True

    def validate_target(self) -> bool:
        """Validate that target path exists."""
        if not self.target_path.exists():
            self.logger.log("TARGET_NOT_FOUND", {
                "target": str(self.target_path)
            })
            self.logger.set_verdict(Verdict.ALARMO)
            return False
        return True

    @staticmethod
    def calculate_entropy(data: bytes) -> float:
        """
        Calculate Shannon entropy of byte data.
        
        Formula: H = -sum(p * log2(p)) for each byte value 0-255
        where p is the probability of byte occurrence.
        
        Returns:
            Entropy in bits/byte (0-8)
        """
        if not data:
            return 0.0

        # Build frequency table
        frequencies = [0] * 256
        for byte in data:
            frequencies[byte] += 1

        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        for freq in frequencies:
            if freq > 0:
                p = freq / data_len
                entropy -= p * math.log2(p)

        return entropy

    def scan_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Scan a single file for high entropy.
        
        Args:
            file_path: Path to file to scan
        
        Returns:
            Dict with entropy data if high entropy, None otherwise
        """
        try:
            # Skip symlinks
            if file_path.is_symlink():
                return None

            # Skip if too large
            file_size = file_path.stat().st_size
            if file_size > self.MAX_FILE_SIZE:
                self.logger.log("FILE_SKIPPED_TOO_LARGE", {
                    "file": str(file_path),
                    "size": file_size,
                    "max": self.MAX_FILE_SIZE
                })
                return None

            # Calculate entropy via streaming read
            entropy = 0.0
            all_data = b""
            
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    all_data += chunk

            entropy = self.calculate_entropy(all_data)

            # Flag if high entropy
            if entropy > self.HIGH_ENTROPY_THRESHOLD:
                result = {
                    "path": str(file_path),
                    "entropy": round(entropy, 4),
                    "size": file_size,
                    "threshold": self.HIGH_ENTROPY_THRESHOLD
                }
                return result

            return None

        except PermissionError:
            self.logger.log("FILE_PERMISSION_DENIED", {
                "file": str(file_path)
            })
            return None
        except Exception as e:
            self.logger.log("FILE_SCAN_ERROR", {
                "file": str(file_path),
                "error": str(e)
            })
            return None

    def scan_directory(self, directory: Path) -> None:
        """
        Recursively scan directory for files.
        
        Args:
            directory: Directory to scan
        """
        try:
            for item in directory.iterdir():
                if item.is_file():
                    self.files_scanned += 1
                    result = self.scan_file(item)
                    if result:
                        self.high_entropy_files.append(result)
                elif item.is_dir() and not item.is_symlink():
                    self.scan_directory(item)
        except PermissionError:
            self.logger.log("DIRECTORY_PERMISSION_DENIED", {
                "directory": str(directory)
            })
        except Exception as e:
            self.logger.log("DIRECTORY_SCAN_ERROR", {
                "directory": str(directory),
                "error": str(e)
            })

    def analyze(self) -> int:
        """
        Execute entropy analysis.
        
        Returns:
            Exit code: 0 if PURA, 1 if ALARMO, 2 if PERJURO_DETEKTITA
        """
        try:
            # Validate SIMULADO mode
            if not self.validate_simulado():
                return 2

            # Validate target
            if not self.validate_target():
                return 1

            self.logger.log("ORACLE_START", {
                "target": str(self.target_path),
                "mode": "SIMULADO",
                "threshold": self.HIGH_ENTROPY_THRESHOLD
            })

            # Perform scan
            if self.target_path.is_file():
                self.files_scanned = 1
                result = self.scan_file(self.target_path)
                if result:
                    self.high_entropy_files.append(result)
            else:
                self.scan_directory(self.target_path)

            # Determine verdict
            if self.high_entropy_files:
                verdict = Verdict.ALARMO
                self.logger.log("HIGH_ENTROPY_DETECTED", {
                    "count": len(self.high_entropy_files),
                    "files": [f["path"] for f in self.high_entropy_files[:5]]  # First 5
                })
            else:
                verdict = Verdict.PURA
                self.logger.log("NO_HIGH_ENTROPY_DETECTED", {
                    "files_scanned": self.files_scanned
                })

            self.logger.set_verdict(verdict)

            # Generate report
            report = {
                "protocol": "oracle_v0.2",
                "protocol_number": 1,
                "timestamp": self.logger.timestamp,
                "target": str(self.target_path),
                "mode": "SIMULADO",
                "files_scanned": self.files_scanned,
                "high_entropy_files": self.high_entropy_files,
                "verdict": verdict.value,
                "warning": "Neniu dosiero estis modifita",
                "orchestrator_logs": self.logger.logs,
                "closure": "Relenthol engaĝita."
            }

            # Output report
            report_json = json.dumps(report, indent=2)
            if self.output_file:
                self.output_file.write_text(report_json)
                self.logger.log("REPORT_WRITTEN", {"path": str(self.output_file)})
            else:
                print(report_json)

            self.logger.log("ORACLE_END", {
                "verdict": verdict.value,
                "files_scanned": self.files_scanned,
                "high_entropy_count": len(self.high_entropy_files)
            })

            # Return appropriate exit code
            if verdict == Verdict.PURA:
                return 0
            elif verdict == Verdict.ALARMO:
                return 1
            else:  # PERJURO_DETEKTITA
                return 2

        except Exception as e:
            self.logger.log("ORACLE_ERROR", {"error": str(e)})
            self.logger.set_verdict(Verdict.ALARMO)

            error_report = {
                "protocol": "oracle_v0.2",
                "protocol_number": 1,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "target": str(self.target_path),
                "verdict": Verdict.ALARMO.value,
                "error": str(e),
                "orchestrator_logs": self.logger.logs,
                "closure": "Relenthol engaĝita."
            }

            error_json = json.dumps(error_report, indent=2)
            if self.output_file:
                self.output_file.write_text(error_json)
            else:
                print(error_json)

            return 1


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Protocol 1: Pendulastika Oracle - DEC FORCE v2.2 Entropy Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python oracle_v0.2.py --simulado --target /path/to/scan
  python oracle_v0.2.py --simulado --target /path/to/scan --output results.json
  python oracle_v0.2.py --simulado=False --target /path  # PERJURO_DETEKTITA verdict
        """
    )

    parser.add_argument(
        "--simulado",
        type=lambda x: x.lower() in ("true", "1", "yes"),
        default=True,
        help="Run in SIMULADO (read-only simulator) mode [default: True]"
    )

    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="Directory or file to analyze (required)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file [default: stdout]"
    )

    args = parser.parse_args()

    # Instantiate and run oracle
    oracle = PendulastikaOracle(
        target_path=args.target,
        output_file=args.output,
        simulado=args.simulado
    )

    exit_code = oracle.analyze()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
