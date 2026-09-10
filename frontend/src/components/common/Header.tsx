import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Shield, Bell, User, LogOut, ChevronDown, Clock, Sparkles } from 'lucide-react';

interface HeaderProps {
  currentTab: string;
  onNavigate: (tab: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ currentTab, onNavigate }) => {
  const { user, logout, quickDemoLogin, triggerSessionExpired } = useAuth();
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const titleMap: Record<string, { title: string; subtitle: string }> = {
    dashboard: { title: 'Executive Overview', subtitle: 'Real-time document screening telemetry & fraud analytics' },
    screening: { title: 'AI Document Screening', subtitle: 'Upload or test fictional identity documents through automated OCR & risk engines' },
    cases: { title: 'Case Management & Adjudication', subtitle: 'Investigate flagged discrepancies, review timeline, and make decisions' },
    reports: { title: 'Compliance & Verification Reports', subtitle: 'Audit-ready historical reporting, exportable in JSON, CSV, and summary formats' },
    audit: { title: 'Security & Audit Logs', subtitle: 'Immutable chain of custody tracking logins, screenings, decisions, and system alerts' },
    settings: { title: 'System Settings & Risk Policies', subtitle: 'Configure risk thresholds, session timeouts, and access permissions' },
    results: { title: 'AI Screening Assessment', subtitle: 'Detailed multi-layer forensic analysis and explainable risk breakdown' },
  };

  const current = titleMap[currentTab] || { title: 'VERINEX Platform', subtitle: 'Identity & Document Screening' };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-20 px-8 bg-navy-900/90 border-b border-slate-800/80 backdrop-blur-md">
      {/* Page Title & Breadcrumb */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold tracking-tight text-white">{current.title}</h1>
          <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Shield className="w-3 h-3 mr-1" />
            AI Guard Active
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-0.5">{current.subtitle}</p>
      </div>

      {/* Action Controls & User Profile */}
      <div className="flex items-center gap-4">
        {/* Quick New Screening CTA */}
        {currentTab !== 'screening' && (
          <button
            onClick={() => onNavigate('screening')}
            className="hidden md:inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 shadow-glow-sm transition duration-150"
          >
            <Sparkles className="w-3.5 h-3.5" />
            New Screening
          </button>
        )}

        {/* Simulate Session Timeout (Required state test) */}
        <button
          onClick={triggerSessionExpired}
          title="Simulate session expiration to verify session-timeout handler"
          className="hidden lg:inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-amber-400 hover:bg-amber-500/10 border border-slate-700/60 transition"
        >
          <Clock className="w-3.5 h-3.5" />
          Test Timeout
        </button>

        {/* Notifications Icon Placeholder */}
        <div className="relative">
          <button className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
          </button>
        </div>

        {/* User Profile Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="flex items-center gap-3 p-1.5 pr-2.5 rounded-xl bg-navy-800 hover:bg-navy-750 border border-slate-700/70 transition"
          >
            <div className="w-8 h-8 rounded-lg overflow-hidden bg-slate-700 border border-blue-400/30 flex items-center justify-center">
              {user?.avatar ? (
                <img src={user.avatar} alt={user.full_name} className="w-full h-full object-cover" />
              ) : (
                <User className="w-4 h-4 text-blue-400" />
              )}
            </div>
            <div className="text-left hidden sm:block">
              <div className="text-xs font-semibold text-white">{user?.full_name || 'Operator'}</div>
              <div className="text-[10px] text-blue-400 font-medium">{user?.role || 'Compliance Analyst'}</div>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {showProfileMenu && (
            <div
              className="absolute right-0 mt-2 w-56 rounded-xl bg-navy-800 border border-slate-700 shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95 duration-150"
              onMouseLeave={() => setShowProfileMenu(false)}
            >
              <div className="px-3 py-2 border-b border-slate-700/60">
                <p className="text-xs font-semibold text-white">{user?.full_name}</p>
                <p className="text-[11px] text-slate-400 truncate">{user?.email}</p>
              </div>

              {/* Quick Role Switcher for Testing */}
              <div className="py-2 border-b border-slate-700/60">
                <span className="px-3 text-[10px] uppercase font-bold text-slate-400 tracking-wider">Switch Demo Persona</span>
                <div className="mt-1 space-y-0.5">
                  <button
                    onClick={() => { quickDemoLogin('analyst'); setShowProfileMenu(false); }}
                    className={`w-full text-left px-3 py-1.5 rounded text-xs transition ${user?.role === 'Compliance Analyst' ? 'bg-blue-600/20 text-blue-300 font-semibold' : 'text-slate-300 hover:bg-slate-700/50'}`}
                  >
                    Sarah Chen (Analyst)
                  </button>
                  <button
                    onClick={() => { quickDemoLogin('reviewer'); setShowProfileMenu(false); }}
                    className={`w-full text-left px-3 py-1.5 rounded text-xs transition ${user?.role === 'Senior Reviewer' ? 'bg-blue-600/20 text-blue-300 font-semibold' : 'text-slate-300 hover:bg-slate-700/50'}`}
                  >
                    David Vance (Senior Reviewer)
                  </button>
                  <button
                    onClick={() => { quickDemoLogin('admin'); setShowProfileMenu(false); }}
                    className={`w-full text-left px-3 py-1.5 rounded text-xs transition ${user?.role === 'Risk Administrator' ? 'bg-blue-600/20 text-blue-300 font-semibold' : 'text-slate-300 hover:bg-slate-700/50'}`}
                  >
                    Alex Mercer (Administrator)
                  </button>
                </div>
              </div>

              <div className="pt-1">
                <button
                  onClick={() => { onNavigate('settings'); setShowProfileMenu(false); }}
                  className="w-full text-left px-3 py-1.5 rounded text-xs text-slate-300 hover:bg-slate-700/50 transition"
                >
                  Preferences & Security
                </button>
                <button
                  onClick={() => { logout(); setShowProfileMenu(false); }}
                  className="w-full text-left px-3 py-1.5 rounded text-xs text-rose-400 hover:bg-rose-500/10 flex items-center gap-2 transition"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
