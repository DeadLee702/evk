export interface RoomReport {
  id: string;
  room: string;
  zodiac: string;
  attack_vector: string;
  signature: string;
  benign_pass: boolean;
  malicious_blocked: boolean;
  status: "PURA" | "VIGLA" | "POLUITA";
  last_check: string;
}

export interface GauntletReport {
  platform: string;
  version: string;
  timestamp: string;
  status: string;
  mode: string;
  total_rooms: number;
  rooms_healthy: number;
  rooms_failed: number;
  health_score: number;
  cop_score: number;
  gauntlet_status: "ZODIAKO_GARDAS" | "BREACH_DETECTED";
  audit_results: Record<string, string>;
  evk_core_detail: string;
  reports: RoomReport[];
  warning?: string;
  closure?: string;
}

export interface ScanRecord {
  id: string;
  artifact_name: string;
  status_code: string;
  verdict: string;
  incident_type: string;
  severity: string;
  enforcement_action: string;
  confidence: number;
  report_json: Record<string, unknown>;
  created_at: string;
}

export interface ComponentStatus {
  name: string;
  version: string;
  status: "OPERATIONAL" | "DEGRADED" | "OFFLINE";
  build_mode: string;
  last_check: string;
}

export interface AuditEvent {
  id: string;
  event_type: string;
  component: string;
  severity: string;
  action: string;
  details: Record<string, unknown>;
  message: string;
  created_at: string;
}

export interface VersionInfo {
  platform: string;
  version: string;
  components: Record<string, string>;
  rust_toolchain: string;
  build_mode: string;
}

export interface ScanResult {
  artifact_path: string;
  artifact_name: string;
  acm: {
    verdict: string;
    status_code: string;
    incident_type: string;
    severity: string;
    enforcement_action: string;
    confidence: number;
    message: string;
    timestamp: string;
  } | null;
  gemini_box: {
    file_path: string;
    status_code: string;
    incident_type: string;
    confidence: number;
    severity: string;
    recommended_action: string;
    analysis: string;
  }[] | null;
  timestamp: string;
}

export const ZODIAC_ICONS: Record<string, string> = {
  Aries: "\u2648",
  Taurus: "\u2649",
  Gemini: "\u264A",
  Cancer: "\u264B",
  Leo: "\u264C",
  Virgo: "\u264D",
  Libra: "\u264E",
  Scorpio: "\u264F",
  Sagittarius: "\u2650",
  Capricorn: "\u2651",
  Aquarius: "\u2652",
  Pisces: "\u2653",
};
