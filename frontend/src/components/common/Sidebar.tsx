import React from 'react';
import {
  LayoutDashboard,
  FileSearch,
  FolderCheck,
  BarChart3,
  ScrollText,
  Settings,
  Shield,
  ShieldCheck,
  LogOut
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  currentTab: string;
  onNavigate: (tab: string) => void;
  pendingCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onNavigate, pendingCount = 0 }) => {
  const { logout, user } = useAuth();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'screening', label: 'Document Screening', icon: FileSearch, badge: 'AI Engine' },
    { id: 'cases', label: 'Cases & Reviews', icon: FolderCheck, count: pendingCount },
    { id: 'reports', label: 'Reports & Export', icon: BarChart3 },
    { id: 'audit', label: 'Audit / Activity Log', icon: ScrollText },
    { id: 'settings', label: 'System Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-navy-950 border-r border-slate-800/80 flex flex-col justify-between flex-shrink-0 min-h-screen">
      <div>
        {/* VERINEX Brand Header */}
        <div className="h-20 flex items-center gap-3 px-6 border-b border-slate-800/80 bg-navy-900/40">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 shadow-glow-sm text-white">
            <Shield className="w-5 h-5" />
            <div className="absolute inset-0 rounded-xl ring-1 ring-white/20"></div>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-lg font-black tracking-widest text-white">VERINEX</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">AI</span>
            </div>
            <p className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Identity Screening</p>
          </div>
        </div>

        {/* Navigation links */}
        <nav className="p-4 space-y-1.5">
          <div className="px-3 pb-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            Core Modules
          </div>

          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 font-semibold shadow-glow-sm'
                    : 'text-slate-300 hover:text-white hover:bg-navy-800/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/15 text-purple-300 font-mono border border-purple-500/20">
                    {item.badge}
                  </span>
                )}
                {item.count !== undefined && item.count > 0 && (
                  <span className="text-[11px] px-2 py-0.5 rounded-full bg-blue-600 text-white font-bold">
                    {item.count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer / Defensive Safeguard Banner */}
      <div className="p-4 border-t border-slate-800/80 space-y-3">
        {/* Compliance Guard Status Widget */}
        <div className="p-3 rounded-xl bg-navy-900/90 border border-slate-800 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-300 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Defensive Shield
            </span>
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          </div>
          <p className="text-[10px] text-slate-400 leading-relaxed">
            Non-adversarial screening mode. Zero document generation/forgery capabilities.
          </p>
        </div>

        {/* User logout */}
        <div className="flex items-center justify-between px-1">
          <div className="text-left">
            <div className="text-xs font-semibold text-slate-200 truncate max-w-[120px]">{user?.full_name}</div>
            <div className="text-[10px] text-slate-400 truncate max-w-[120px]">{user?.role}</div>
          </div>
          <button
            onClick={logout}
            title="Log out of session"
            className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
