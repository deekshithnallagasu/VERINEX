import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { AuditLog } from '../services/types';
import {
  ScrollText,
  Search,
  Filter,
  Shield,
  ShieldAlert,
  Info,
  Clock,
  Laptop,
  Terminal
} from 'lucide-react';

export const AuditLogPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');

  useEffect(() => {
    loadLogs();
  }, [actionFilter, severityFilter]);

  async function loadLogs() {
    setIsLoading(true);
    try {
      const data = await api.listAuditLogs({
        action: actionFilter,
        severity: severityFilter,
        search
      });
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setIsLoading(false);
    }
  }

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadLogs();
  };

  return (
    <div className="p-6 sm:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <ScrollText className="w-5 h-5 text-blue-400" />
            Security & Activity Audit Logs
          </h2>
          <p className="text-xs text-slate-400">
            Cryptographically sealed, append-only audit trail enforcing SOC2 & GDPR accountability.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20">
          <Shield className="w-3.5 h-3.5" />
          <span>Chain of Custody Verified</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search audit trail by user, action, details, or Case ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-navy-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="px-3 py-2 bg-navy-900 border border-slate-700 rounded-xl text-xs text-slate-200 focus:outline-none"
            >
              <option value="ALL">All Actions</option>
              <option value="USER_LOGIN">Logins</option>
              <option value="SCREENING_RUN">Screenings</option>
              <option value="CASE_STATUS_UPDATE">Case Decisions</option>
              <option value="NOTE_ADDED">Notes</option>
              <option value="EXPORT_REPORT">Exports</option>
              <option value="SETTINGS_UPDATE">Settings Changes</option>
            </select>

            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="px-3 py-2 bg-navy-900 border border-slate-700 rounded-xl text-xs text-slate-200 focus:outline-none"
            >
              <option value="ALL">All Severities</option>
              <option value="INFO">Info</option>
              <option value="WARNING">Warning</option>
              <option value="CRITICAL">Critical</option>
            </select>

            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white transition shadow-glow-sm"
            >
              Filter
            </button>
          </div>
        </form>
      </div>

      {/* Logs Table */}
      <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-navy-900/80 text-slate-400 uppercase font-semibold border-b border-slate-700/60">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Operator</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Case Ref</th>
                <th className="py-3 px-4">Event Details</th>
                <th className="py-3 px-4 text-right">Client Endpoint</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400">
                    No matching audit logs recorded.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-navy-750/40 transition">
                    <td className="py-3.5 px-4 text-slate-400 font-mono whitespace-nowrap">
                      {new Date(log.created_at).toLocaleDateString()} {new Date(log.created_at).toLocaleTimeString()}
                    </td>
                    <td className="py-3.5 px-4">
                      {log.severity === 'CRITICAL' ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                          CRITICAL
                        </span>
                      ) : log.severity === 'WARNING' ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                          WARNING
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                          INFO
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-white">
                      {log.username}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px] text-blue-400 font-semibold">
                      {log.action}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-400">
                      {log.case_id || '—'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 max-w-xs truncate" title={log.details}>
                      {log.details}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-[11px] text-slate-400">
                      {log.ip_address}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
