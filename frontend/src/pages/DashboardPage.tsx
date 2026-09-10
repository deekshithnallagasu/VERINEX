import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DashboardStats, ScreeningCase } from '../services/types';
import { StatCard } from '../components/common/StatCard';
import { RiskBadge, StatusBadge } from '../components/common/Badge';
import {
  FileCheck2,
  CheckCircle2,
  AlertOctagon,
  Clock,
  Sparkles,
  ArrowRight,
  Shield,
  Search,
  ExternalLink,
  Filter
} from 'lucide-react';

interface DashboardPageProps {
  onNavigate: (tab: string, caseId?: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.getDashboardStats();
        setStats(data);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="p-8 space-y-6 animate-pulse">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-navy-800/60 rounded-xl"></div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-72 bg-navy-800/60 rounded-2xl"></div>
          <div className="h-72 bg-navy-800/60 rounded-2xl"></div>
        </div>
        <div className="h-80 bg-navy-800/60 rounded-2xl"></div>
      </div>
    );
  }

  const metrics = stats?.metrics || {
    total_screenings: 0,
    verified_documents: 0,
    suspicious_documents: 0,
    pending_reviews: 0,
    verification_rate: 0,
    avg_processing_time_sec: 2.4
  };

  const riskDist = stats?.risk_distribution || { LOW: 0, MEDIUM: 0, HIGH: 0 };
  const totalRiskCount = riskDist.LOW + riskDist.MEDIUM + riskDist.HIGH || 1;
  const lowPercent = Math.round((riskDist.LOW / totalRiskCount) * 100);
  const medPercent = Math.round((riskDist.MEDIUM / totalRiskCount) * 100);
  const highPercent = Math.round((riskDist.HIGH / totalRiskCount) * 100);

  // Filter recent screenings
  const filteredCases = (stats?.recent_screenings || []).filter((c) => {
    const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter;
    const matchesSearch =
      c.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.file_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.extracted_data.full_name && c.extracted_data.full_name.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="p-6 sm:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Quick Launch Callout Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-900/40 via-indigo-900/30 to-purple-900/40 border border-blue-500/20 p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 backdrop-blur-xl">
        <div className="space-y-1 z-10">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-500/30">
              Interactive Defensive Demo
            </span>
            <span className="text-xs text-slate-400">Zero Configuration Ready</span>
          </div>
          <h2 className="text-xl font-bold text-white">Test Automated AI Screening Workflow</h2>
          <p className="text-xs text-slate-300 max-w-2xl">
            Choose from 4 pre-configured fictional identity specimens (clean passports, expired licenses, tampered MRZs, or degraded photos) or upload your own file to experience OCR parsing and transparent risk scoring.
          </p>
        </div>
        <button
          onClick={() => onNavigate('screening')}
          className="z-10 flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-semibold text-xs shadow-glow-sm transition duration-150 flex-shrink-0"
        >
          <Sparkles className="w-4 h-4" />
          <span>Launch Screening</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* 4 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Screenings"
          value={metrics.total_screenings}
          subtitle="Processed identity documents"
          icon={FileCheck2}
          accentColor="blue"
          trend={{ value: "+14.2% this week", positive: true }}
        />
        <StatCard
          title="Verified Documents"
          value={metrics.verified_documents}
          subtitle={`${metrics.verification_rate}% acceptance rate`}
          icon={CheckCircle2}
          accentColor="emerald"
          trend={{ value: "+6.8%", positive: true }}
        />
        <StatCard
          title="Suspicious Documents"
          value={metrics.suspicious_documents}
          subtitle="Flagged or elevated risk"
          icon={AlertOctagon}
          accentColor="rose"
          trend={{ value: "Priority review", positive: false }}
        />
        <StatCard
          title="Pending Reviews"
          value={metrics.pending_reviews}
          subtitle="Awaiting human decision"
          icon={Clock}
          accentColor="amber"
        />
      </div>

      {/* Analytics Row: Screening Trends & Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Chart (SVG Visual) */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white tracking-wide">Screening Volume & Telemetry</h3>
              <p className="text-xs text-slate-400">Daily verification vs suspicious document flags</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Verified
              </span>
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> Suspicious
              </span>
            </div>
          </div>

          {/* Render Visual Bar / Column Chart */}
          <div className="h-56 flex items-end justify-between gap-3 pt-4 px-2 border-b border-slate-700/60">
            {(stats?.activity_chart || []).map((item, idx) => {
              const maxVal = 25;
              const vHeight = Math.min(100, Math.max(15, (item.verified / maxVal) * 100));
              const sHeight = Math.min(60, Math.max(5, (item.suspicious / maxVal) * 100));
              return (
                <div key={idx} className="flex-1 flex flex-col items-center gap-2 group relative">
                  {/* Tooltip on hover */}
                  <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-navy-950 text-white text-[10px] py-1 px-2 rounded border border-slate-700 pointer-events-none whitespace-nowrap z-20 shadow-lg">
                    {item.day}: {item.verified} verified, {item.suspicious} flagged
                  </div>

                  <div className="w-full max-w-[28px] flex items-end justify-center gap-1 h-44">
                    <div
                      style={{ height: `${vHeight}%` }}
                      className="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t-md transition-all duration-300 group-hover:brightness-125 shadow-glow-sm"
                    ></div>
                    <div
                      style={{ height: `${sHeight}%` }}
                      className="w-full bg-gradient-to-t from-rose-600 to-rose-400 rounded-t-md transition-all duration-300 group-hover:brightness-125"
                    ></div>
                  </div>
                  <span className="text-[11px] font-medium text-slate-400 truncate">{item.day}</span>
                </div>
              );
            })}
          </div>
          <div className="flex items-center justify-between pt-3 text-xs text-slate-400">
            <span>Avg throughput: 2.4s per document</span>
            <span className="text-emerald-400 font-medium">99.8% System Uptime</span>
          </div>
        </div>

        {/* Risk Distribution Card */}
        <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-white tracking-wide">Risk Distribution</h3>
              <span className="text-[11px] font-mono text-slate-400">{metrics.total_screenings} total</span>
            </div>

            {/* Segmented Bar */}
            <div className="space-y-2 mt-4">
              <div className="h-3.5 w-full bg-slate-800 rounded-full overflow-hidden flex">
                <div
                  style={{ width: `${lowPercent}%` }}
                  className="bg-emerald-500 transition-all duration-500"
                  title={`Low: ${lowPercent}%`}
                ></div>
                <div
                  style={{ width: `${medPercent}%` }}
                  className="bg-amber-500 transition-all duration-500"
                  title={`Medium: ${medPercent}%`}
                ></div>
                <div
                  style={{ width: `${highPercent}%` }}
                  className="bg-rose-500 transition-all duration-500"
                  title={`High: ${highPercent}%`}
                ></div>
              </div>
            </div>

            {/* Breakdown details */}
            <div className="mt-6 space-y-3.5">
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-navy-900/60 border border-slate-700/40">
                <div className="flex items-center gap-2.5">
                  <span className="w-3 h-3 rounded-full bg-emerald-400"></span>
                  <span className="text-xs font-semibold text-slate-200">Low Risk (0-29)</span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-white">{riskDist.LOW}</span>
                  <span className="text-[10px] text-slate-400 ml-1.5">({lowPercent}%)</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-2.5 rounded-xl bg-navy-900/60 border border-slate-700/40">
                <div className="flex items-center gap-2.5">
                  <span className="w-3 h-3 rounded-full bg-amber-400"></span>
                  <span className="text-xs font-semibold text-slate-200">Medium Risk (30-69)</span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-white">{riskDist.MEDIUM}</span>
                  <span className="text-[10px] text-slate-400 ml-1.5">({medPercent}%)</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-2.5 rounded-xl bg-navy-900/60 border border-slate-700/40">
                <div className="flex items-center gap-2.5">
                  <span className="w-3 h-3 rounded-full bg-rose-400 shadow-glow-danger"></span>
                  <span className="text-xs font-semibold text-slate-200">High Risk (70-100)</span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-white">{riskDist.HIGH}</span>
                  <span className="text-[10px] text-slate-400 ml-1.5">({highPercent}%)</span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-700/60 text-[11px] text-slate-400 flex items-center justify-between">
            <span>Threshold engine: Active</span>
            <button
              onClick={() => onNavigate('settings')}
              className="text-blue-400 hover:text-blue-300 transition underline underline-offset-2"
            >
              Tune Parameters
            </button>
          </div>
        </div>
      </div>

      {/* Recent Screenings Table */}
      <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-bold text-white tracking-wide">Recent Identity Screenings</h3>
            <p className="text-xs text-slate-400">Live screening stream from automated ingest and user uploads</p>
          </div>

          {/* Search and Filters */}
          <div className="flex items-center gap-2.5 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-64">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search case, holder name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 bg-navy-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-2.5 py-1.5 bg-navy-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="ALL">All Status</option>
              <option value="VERIFIED">Verified</option>
              <option value="IN_REVIEW">In Review</option>
              <option value="FLAGGED">Flagged</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-navy-900/80 text-slate-400 uppercase font-semibold border-b border-slate-700/60">
              <tr>
                <th className="py-3 px-4">Case ID</th>
                <th className="py-3 px-4">Subject Name</th>
                <th className="py-3 px-4">Doc Type</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Date & Time</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {filteredCases.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400">
                    No matching screening cases found.
                  </td>
                </tr>
              ) : (
                filteredCases.map((c) => (
                  <tr key={c.id} className="hover:bg-navy-750/40 transition">
                    <td className="py-3.5 px-4 font-mono font-semibold text-blue-400">
                      {c.id}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-white">
                      {c.extracted_data.full_name || 'Anonymous Specimen'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">
                      {c.document_type.replace('_', ' ')}
                    </td>
                    <td className="py-3.5 px-4">
                      <RiskBadge level={c.overall_risk_level} score={c.risk_score} size="sm" />
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={c.status} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {new Date(c.created_at).toLocaleDateString()} {new Date(c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => onNavigate('cases', c.id)}
                        className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-slate-700/60 hover:bg-blue-600 hover:text-white text-slate-200 transition font-medium"
                      >
                        <span>Investigate</span>
                        <ExternalLink className="w-3 h-3" />
                      </button>
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
