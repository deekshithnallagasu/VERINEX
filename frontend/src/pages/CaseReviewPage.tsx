import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ScreeningCase, CaseStatus } from '../services/types';
import { RiskBadge, StatusBadge } from '../components/common/Badge';
import {
  FolderCheck,
  Check,
  Flag,
  RotateCcw,
  XCircle,
  MessageSquare,
  Clock,
  User,
  Shield,
  Search,
  ExternalLink,
  ChevronRight,
  Send
} from 'lucide-react';

interface CaseReviewPageProps {
  initialCaseId?: string | null;
  onNavigate: (tab: string, caseId?: string) => void;
}

export const CaseReviewPage: React.FC<CaseReviewPageProps> = ({ initialCaseId, onNavigate }) => {
  const [cases, setCases] = useState<ScreeningCase[]>([]);
  const [activeCase, setActiveCase] = useState<ScreeningCase | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [noteText, setNoteText] = useState('');
  const [isSubmittingNote, setIsSubmittingNote] = useState(false);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadCases();
  }, []);

  async function loadCases() {
    setIsLoading(true);
    try {
      const list = await api.listScreenings();
      setCases(list);

      if (initialCaseId) {
        const found = list.find((c) => c.id === initialCaseId);
        if (found) setActiveCase(found);
        else if (list.length > 0) setActiveCase(list[0]);
      } else if (list.length > 0) {
        setActiveCase(list[0]);
      }
    } catch (err) {
      console.error('Failed to load cases:', err);
    } finally {
      setIsLoading(false);
    }
  }

  const handleUpdateStatus = async (status: CaseStatus) => {
    if (!activeCase) return;
    try {
      const updated = await api.updateCaseStatus(
        activeCase.id,
        status,
        `Status updated to ${status} by operator.`
      );
      setActiveCase(updated);
      setCases((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeCase || !noteText.trim()) return;

    setIsSubmittingNote(true);
    try {
      await api.addCaseNote(activeCase.id, noteText.trim());
      // Refresh active case details
      const refreshed = await api.getScreeningCase(activeCase.id);
      setActiveCase(refreshed);
      setNoteText('');
    } catch (err) {
      console.error('Failed to add note:', err);
    } finally {
      setIsSubmittingNote(false);
    }
  };

  const filteredCases = cases.filter((c) => {
    const matchStatus = statusFilter === 'ALL' || c.status === statusFilter;
    const matchSearch =
      c.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.extracted_data.full_name && c.extracted_data.full_name.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchStatus && matchSearch;
  });

  if (isLoading) {
    return <div className="p-8 text-center text-slate-400">Loading case adjudication queue...</div>;
  }

  const previewSrc = activeCase?.file_url || '';

  return (
    <div className="p-6 sm:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <FolderCheck className="w-5 h-5 text-blue-400" />
            Case Review & Forensic Adjudication
          </h2>
          <p className="text-xs text-slate-400">
            Investigate extracted fields, cross-check optical signals, record reviewer notes, and render authoritative decisions.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 bg-navy-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none"
          >
            <option value="ALL">All Cases ({cases.length})</option>
            <option value="IN_REVIEW">In Review</option>
            <option value="FLAGGED">Flagged</option>
            <option value="VERIFIED">Verified</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>
      </div>

      {/* Main Layout: Case List Sidebar (4 Cols) + Deep-Dive Workspace (8 Cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Case Queue List */}
        <div className="lg:col-span-4 p-4 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search by Case ID or name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 bg-navy-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="space-y-2 max-h-[70vh] overflow-y-auto pr-1">
            {filteredCases.map((c) => {
              const isSelected = activeCase?.id === c.id;
              return (
                <button
                  key={c.id}
                  onClick={() => setActiveCase(c)}
                  className={`w-full p-3 rounded-xl text-left border transition ${
                    isSelected
                      ? 'bg-blue-600/15 border-blue-500 shadow-glow-sm'
                      : 'bg-navy-900/60 border-slate-700/50 hover:bg-navy-750'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono font-bold text-blue-400">{c.id}</span>
                    <StatusBadge status={c.status} size="sm" />
                  </div>
                  <div className="text-xs font-semibold text-white truncate">
                    {c.extracted_data.full_name || 'Anonymous Specimen'}
                  </div>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="text-[10px] text-slate-400">{c.document_type.replace('_', ' ')}</span>
                    <RiskBadge level={c.overall_risk_level} score={c.risk_score} size="sm" />
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right: Active Case Investigator Workspace */}
        {activeCase ? (
          <div className="lg:col-span-8 space-y-6">
            {/* Case Header Card */}
            <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-700/60">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-base font-bold text-white font-mono">{activeCase.id}</span>
                    <StatusBadge status={activeCase.status} />
                    <RiskBadge level={activeCase.overall_risk_level} score={activeCase.risk_score} size="sm" />
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Uploaded: {new Date(activeCase.created_at).toLocaleString()} • Document Type: {activeCase.document_type}
                  </p>
                </div>

                {/* Adjudication Decision Buttons */}
                <div className="flex items-center gap-2 flex-wrap">
                  <button
                    onClick={() => handleUpdateStatus('VERIFIED')}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition flex items-center gap-1 shadow-glow-success"
                  >
                    <Check className="w-3.5 h-3.5" />
                    Approve
                  </button>
                  <button
                    onClick={() => handleUpdateStatus('FLAGGED')}
                    className="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs transition flex items-center gap-1"
                  >
                    <Flag className="w-3.5 h-3.5" />
                    Flag
                  </button>
                  <button
                    onClick={() => handleUpdateStatus('IN_REVIEW')}
                    className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition flex items-center gap-1"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    Manual Review
                  </button>
                  <button
                    onClick={() => handleUpdateStatus('REJECTED')}
                    className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs transition flex items-center gap-1 shadow-glow-danger"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    Reject
                  </button>
                </div>
              </div>

              {/* Side-by-side: Document Visual Inspector vs Extracted Data */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Visual Specimen with Bounding Box Overlay */}
                <div className="space-y-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    Visual Inspection Zone (VIZ)
                  </span>
                  <div className="h-56 rounded-xl bg-navy-950 border border-slate-800 overflow-hidden flex items-center justify-center relative group">
                    <img
                      src={previewSrc}
                      alt="Case specimen"
                      className="w-full h-full object-contain p-2 transition-transform duration-300 group-hover:scale-105"
                    />
                    <div className="absolute bottom-2 right-2 px-2 py-0.5 rounded bg-navy-900/80 text-[10px] text-slate-300 border border-slate-700">
                      Quality: {activeCase.document_quality_score}%
                    </div>
                  </div>
                </div>

                {/* Extracted Details */}
                <div className="space-y-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    Extracted Subject Identity
                  </span>
                  <div className="p-3.5 rounded-xl bg-navy-900/70 border border-slate-700/50 space-y-2 text-xs">
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase font-semibold">Legal Name</span>
                      <span className="text-white font-bold">{activeCase.extracted_data.full_name || 'N/A'}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Doc Number</span>
                        <span className="text-white font-mono">{activeCase.extracted_data.document_number || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">DOB</span>
                        <span className="text-white">{activeCase.extracted_data.date_of_birth || 'N/A'}</span>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Expiration</span>
                        <span className="text-white">{activeCase.extracted_data.expiry_date || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Authority</span>
                        <span className="text-white truncate block">{activeCase.extracted_data.issuing_authority || 'Standard'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Reviewer Notes & Timeline Tabs / Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Reviewer Notes */}
              <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-blue-400" />
                    Reviewer Notes & Rationale
                  </h3>
                  <span className="text-xs text-slate-400">{activeCase.notes?.length || 0} Notes</span>
                </div>

                {/* Add Note Input */}
                <form onSubmit={handleAddNote} className="space-y-2">
                  <textarea
                    rows={3}
                    value={noteText}
                    onChange={(e) => setNoteText(e.target.value)}
                    placeholder="Enter adjudication findings, verification references, or escalate instructions..."
                    className="w-full px-3 py-2 bg-navy-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={isSubmittingNote || !noteText.trim()}
                      className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition flex items-center gap-1.5 disabled:opacity-50"
                    >
                      <Send className="w-3 h-3" />
                      <span>Record Note</span>
                    </button>
                  </div>
                </form>

                {/* Notes History */}
                <div className="space-y-2.5 max-h-52 overflow-y-auto pr-1">
                  {(!activeCase.notes || activeCase.notes.length === 0) ? (
                    <p className="text-xs text-slate-500 text-center py-4">No notes recorded yet.</p>
                  ) : (
                    activeCase.notes.map((n) => (
                      <div key={n.id} className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40 space-y-1">
                        <div className="flex items-center justify-between text-[10px] text-slate-400">
                          <span className="font-semibold text-blue-300">{n.author_name} ({n.author_role})</span>
                          <span>{new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                        <p className="text-xs text-slate-200 leading-relaxed">{n.note_text}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* End-to-End Timeline */}
              <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
                <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
                  <Clock className="w-4 h-4 text-purple-400" />
                  Screening Lifecycle Timeline
                </h3>
                <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                  {(activeCase.timeline || []).map((t, idx) => (
                    <div key={idx} className="flex items-start gap-3 text-xs">
                      <div className="w-2 h-2 rounded-full bg-blue-400 mt-1.5 flex-shrink-0"></div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-200">{t.step}</span>
                          <span className="text-[10px] text-slate-500">{t.timestamp}</span>
                        </div>
                        <p className="text-slate-400 text-[11px] leading-snug mt-0.5">{t.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="lg:col-span-8 p-12 text-center text-slate-400 rounded-2xl bg-navy-800/80 border border-slate-700/60">
            Select a case from the queue to view details.
          </div>
        )}
      </div>
    </div>
  );
};
