import { useEffect, useState } from "react";
import { useAuth, RedirectToSignIn, UserButton } from "@clerk/nextjs";
import Link from "next/link";

interface Config {
  services: string;
  standard_rate: string;
  onboarding_rate: string;
  availability: string;
  response_policy: string;
}

const EMPTY_CONFIG: Config = {
  services: "",
  standard_rate: "",
  onboarding_rate: "",
  availability: "",
  response_policy: "",
};

export default function Settings() {
  const { isLoaded, isSignedIn } = useAuth();

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-[#05050A] flex items-center justify-center">
        <span className="text-[#9397AC] text-sm">Checking session...</span>
      </div>
    );
  }

  if (!isSignedIn) {
    return <RedirectToSignIn />;
  }

  return <SettingsForm />;
}

function SettingsForm() {
  const [config, setConfig] = useState<Config>(EMPTY_CONFIG);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function load() {
      const res = await fetch("/api/company-config");
      const data = await res.json();
      if (data) {
        setConfig({
          services: data.services || "",
          standard_rate: data.standard_rate || "",
          onboarding_rate: data.onboarding_rate || "",
          availability: data.availability || "",
          response_policy: data.response_policy || "",
        });
      }
      setLoading(false);
    }
    load();
  }, []);

  async function handleSave() {
    setSaving(true);
    setSaved(false);
    await fetch("/api/company-config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config),
    });
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  }

  function update(field: keyof Config, value: string) {
    setConfig((prev) => ({ ...prev, [field]: value }));
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#05050A] flex items-center justify-center">
        <span className="text-[#9397AC] text-sm">Loading your settings...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#05050A] text-[#F2F2F8] font-[family-name:var(--font-body)] px-6 py-14 md:px-10">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link href="/" className="text-xs text-[#9397AC] hover:text-[#F2F2F8] transition-colors mb-3 inline-block">
              &larr; Back to dashboard
            </Link>
            <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Business Settings</h1>
            <p className="text-[#9397AC] text-sm mt-2">
              This is what your agent uses to draft accurate replies. Nothing here gets shared outside your account.
            </p>
          </div>
          <UserButton />
        </div>

        <div className="space-y-5">
          <Field
            label="Services"
            placeholder="e.g. Marketing strategy, social media management, brand consulting"
            value={config.services}
            onChange={(v) => update("services", v)}
          />
          <Field
            label="Standard rate"
            placeholder="e.g. $400/month for ongoing retainer clients (up to 10 hours/month)"
            value={config.standard_rate}
            onChange={(v) => update("standard_rate", v)}
          />
          <Field
            label="Onboarding rate"
            placeholder="e.g. $450/month for the first 3 months, then drops to standard rate"
            value={config.onboarding_rate}
            onChange={(v) => update("onboarding_rate", v)}
          />
          <Field
            label="Availability"
            placeholder="e.g. Currently accepting 2 new clients starting next month"
            value={config.availability}
            onChange={(v) => update("availability", v)}
          />
          <Field
            label="Response policy"
            placeholder="e.g. Always be warm and professional. Clarify rate distinctions clearly."
            value={config.response_policy}
            onChange={(v) => update("response_policy", v)}
            multiline
          />
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="mt-8 w-full rounded-full py-3 font-medium text-sm transition-colors bg-[#8B7CF7] hover:bg-[#7A6BE8] disabled:opacity-50 text-[#05050A]"
        >
          {saving ? "Saving..." : saved ? "Saved ✓" : "Save settings"}
        </button>
      </div>
    </div>
  );
}

function Field({
  label,
  placeholder,
  value,
  onChange,
  multiline,
}: {
  label: string;
  placeholder: string;
  value: string;
  onChange: (v: string) => void;
  multiline?: boolean;
}) {
  const baseClass =
    "w-full rounded-2xl bg-white/[0.035] border border-white/[0.08] px-4 py-3 text-sm text-[#F2F2F8] placeholder:text-[#5A5F70] focus:outline-none focus:border-[#8B7CF7]/50 transition-colors";

  return (
    <div>
      <label className="block text-xs tracking-wider text-[#9397AC] uppercase mb-2">{label}</label>
      {multiline ? (
        <textarea
          className={`${baseClass} min-h-[90px] resize-none`}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      ) : (
        <input
          className={baseClass}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      )}
    </div>
  );
}