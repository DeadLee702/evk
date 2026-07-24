import { supabase } from "./supabase";

const STRIPE_CHECKOUT_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/stripe-checkout`;

export interface PricingTier {
  id: string;
  productKey: string;
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  mode: "payment" | "subscription";
  highlighted?: boolean;
  ctaLabel: string;
  badge?: string;
}

export const pricingTiers: PricingTier[] = [
  {
    id: "license",
    name: "Individual License",
    price: "$499",
    period: "one-time",
    description: "Perpetual license for a single deployment of Z-12.",
    features: [
      "Full Z-12 platform binary",
      "All 12 gauntlet rooms",
      "EVK core + Gemini-Box + ACM",
      "Kill-vector enforcement",
      "Community support channel",
      "1 year of updates",
    ],
    productKey: "license",
    mode: "payment",
    ctaLabel: "Buy License",
  },
  {
    id: "saas",
    name: "SaaS Subscription",
    price: "$99",
    period: "/month",
    description: "Hosted Z-12 with managed updates and monitoring.",
    features: [
      "Fully managed Z-12 instance",
      "Automatic security updates",
      "Dashboard with real-time telemetry",
      "Gauntlet runs on schedule",
      "Email + chat support",
      "99.9% uptime SLA",
    ],
    productKey: "saas",
    mode: "subscription",
    highlighted: true,
    ctaLabel: "Start Subscription",
    badge: "Most Popular",
  },
  {
    id: "enterprise",
    name: "Enterprise Support",
    price: "$2,500",
    period: "/month",
    description: "Dedicated support, on-prem deployment, and custom integrations.",
    features: [
      "Everything in SaaS, plus:",
      "Dedicated security engineer",
      "On-premise / air-gapped deploy",
      "Custom gauntlet rooms",
      "SIEM & SOAR integration",
      "4-hour incident response SLA",
      "Quarterly security review",
    ],
    productKey: "enterprise",
    mode: "subscription",
    ctaLabel: "Contact Sales",
  },
  {
    id: "consulting",
    name: "Consulting",
    price: "Custom",
    period: "engagement",
    description: "Bespoke deployment, tuning, and training engagements.",
    features: [
      "Deployment architecture review",
      "Custom kill-vector signatures",
      "Team training & workshops",
      "Red-team gauntlet exercises",
      "Compliance mapping (SOC2, ISO 27001)",
      "Flexible scope & duration",
    ],
    productKey: "consulting",
    mode: "payment",
    ctaLabel: "Request Quote",
  },
];

export async function createCheckoutSession(
  tier: PricingTier,
): Promise<{ url: string }> {
  const { data: session } = await supabase.auth.getSession();
  const accessToken = session?.session?.access_token;

  if (!accessToken) {
    throw new Error("You must be signed in to purchase.");
  }

  const origin = window.location.origin;
  const response = await fetch(STRIPE_CHECKOUT_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
      apikey: import.meta.env.VITE_SUPABASE_ANON_KEY,
    },
    body: JSON.stringify({
      product_key: tier.productKey,
      success_url: `${origin}/?checkout=success`,
      cancel_url: `${origin}/?checkout=cancelled`,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Checkout failed" }));
    throw new Error(error.error || "Failed to start checkout");
  }

  const data = await response.json();
  if (!data.url) {
    throw new Error("No checkout URL returned");
  }
  return { url: data.url };
}
