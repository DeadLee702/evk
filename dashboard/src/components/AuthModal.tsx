import { useState, useEffect } from "react";
import { supabase } from "../lib/supabase";
import type { User } from "@supabase/supabase-js";

interface Props {
  open: boolean;
  onClose: () => void;
  onAuthSuccess: (user: User) => void;
}

export function AuthModal({ open, onClose, onAuthSuccess }: Props) {
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setError(null);
      setEmail("");
      setPassword("");
    }
  }, [open]);

  if (!open) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (mode === "signup") {
        const { data, error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        if (data.user) onAuthSuccess(data.user);
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        if (data.user) onAuthSuccess(data.user);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm" onClick={onClose}>
      <div
        className="glass-card rounded-2xl p-8 w-full max-w-md mx-4 border border-z12-border"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-100">
            {mode === "signin" ? "Sign In" : "Create Account"}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-300 text-xl leading-none"
          >
            &times;
          </button>
        </div>

        <div className="flex gap-2 mb-6 p-1 bg-z12-bg rounded-lg border border-z12-border">
          <button
            onClick={() => setMode("signin")}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
              mode === "signin"
                ? "bg-z12-primary text-white"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => setMode("signup")}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
              mode === "signup"
                ? "bg-z12-primary text-white"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1.5">
              Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-z12-bg border border-z12-border rounded-lg px-3 py-2.5 text-sm text-gray-200 placeholder-gray-600 focus:border-z12-primary focus:outline-none transition-colors"
              placeholder="you@company.com"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1.5">
              Password
            </label>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-z12-bg border border-z12-border rounded-lg px-3 py-2.5 text-sm text-gray-200 placeholder-gray-600 focus:border-z12-primary focus:outline-none transition-colors"
              placeholder="Minimum 6 characters"
            />
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-xs text-red-400">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-z12-primary hover:bg-blue-600 disabled:bg-gray-700 disabled:text-gray-500 text-white text-sm font-medium rounded-lg transition-colors"
          >
            {loading
              ? "Please wait..."
              : mode === "signin"
                ? "Sign In"
                : "Create Account"}
          </button>
        </form>

        <p className="mt-4 text-xs text-gray-600 text-center">
          {mode === "signin"
            ? "Need an account? "
            : "Already have one? "}
          <button
            onClick={() => setMode(mode === "signin" ? "signup" : "signin")}
            className="text-z12-primary hover:text-blue-400"
          >
            {mode === "signin" ? "Sign up" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}
