import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  Settings,
  User,
  Building,
  Shield,
  Bell,
  Key,
  Database,
  Lock,
  CheckCircle2,
  Save,
  RefreshCw,
  LogOut
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'organization' | 'security' | 'notifications' | 'roles' | 'api' | 'retention'>('security');

  // Form states
  const [lowThreshold, setLowThreshold] = useState('29');
  const [medThreshold, setMedThreshold] = useState('69');
  const [sessionTimeout, setSessionTimeout] = useState('30');
  const [dataRetentionDays, setDataRetentionDays] = useState('90');
  const [mfaEnabled, setMfaEnabled] = useState(true);
  const [notifyHighRisk, setNotifyHighRisk] = useState(true);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // API Key generation state
  const [apiKey, setApiKey] = useState('vnx_live_99a8b7c6d5e4f3a2b1c0d9e8');
  const [apiKeyCopied, setApiKeyCopied] = useState(false);

  useEffect(() => {
    async function loadSettings() {
      try {
        const data = await api.getSettings();
        if (data.risk_low_threshold) setLowThreshold(data.risk_low_threshold.value);
        if (data.risk_med_threshold) setMedThreshold(data.risk_med_threshold.value);
        if (data.session_timeout_minutes) setSessionTimeout(data.session_timeout_minutes.value);
        if (data.data_retention_days) setDataRetentionDays(data.data_retention_days.value);
      } catch (err) {
        console.error('Failed to load settings:', err);
      }
    }
    loadSettings();
  }, []);

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await api.updateSettings({
        risk_low_threshold: lowThreshold,
        risk_med_threshold: medThreshold,
        session_timeout_minutes: sessionTimeout,
        data_retention_days: dataRetentionDays
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to save settings:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleGenerateApiKey = () => {
    const randomHex = Array.from({ length: 24 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
    setApiKey(`vnx_live_${randomHex}`);
  };

  const tabs = [
    { id: 'profile', label: 'Operator Profile', icon: User },
    { id: 'organization', label: 'Organization', icon: Building },
    { id: 'security', label: 'Security & Risk Policy', icon: Shield },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'roles', label: 'Roles & Permissions', icon: Lock },
    { id: 'api', label: 'API & Webhooks', icon: Key },
    { id: 'retention', label: 'Data Retention & GDPR', icon: Database },
  ];

  return (
    <div className="p-6 sm:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Settings className="w-5 h-5 text-blue-400" />
          System Settings & Operational Policies
        </h2>
        <p className="text-xs text-slate-400">
          Tune algorithmic risk cutoffs, session policies, API credentials, and regulatory privacy controls.
        </p>
      </div>

      {saveSuccess && (
        <div className="p-3.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>System operational settings updated and logged to audit trail.</span>
        </div>
      )}

      {/* Main Grid: Tabs Sidebar (3 cols) + Content (9 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Tab Menu */}
        <div className="lg:col-span-3 p-3 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition ${
                  isActive
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-glow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-navy-900/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Right: Tab Panels */}
        <div className="lg:col-span-9 p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md">
          {/* Security & Risk Policy Tab */}
          {activeTab === 'security' && (
            <form onSubmit={handleSaveSettings} className="space-y-6">
              <div>
                <h3 className="text-sm font-bold text-white tracking-wide">
                  Risk Engine Sensitivity Thresholds
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Configure numerical score boundaries (0–100) separating Low, Medium, and High risk classifications.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-navy-900/60 border border-slate-700/40 space-y-2">
                  <label className="block text-xs font-semibold text-slate-200">
                    Low Risk Maximum Score (Currently &le; {lowThreshold})
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="50"
                    value={lowThreshold}
                    onChange={(e) => setLowThreshold(e.target.value)}
                    className="w-full px-3 py-2 bg-navy-950 border border-slate-700 rounded-xl text-xs text-white"
                  />
                  <span className="text-[10px] text-slate-400 block">
                    Scores below this limit qualify for expedited automated verification.
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-navy-900/60 border border-slate-700/40 space-y-2">
                  <label className="block text-xs font-semibold text-slate-200">
                    Medium Risk Maximum Score (Currently &le; {medThreshold})
                  </label>
                  <input
                    type="number"
                    min="51"
                    max="85"
                    value={medThreshold}
                    onChange={(e) => setMedThreshold(e.target.value)}
                    className="w-full px-3 py-2 bg-navy-950 border border-slate-700 rounded-xl text-xs text-white"
                  />
                  <span className="text-[10px] text-slate-400 block">
                    Scores above this cutoff automatically flag for mandatory senior adjudication.
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-700/60 space-y-4">
                <h3 className="text-sm font-bold text-white tracking-wide">
                  Session & Inactivity Policies
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-navy-900/60 border border-slate-700/40 space-y-2">
                    <label className="block text-xs font-semibold text-slate-200">
                      Session Inactivity Timeout (Minutes)
                    </label>
                    <select
                      value={sessionTimeout}
                      onChange={(e) => setSessionTimeout(e.target.value)}
                      className="w-full px-3 py-2 bg-navy-950 border border-slate-700 rounded-xl text-xs text-white"
                    >
                      <option value="15">15 Minutes (Strict Financial)</option>
                      <option value="30">30 Minutes (Enterprise Standard)</option>
                      <option value="60">60 Minutes (Standard)</option>
                    </select>
                  </div>

                  <div className="p-4 rounded-xl bg-navy-900/60 border border-slate-700/40 space-y-2">
                    <label className="block text-xs font-semibold text-slate-200">
                      Two-Factor Authentication (2FA)
                    </label>
                    <div className="flex items-center justify-between pt-1">
                      <span className="text-xs text-slate-400">Enforce Hardware/TOTP</span>
                      <input
                        type="checkbox"
                        checked={mfaEnabled}
                        onChange={(e) => setMfaEnabled(e.target.checked)}
                        className="w-4 h-4 rounded text-blue-600 bg-navy-950 border-slate-700"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition shadow-glow-sm flex items-center gap-2"
                >
                  {isSaving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                  <span>Save Policy Settings</span>
                </button>
              </div>
            </form>
          )}

          {/* Operator Profile Tab */}
          {activeTab === 'profile' && (
            <div className="space-y-5">
              <h3 className="text-sm font-bold text-white tracking-wide">Operator Profile</h3>
              <div className="flex items-center gap-4 pb-4 border-b border-slate-700/60">
                <img
                  src={user?.avatar || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150'}
                  alt={user?.full_name}
                  className="w-16 h-16 rounded-2xl object-cover border-2 border-blue-500/40 shadow-glow-sm"
                />
                <div>
                  <h4 className="text-base font-bold text-white">{user?.full_name}</h4>
                  <p className="text-xs text-blue-400 font-semibold">{user?.role}</p>
                  <p className="text-[11px] text-slate-400">{user?.email}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Username</label>
                  <input
                    type="text"
                    disabled
                    value={user?.username}
                    className="w-full px-3 py-2 bg-navy-950 border border-slate-700 rounded-xl text-slate-300 opacity-80"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Operator Clearance Level</label>
                  <input
                    type="text"
                    disabled
                    value="Tier-3 Lead Investigator"
                    className="w-full px-3 py-2 bg-navy-950 border border-slate-700 rounded-xl text-slate-300 opacity-80"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Organization Tab */}
          {activeTab === 'organization' && (
            <div className="space-y-4 text-xs">
              <h3 className="text-sm font-bold text-white tracking-wide">Corporate Organization</h3>
              <div className="p-4 rounded-xl bg-navy-900/60 border border-slate-700/40 space-y-3">
                <div>
                  <label className="block text-slate-400 mb-1">Organization Name</label>
                  <input
                    type="text"
                    defaultValue="Verinex Global Compliance Corp"
                    className="w-full px-3 py-2 bg-navy-950 border border-slate-700 rounded-xl text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Regulatory Jurisdiction</label>
                  <input
                    type="text"
                    defaultValue="Global / Multi-Jurisdictional (FATF, FinCEN, EBA Compliant)"
                    className="w-full px-3 py-2 bg-navy-950 border border-slate-700 rounded-xl text-white"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="space-y-4 text-xs">
              <h3 className="text-sm font-bold text-white tracking-wide">Notification & Alert Channels</h3>
              <div className="p-4 rounded-xl bg-navy-900/60 border border-slate-700/40 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-semibold text-white block">High-Risk Case Escalation</span>
                    <span className="text-slate-400 text-[11px]">Instant dispatch email when an ID scores &ge; 70</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifyHighRisk}
                    onChange={(e) => setNotifyHighRisk(e.target.checked)}
                    className="w-4 h-4 rounded text-blue-600 bg-navy-950 border-slate-700"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Roles & Permissions Tab */}
          {activeTab === 'roles' && (
            <div className="space-y-4 text-xs">
              <h3 className="text-sm font-bold text-white tracking-wide">Role-Based Access Control (RBAC) Matrix</h3>
              <div className="divide-y divide-slate-700/50 p-4 rounded-xl bg-navy-900/60 border border-slate-700/40">
                <div className="py-2.5 flex items-center justify-between">
                  <div>
                    <span className="font-bold text-white">Risk Administrator</span>
                    <span className="text-slate-400 block text-[11px]">Full access, policy configuration, audit export</span>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-semibold text-[10px]">Unrestricted</span>
                </div>
                <div className="py-2.5 flex items-center justify-between">
                  <div>
                    <span className="font-bold text-white">Senior Reviewer</span>
                    <span className="text-slate-400 block text-[11px]">Adjudicate cases, override AI risk, generate reports</span>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-semibold text-[10px]">Adjudication</span>
                </div>
                <div className="py-2.5 flex items-center justify-between">
                  <div>
                    <span className="font-bold text-white">Compliance Analyst</span>
                    <span className="text-slate-400 block text-[11px]">Screen documents, record case notes, review flags</span>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-semibold text-[10px]">Screening</span>
                </div>
              </div>
            </div>
          )}

          {/* API Settings Tab */}
          {activeTab === 'api' && (
            <div className="space-y-4 text-xs">
              <h3 className="text-sm font-bold text-white tracking-wide">REST API & Secret Keys</h3>
              <div className="p-4 rounded-xl bg-navy-900/60 border border-slate-700/40 space-y-3">
                <div>
                  <label className="block text-slate-400 mb-1">Production Secret Key</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      readOnly
                      value={apiKey}
                      className="flex-1 px-3 py-2 bg-navy-950 border border-slate-700 rounded-xl font-mono text-xs text-white"
                    />
                    <button
                      type="button"
                      onClick={() => {
                        navigator.clipboard.writeText(apiKey);
                        setApiKeyCopied(true);
                        setTimeout(() => setApiKeyCopied(false), 2000);
                      }}
                      className="px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-xl text-white font-semibold"
                    >
                      {apiKeyCopied ? 'Copied!' : 'Copy'}
                    </button>
                    <button
                      type="button"
                      onClick={handleGenerateApiKey}
                      className="px-3 py-2 bg-blue-600 hover:bg-blue-500 rounded-xl text-white font-semibold"
                    >
                      Regenerate
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Data Retention & GDPR Tab */}
          {activeTab === 'retention' && (
            <div className="space-y-4 text-xs">
              <h3 className="text-sm font-bold text-white tracking-wide">Data Retention & Privacy Lifecycle</h3>
              <div className="p-4 rounded-xl bg-navy-900/60 border border-slate-700/40 space-y-3">
                <div>
                  <label className="block text-slate-400 mb-1">Automated PII Redaction Window</label>
                  <select
                    value={dataRetentionDays}
                    onChange={(e) => setDataRetentionDays(e.target.value)}
                    className="w-full px-3 py-2 bg-navy-950 border border-slate-700 rounded-xl text-white"
                  >
                    <option value="30">30 Days (Strict European Banking Standard)</option>
                    <option value="90">90 Days (Enterprise Standard)</option>
                    <option value="365">365 Days (Extended Compliance)</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
