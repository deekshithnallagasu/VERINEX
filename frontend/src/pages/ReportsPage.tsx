import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ScreeningCase } from '../services/types';
import { RiskBadge, StatusBadge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import {
  BarChart3,
  Search,
  Download,
  FileText,
  Filter,
  Eye,
  CheckCircle2,
  AlertOctagon,
  Clock,
  ExternalLink,
  Printer
} from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<ScreeningCase[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [docTypeFilter, setDocTypeFilter] = useState('ALL');

  // Modal for report preview
  const [selectedReport, setSelectedReport] = useState<ScreeningCase | null>(null);

  useEffect(() => {
    loadReports();
  }, [statusFilter, riskFilter, docTypeFilter]);

  async function loadReports() {
    setIsLoading(true);
    try {
      const data = await api.listReports({
        status: statusFilter,
        risk_level: riskFilter,
        doc_type: docTypeFilter,
        search
      });
      setReports(data.reports || []);
      setSummary(data.summary || null);
    } catch (err) {
      console.error('Failed to load reports:', err);
    } finally {
      setIsLoading(false);
    }
  }

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadReports();
  };

  const handleExport = (caseId: string, format: 'json' | 'csv') => {
    const url = api.getReportExportUrl(caseId, format);
    window.open(url, '_blank');
  };

  return (
    <div className="p-6 sm:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            Verification & Compliance Reports
          </h2>
          <p className="text-xs text-slate-400">
            Historical audit reports, regulatory compliance packages, and multi-format export utilities.
          </p>
        </div>
      </div>

      {/* Summary Statistics Cards */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-navy-800/80 border border-slate-700/60 flex items-center justify-between">
            <div>
              <span className="text-[10px] uppercase font-semibold text-slate-400 block">Total Reports</span>
              <span className="text-2xl font-bold text-white mt-1 block">{summary.total_reports}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-blue-500/10 text-blue-400">
              <FileText className="w-5 h-5" />
            </div>
          </div>

          <div className="p-4 rounded-xl bg-navy-800/80 border border-slate-700/60 flex items-center justify-between">
            <div>
              <span className="text-[10px] uppercase font-semibold text-slate-400 block">Verified Valid</span>
              <span className="text-2xl font-bold text-emerald-400 mt-1 block">{summary.verified_count}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>

          <div className="p-4 rounded-xl bg-navy-800/80 border border-slate-700/60 flex items-center justify-between">
            <div>
              <span className="text-[10px] uppercase font-semibold text-slate-400 block">Flagged Cases</span>
              <span className="text-2xl font-bold text-rose-400 mt-1 block">{summary.flagged_count}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-rose-500/10 text-rose-400">
              <AlertOctagon className="w-5 h-5" />
            </div>
          </div>

          <div className="p-4 rounded-xl bg-navy-800/80 border border-slate-700/60 flex items-center justify-between">
            <div>
              <span className="text-[10px] uppercase font-semibold text-slate-400 block">In Review Queue</span>
              <span className="text-2xl font-bold text-amber-400 mt-1 block">{summary.in_review_count}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400">
              <Clock className="w-5 h-5" />
            </div>
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search reports by Case ID, name, or filename..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-navy-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 bg-navy-900 border border-slate-700 rounded-xl text-xs text-slate-200 focus:outline-none"
            >
              <option value="ALL">Status: All</option>
              <option value="VERIFIED">Verified</option>
              <option value="IN_REVIEW">In Review</option>
              <option value="FLAGGED">Flagged</option>
              <option value="REJECTED">Rejected</option>
            </select>

            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="px-3 py-2 bg-navy-900 border border-slate-700 rounded-xl text-xs text-slate-200 focus:outline-none"
            >
              <option value="ALL">Risk: All</option>
              <option value="LOW">Low Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="HIGH">High Risk</option>
            </select>

            <select
              value={docTypeFilter}
              onChange={(e) => setDocTypeFilter(e.target.value)}
              className="px-3 py-2 bg-navy-900 border border-slate-700 rounded-xl text-xs text-slate-200 focus:outline-none"
            >
              <option value="ALL">Doc: All Types</option>
              <option value="PASSPORT">Passport</option>
              <option value="DRIVERS_LICENSE">Driver's License</option>
              <option value="NATIONAL_ID">National ID</option>
              <option value="RESIDENCE_PERMIT">Residence Permit</option>
            </select>

            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white transition shadow-glow-sm"
            >
              Apply Filter
            </button>
          </div>
        </form>
      </div>

      {/* Reports Table */}
      <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-navy-900/80 text-slate-400 uppercase font-semibold border-b border-slate-700/60">
              <tr>
                <th className="py-3 px-4">Report ID</th>
                <th className="py-3 px-4">Case ID</th>
                <th className="py-3 px-4">Subject Name</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Generated</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {reports.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400">
                    No matching compliance reports found.
                  </td>
                </tr>
              ) : (
                reports.map((r) => (
                  <tr key={r.id} className="hover:bg-navy-750/40 transition">
                    <td className="py-3.5 px-4 font-mono font-bold text-white">
                      REP-{r.id}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-blue-400">{r.id}</td>
                    <td className="py-3.5 px-4 font-medium text-white">
                      {r.extracted_data.full_name || 'Anonymous'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">{r.document_type.replace('_', ' ')}</td>
                    <td className="py-3.5 px-4">
                      <RiskBadge level={r.overall_risk_level} score={r.risk_score} size="sm" />
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={r.status} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {new Date(r.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-1.5">
                      <button
                        onClick={() => setSelectedReport(r)}
                        className="p-1.5 rounded-lg bg-slate-700/60 hover:bg-slate-700 text-slate-300 transition"
                        title="View Full Report Summary"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleExport(r.id, 'json')}
                        className="p-1.5 rounded-lg bg-slate-700/60 hover:bg-blue-600 hover:text-white text-slate-300 transition"
                        title="Download JSON Report"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Report Detail Preview Modal */}
      {selectedReport && (
        <Modal
          isOpen={!!selectedReport}
          onClose={() => setSelectedReport(null)}
          title={`Forensic Screening Report: REP-${selectedReport.id}`}
          maxWidth="2xl"
        >
          <div className="space-y-5 text-xs text-slate-300">
            {/* Disclaimer */}
            <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300">
              <span className="font-bold text-white">Ethical Screening Statement: </span>
              Generated strictly for defensive verification. AI risk scoring provides decision-support only.
            </div>

            {/* Top Details */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-xl bg-navy-900 border border-slate-700/60">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">Case ID</span>
                <span className="font-mono text-white font-bold">{selectedReport.id}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">Risk Score</span>
                <span className="text-white font-bold">{selectedReport.risk_score} / 100</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">AI Confidence</span>
                <span className="text-white font-bold">{selectedReport.ai_confidence}%</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">Adjudication</span>
                <StatusBadge status={selectedReport.status} size="sm" />
              </div>
            </div>

            {/* Subject Data */}
            <div className="p-4 rounded-xl bg-navy-900 border border-slate-700/60 space-y-2">
              <h4 className="font-bold text-white text-xs uppercase tracking-wider">
                Extracted Credential Data
              </h4>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <span className="text-slate-400 block text-[10px]">Legal Name</span>
                  <span className="font-semibold text-white">{selectedReport.extracted_data.full_name || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Document Number</span>
                  <span className="font-mono text-white">{selectedReport.extracted_data.document_number || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Date of Birth</span>
                  <span className="text-white">{selectedReport.extracted_data.date_of_birth || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Expiration Date</span>
                  <span className="text-white">{selectedReport.extracted_data.expiry_date || 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Suspicious Flags */}
            <div className="space-y-2">
              <h4 className="font-bold text-white text-xs uppercase tracking-wider">
                Recorded Risk Flags ({selectedReport.suspicious_indicators.length})
              </h4>
              {selectedReport.suspicious_indicators.length === 0 ? (
                <p className="text-emerald-400 text-xs">No tampering or inconsistency indicators recorded.</p>
              ) : (
                selectedReport.suspicious_indicators.map((ind, i) => (
                  <div key={i} className="p-2.5 rounded-lg bg-navy-900 border border-slate-700 text-xs">
                    <span className="font-bold text-rose-400">{ind.title}: </span>
                    <span>{ind.explanation}</span>
                  </div>
                ))
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-700">
              <button
                onClick={() => handleExport(selectedReport.id, 'csv')}
                className="px-3.5 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold flex items-center gap-1.5 transition"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export CSV</span>
              </button>
              <button
                onClick={() => handleExport(selectedReport.id, 'json')}
                className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1.5 transition"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export JSON</span>
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
