import React from 'react';
import { ScreeningCase } from '../services/types';
import { RiskBadge, StatusBadge } from '../components/common/Badge';
import {
  ShieldCheck,
  AlertTriangle,
  AlertOctagon,
  CheckCircle2,
  XCircle,
  FileText,
  User,
  Calendar,
  CreditCard,
  MapPin,
  Building,
  ArrowLeft,
  ExternalLink,
  Sparkles,
  Info,
  Check,
  Send,
  Flag
} from 'lucide-react';

interface ScreeningResultPageProps {
  caseData: ScreeningCase;
  onNavigate: (tab: string, caseId?: string) => void;
  onStatusUpdate: (caseId: string, status: any) => Promise<void>;
}

export const ScreeningResultPage: React.FC<ScreeningResultPageProps> = ({
  caseData,
  onNavigate,
  onStatusUpdate
}) => {
  const data = caseData.extracted_data || {};
  const isHighRisk = caseData.overall_risk_level === 'HIGH';
  const isMedRisk = caseData.overall_risk_level === 'MEDIUM';

  const previewSrc = caseData.file_url;

  return (
    <div className="p-6 sm:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header Navigation Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <button
          onClick={() => onNavigate('screening')}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Screening Ingest</span>
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('reports', caseData.id)}
            className="px-3.5 py-1.5 rounded-lg bg-navy-800 hover:bg-navy-750 border border-slate-700 text-xs font-medium text-slate-200 transition flex items-center gap-1.5"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Generate Report</span>
          </button>
          <button
            onClick={() => onNavigate('cases', caseData.id)}
            className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-glow-sm transition flex items-center gap-1.5"
          >
            <span>Open Case Review</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Prominent Ethical AI Disclaimer Banner */}
      <div className="p-4 rounded-xl bg-navy-900/90 border border-blue-500/30 text-xs text-slate-300 flex items-start gap-3 backdrop-blur-md shadow-glow-sm">
        <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 flex-shrink-0">
          <Info className="w-5 h-5" />
        </div>
        <div className="space-y-1">
          <p className="font-bold text-white uppercase tracking-wider text-[11px]">
            AI-Assisted Decision Support Notice
          </p>
          <p className="leading-relaxed text-slate-300">
            This evaluation reflects automated optical analysis and rule consistency heuristics. The system does not possess absolute legal certainty and does not definitively declare any subject fraudulent. High-risk indicators require secondary adjudication by a qualified human document specialist.
          </p>
        </div>
      </div>

      {/* Top Assessment Overview Card */}
      <div className="p-6 sm:p-8 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
          {/* Risk Level Badge & Score Gauge (5 Cols) */}
          <div className="md:col-span-5 flex items-center gap-6 border-b md:border-b-0 md:border-r border-slate-700/60 pb-6 md:pb-0 pr-0 md:pr-6">
            <div className="relative flex items-center justify-center">
              {/* Circular Gauge Representation */}
              <div
                className={`w-28 h-28 rounded-full border-4 flex flex-col items-center justify-center ${
                  isHighRisk
                    ? 'border-rose-500/60 bg-rose-500/10 shadow-glow-danger'
                    : isMedRisk
                    ? 'border-amber-500/60 bg-amber-500/10'
                    : 'border-emerald-500/60 bg-emerald-500/10 shadow-glow-success'
                }`}
              >
                <span className="text-3xl font-extrabold text-white">{caseData.risk_score}</span>
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Risk Score</span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-[11px] font-mono text-slate-400">CASE REF: {caseData.id}</div>
              <div>
                <RiskBadge level={caseData.overall_risk_level} size="lg" />
              </div>
              <div className="flex items-center gap-2 pt-1">
                <StatusBadge status={caseData.status} size="sm" />
                <span className="text-[11px] text-slate-400">• {caseData.document_type.replace('_', ' ')}</span>
              </div>
            </div>
          </div>

          {/* Forensic Confidence & Quality Telemetry (7 Cols) */}
          <div className="md:col-span-7 grid grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-navy-900/60 border border-slate-700/40 text-center">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                AI Confidence
              </span>
              <span className="text-2xl font-bold text-blue-400 mt-1 block">
                {caseData.ai_confidence}%
              </span>
              <span className="text-[10px] text-slate-400">Algorithmic synthesis</span>
            </div>

            <div className="p-4 rounded-xl bg-navy-900/60 border border-slate-700/40 text-center">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                Document Quality
              </span>
              <span
                className={`text-2xl font-bold mt-1 block ${
                  caseData.document_quality_score < 60 ? 'text-amber-400' : 'text-emerald-400'
                }`}
              >
                {caseData.document_quality_score}%
              </span>
              <span className="text-[10px] text-slate-400">Sharpness & lighting</span>
            </div>

            <div className="p-4 rounded-xl bg-navy-900/60 border border-slate-700/40 text-center">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                OCR Confidence
              </span>
              <span className="text-2xl font-bold text-purple-400 mt-1 block">
                {caseData.ocr_confidence}%
              </span>
              <span className="text-[10px] text-slate-400">Character recognition</span>
            </div>
          </div>
        </div>
      </div>

      {/* Split Section: Extracted Information vs Document Preview & Consistency */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Extracted Structured Information (6 Cols) */}
        <div className="lg:col-span-6 space-y-6">
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-700/60">
              <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-400" />
                Extracted Identity Fields (OCR)
              </h3>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                100% Extracted
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <User className="w-3 h-3 text-blue-400" /> Full Holder Name
                </span>
                <span className="text-sm font-bold text-white mt-1 block truncate">
                  {data.full_name || 'N/A'}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <CreditCard className="w-3 h-3 text-purple-400" /> Document Number
                </span>
                <span className="text-sm font-mono font-bold text-white mt-1 block">
                  {data.document_number || 'N/A'}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Calendar className="w-3 h-3 text-cyan-400" /> Date of Birth
                </span>
                <span className="text-sm font-bold text-white mt-1 block">
                  {data.date_of_birth || 'N/A'}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Calendar className="w-3 h-3 text-rose-400" /> Expiration Date
                </span>
                <span className="text-sm font-bold text-white mt-1 block">
                  {data.expiry_date || 'N/A'}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Building className="w-3 h-3 text-amber-400" /> Issuing Authority
                </span>
                <span className="text-xs font-medium text-slate-200 mt-1 block truncate">
                  {data.issuing_authority || 'Standard Authority'}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <MapPin className="w-3 h-3 text-emerald-400" /> Jurisdiction / Nationality
                </span>
                <span className="text-xs font-medium text-slate-200 mt-1 block truncate">
                  {data.nationality || 'USA'}
                </span>
              </div>
            </div>

            {/* Address */}
            {data.address && (
              <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                  Residential Address
                </span>
                <span className="text-xs text-slate-200 mt-0.5 block">{data.address}</span>
              </div>
            )}

            {/* Machine Readable Zone (MRZ) if present */}
            {(data.mrz_line1 || data.mrz_line2) && (
              <div className="p-3.5 rounded-xl bg-navy-950 border border-slate-800 space-y-1">
                <span className="text-[10px] font-mono font-bold text-blue-400 uppercase">
                  Machine Readable Zone (MRZ - ICAO 9303)
                </span>
                <div className="font-mono text-xs text-emerald-400 bg-black/40 p-2.5 rounded-lg overflow-x-auto space-y-0.5">
                  <div>{data.mrz_line1}</div>
                  <div>{data.mrz_line2}</div>
                </div>
              </div>
            )}
          </div>

          {/* Suspicious Indicators / Flags List */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
                <AlertOctagon className="w-4 h-4 text-rose-400" />
                Suspicious Indicators & Plain-Language Flags
              </h3>
              <span className="text-xs font-bold text-slate-400">
                {caseData.suspicious_indicators.length} Flagged
              </span>
            </div>

            {caseData.suspicious_indicators.length === 0 ? (
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>No critical tampering or inconsistency flags identified.</span>
              </div>
            ) : (
              <div className="space-y-3">
                {caseData.suspicious_indicators.map((ind, idx) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-xl border space-y-2 ${
                      ind.severity === 'HIGH'
                        ? 'bg-rose-500/10 border-rose-500/30'
                        : 'bg-amber-500/10 border-amber-500/30'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <AlertTriangle
                          className={`w-4 h-4 ${
                            ind.severity === 'HIGH' ? 'text-rose-400' : 'text-amber-400'
                          }`}
                        />
                        <span className="text-xs font-bold text-white">{ind.title}</span>
                      </div>
                      <span
                        className={`text-[9px] font-bold px-2 py-0.5 rounded ${
                          ind.severity === 'HIGH'
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        }`}
                      >
                        {ind.severity} SEVERITY
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">{ind.explanation}</p>
                    {ind.recommendation && (
                      <div className="pt-2 border-t border-slate-700/40 text-[11px] text-slate-400">
                        <span className="font-semibold text-slate-300">Action Protocol: </span>
                        {ind.recommendation}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Specimen Preview & Consistency Checks (6 Cols) */}
        <div className="lg:col-span-6 space-y-6">
          {/* Specimen Visual Preview */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white tracking-wide">Document Specimen View</h3>
              <span className="text-xs text-slate-400">{caseData.file_name}</span>
            </div>
            <div className="h-64 rounded-xl bg-navy-950 border border-slate-800 overflow-hidden flex items-center justify-center relative">
              <img src={previewSrc} alt="Screened document" className="w-full h-full object-contain p-2" />
            </div>
          </div>

          {/* Multi-Layer Consistency Analysis Table */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Automated Forensic Checks
            </h3>
            <div className="divide-y divide-slate-700/50">
              {caseData.consistency_checks.map((check, idx) => (
                <div key={idx} className="py-3 flex items-start justify-between gap-3">
                  <div className="space-y-0.5">
                    <span className="text-xs font-semibold text-slate-200 block">
                      {check.check_name}
                    </span>
                    <span className="text-[11px] text-slate-400 block leading-snug">
                      {check.details}
                    </span>
                  </div>
                  <div>
                    {check.status === 'PASS' ? (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                        <CheckCircle2 className="w-3 h-3" /> PASS
                      </span>
                    ) : check.status === 'WARN' ? (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
                        <AlertTriangle className="w-3 h-3" /> WARN
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/15 text-rose-400 border border-rose-500/30">
                        <XCircle className="w-3 h-3" /> FAIL
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Human Review Decision Bar */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <h3 className="text-sm font-bold text-white tracking-wide">Adjudication & Routing</h3>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={async () => {
                  await onStatusUpdate(caseData.id, 'VERIFIED');
                  onNavigate('cases', caseData.id);
                }}
                className="py-2.5 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition flex items-center justify-center gap-1.5 shadow-glow-success"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Verify & Approve</span>
              </button>

              <button
                onClick={async () => {
                  await onStatusUpdate(caseData.id, 'FLAGGED');
                  onNavigate('cases', caseData.id);
                }}
                className="py-2.5 px-3 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs transition flex items-center justify-center gap-1.5 shadow-glow-danger"
              >
                <Flag className="w-3.5 h-3.5" />
                <span>Flag for Investigation</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
