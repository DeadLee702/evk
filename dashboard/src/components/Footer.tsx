import type { VersionInfo } from "../types";

export function Footer({ version }: { version: VersionInfo | null }) {
  return (
    <footer className="mt-6 glass-card rounded-xl p-4">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span className="font-mono">
            {version?.platform || "Z-12"} v{version?.version || "1.0.0"}
          </span>
          {version?.components &&
            Object.entries(version.components).map(([key, val]) => (
              <span key={key} className="font-mono">
                {key}: <span className="text-gray-400">{val}</span>
              </span>
            ))}
        </div>
        <div className="flex items-center gap-3">
          <span>Build: {version?.build_mode || "release"}</span>
          <span>Toolchain: {version?.rust_toolchain || "stable"}</span>
        </div>
      </div>
    </footer>
  );
}
