import { useState } from "react";
import { pricingTiers, createCheckoutSession, type PricingTier } from "../lib/stripe";

interface Props {
  onBack: () => void;
  onRequireAuth: () => void;
  isSignedIn: boolean;
}

export function PricingPage({ onBack, onRequireAuth, isSignedIn }: Props) {
  const [checkoutTier, setCheckoutTier] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePurchase = async (tier: PricingTier) => {
    if (tier.id === "consulting") {
      window.location.href = "mailto:sales@z12.security?subject=Z-12%20Consulting%20Engagement";
      return;
    }

    if (!isSignedIn) {
      onRequireAuth();
      return;
    }

    setCheckoutTier(tier.id);
    setError(null);
    try {
      const { url } = await createCheckoutSession(tier);
      window.location.href = url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout failed");
    } finally {
      setCheckoutTier(null);
    }
  };

  return (
    <div className="min-h-screen bg-z12-bg text-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-200 transition-colors"
          >
            <span>&larr;</span> Back to Dashboard
          </button>
          <h1 className="text-lg font-semibold text-gray-300">
            Z-12 Sovereign Security Platform
          </h1>
        </div>

        {/* Hero */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-100 mb-3">
            Pricing
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            From individual licenses to enterprise-grade support, choose the
            plan that fits your security posture.
          </p>
        </div>

        {/* Error banner */}
        {error && (
          <div className="mb-6 max-w-2xl mx-auto p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-400 text-center">
            {error}
          </div>
        )}

        {/* Pricing cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {pricingTiers.map((tier) => (
            <div
              key={tier.id}
              className={`glass-card rounded-2xl p-6 flex flex-col relative transition-all hover:scale-[1.02] ${
                tier.highlighted
                  ? "border-z12-primary border-2 shadow-lg shadow-blue-500/10"
                  : "border-z12-border"
              }`}
            >
              {tier.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-z12-primary text-white text-xs font-medium rounded-full whitespace-nowrap">
                  {tier.badge}
                </div>
              )}

              <h3 className="text-lg font-semibold text-gray-100 mb-1">
                {tier.name}
              </h3>
              <p className="text-xs text-gray-500 mb-4 min-h-[2.5rem]">
                {tier.description}
              </p>

              <div className="flex items-baseline gap-1 mb-6">
                <span className="text-3xl font-bold text-gray-100">
                  {tier.price}
                </span>
                <span className="text-sm text-gray-500">
                  {tier.period}
                </span>
              </div>

              <ul className="space-y-2.5 mb-6 flex-1">
                {tier.features.map((feature, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-gray-400"
                  >
                    <span className="text-z12-success mt-0.5 shrink-0">
                      &#10003;
                    </span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handlePurchase(tier)}
                disabled={checkoutTier === tier.id}
                className={`w-full py-2.5 text-sm font-medium rounded-lg transition-colors disabled:opacity-50 ${
                  tier.highlighted
                    ? "bg-z12-primary hover:bg-blue-600 text-white"
                    : "bg-z12-surface border border-z12-border hover:border-gray-600 text-gray-200"
                }`}
              >
                {checkoutTier === tier.id
                  ? "Redirecting..."
                  : tier.ctaLabel}
              </button>
            </div>
          ))}
        </div>

        {/* FAQ section */}
        <div className="max-w-3xl mx-auto">
          <h3 className="text-xl font-semibold text-gray-200 mb-6 text-center">
            Frequently Asked Questions
          </h3>
          <div className="space-y-4">
            <div className="glass-card rounded-xl p-5">
              <h4 className="text-sm font-medium text-gray-200 mb-2">
                What's the difference between a license and SaaS?
              </h4>
              <p className="text-sm text-gray-400">
                An individual license is a one-time purchase that gives you the
                Z-12 binaries to run on your own infrastructure. SaaS is a
                managed, hosted instance with automatic updates and monitoring.
              </p>
            </div>
            <div className="glass-card rounded-xl p-5">
              <h4 className="text-sm font-medium text-gray-200 mb-2">
                Can I upgrade from a license to SaaS later?
              </h4>
              <p className="text-sm text-gray-400">
                Yes. Your configuration and gauntlet history can be migrated to
                a hosted instance at any time. Contact support for assistance.
              </p>
            </div>
            <div className="glass-card rounded-xl p-5">
              <h4 className="text-sm font-medium text-gray-200 mb-2">
                What does enterprise support include?
              </h4>
              <p className="text-sm text-gray-400">
                Enterprise includes a dedicated security engineer, on-premise or
                air-gapped deployment options, custom gauntlet rooms, SIEM/SOAR
                integration, and a 4-hour incident response SLA.
              </p>
            </div>
            <div className="glass-card rounded-xl p-5">
              <h4 className="text-sm font-medium text-gray-200 mb-2">
                How does consulting work?
              </h4>
              <p className="text-sm text-gray-400">
                Consulting engagements are scoped per project. They can include
                deployment architecture reviews, custom kill-vector signatures,
                team training, red-team gauntlet exercises, and compliance
                mapping. Contact us for a quote.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
