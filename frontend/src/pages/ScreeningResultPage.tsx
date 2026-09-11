import React, { useState } from 'react';
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
  Flag,
  ZoomIn,
  Layers,
  Camera,
  Fingerprint,
  FileCheck2,
  Eye,
  Sliders,
  Clock
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
  const [activeForensicTab, setActiveForensicTab] = useState<'annotated' | 'ela' | 'original'>('annotated');
  const [showBoundingBoxes, setShowBoundingBoxes] = useState(true);
  const [isZoomed, setIsZoomed] = useState(false);

  const data = caseData.extracted_data || {};
  const mrz = caseData.mrz_result || {};
  const tampering = caseData.tampering_result || {};
  const face = caseData.face_result || {};
  const validation = caseData.validation_result || {};

  const isHighRisk = caseData.overall_risk_level === 'HIGH' || caseData.risk_score >= 60;
  const isMedRisk = caseData.overall_risk_level === 'MEDIUM' || (caseData.risk_score >= 30 && caseData.risk_score < 60);
  
  // Standardized Risk Terminology
  const riskLabel = isHighRisk ? 'HIGH RISK' : (isMedRisk ? 'REVIEW REQUIRED' : 'LOW RISK');

  const previewSrc = caseData.file_url;
  const annotatedSrc = caseData.annotated_file_url || previewSrc;
  const elaSrc = tampering?.ela_heatmap_url || previewSrc;

  const currentForensicView = activeForensicTab === 'ela' ? elaSrc : (activeForensicTab === 'annotated' ? annotatedSrc : previewSrc);

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

      {/* Prominent Ethical AI Decision Support Banner */}
      <div className="p-4 rounded-xl bg-navy-900/90 border border-blue-500/30 text-xs text-slate-300 flex items-start gap-3 backdrop-blur-md shadow-glow-sm">
        <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 flex-shrink-0">
          <Info className="w-5 h-5" />
        </div>
        <div className="space-y-1">
          <p className="font-bold text-white uppercase tracking-wider text-[11px] flex items-center gap-2">
            <span>AI-Assisted Decision Support Notice</span>
            <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 text-[10px] font-mono lowercase">advisory-only</span>
          </p>
          <p className="leading-relaxed text-slate-300">
            Results are screening indicators and do not constitute definitive legal determination. The system never claims 100% fake detection certainty. High-risk indicators require secondary adjudication by an authorized officer.
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
                <span className="text-3xl font-black tracking-tight text-white font-mono">
                  {caseData.risk_score}
                </span>
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                  / 100 Risk
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className={`px-2.5 py-1 rounded text-xs font-bold font-mono tracking-wider ${
                  isHighRisk ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' :
                  (isMedRisk ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40')
                }`}>
                  {riskLabel}
                </span>
                <StatusBadge status={caseData.status} />
              </div>
              <p className="text-xs text-slate-400 font-mono">Case #{caseData.id}</p>
              <p className="text-xs text-slate-300 font-medium">
                Recommendation: <span className="font-bold text-white">{caseData.recommendation || (isHighRisk ? 'Mandatory Secondary Inspection' : (isMedRisk ? 'Manual Verification Required' : 'Screening Clear'))}</span>
              </p>
            </div>
          </div>

          {/* Granular Telemetry Badges (7 Cols) */}
          <div className="md:col-span-7 grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-3.5 rounded-xl bg-navy-900/60 border border-slate-700/50">
              <p className="text-[11px] text-slate-400 font-medium">AI Confidence</p>
              <p className="text-xl font-bold text-white mt-1 font-mono">{caseData.ai_confidence}%</p>
              <div className="w-full bg-slate-800 h-1 rounded-full mt-2 overflow-hidden">
                <div className="bg-blue-500 h-full" style={{ width: `${caseData.ai_confidence}%` }} />
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-navy-900/60 border border-slate-700/50">
              <p className="text-[11px] text-slate-400 font-medium">Image Quality</p>
              <p className="text-xl font-bold text-white mt-1 font-mono">{caseData.document_quality_score}%</p>
              <div className="w-full bg-slate-800 h-1 rounded-full mt-2 overflow-hidden">
                <div className="bg-emerald-500 h-full" style={{ width: `${caseData.document_quality_score}%` }} />
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-navy-900/60 border border-slate-700/50">
              <p className="text-[11px] text-slate-400 font-medium">RapidOCR Conf.</p>
              <p className="text-xl font-bold text-white mt-1 font-mono">{caseData.ocr_confidence}%</p>
              <div className="w-full bg-slate-800 h-1 rounded-full mt-2 overflow-hidden">
                <div className="bg-purple-500 h-full" style={{ width: `${caseData.ocr_confidence}%` }} />
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-navy-900/60 border border-slate-700/50">
              <p className="text-[11px] text-slate-400 font-medium">Tamper Score</p>
              <p className={`text-xl font-bold mt-1 font-mono ${tampering?.tampering_score > 30 ? 'text-rose-400' : 'text-emerald-400'}`}>
                {tampering?.tampering_score !== undefined ? `${tampering.tampering_score}/100` : '0.0'}
              </p>
              <div className="w-full bg-slate-800 h-1 rounded-full mt-2 overflow-hidden">
                <div className={`${tampering?.tampering_score > 30 ? 'bg-rose-500' : 'bg-emerald-500'} h-full`} style={{ width: `${Math.min(100, tampering?.tampering_score || 5)}%` }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* DOCUMENT TYPE AUTHENTICATION STATUS BANNER */}
      {caseData.classification_result && (
        <div className={`p-4 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs ${
          caseData.classification_result.validation_status === 'DOCUMENT_TYPE_CONFIRMED'
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
            : caseData.classification_result.validation_status === 'DOCUMENT_TYPE_MISMATCH' || caseData.classification_result.validation_status === 'UNKNOWN_DOCUMENT'
            ? 'bg-rose-500/15 border-rose-500/30 text-rose-300'
            : 'bg-amber-500/15 border-amber-500/30 text-amber-300'
        }`}>
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-5 h-5 flex-shrink-0 text-blue-400" />
            <div>
              <span className="font-bold text-white">Document Type Authentication: </span>
              <span>
                Selected: <strong className="text-white">{caseData.selected_document_type || caseData.document_type}</strong> | Detected: <strong className="text-white">{caseData.classification_result.detected_document_name || caseData.document_type}</strong>
              </span>
              {caseData.classification_result.warning_message && (
                <p className="text-[11px] mt-0.5 text-rose-200">{caseData.classification_result.warning_message}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2 font-mono">
            <span className="px-2 py-0.5 rounded bg-navy-900 border border-slate-700 text-[11px]">
              Confidence: {caseData.classification_result.classification_confidence}%
            </span>
            <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
              caseData.classification_result.validation_status === 'DOCUMENT_TYPE_CONFIRMED'
                ? 'bg-emerald-500/20 text-emerald-300'
                : 'bg-rose-500/20 text-rose-300'
            }`}>
              {caseData.classification_result.validation_status}
            </span>
          </div>
        </div>
      )}

      {/* PHASE 18: SIDE-BY-SIDE FORENSIC INSPECTOR COMPONENT */}
      <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-400" />
              Side-by-Side Visual Forensics & ELA Inspection
            </h3>
            <p className="text-xs text-slate-400">
              Compare pristine original specimen against Error Level Analysis (ELA) and localized tampering overlays
            </p>
          </div>

          <div className="flex items-center gap-2 bg-navy-900/80 p-1 rounded-xl border border-slate-700/60">
            <button
              onClick={() => setActiveForensicTab('annotated')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${
                activeForensicTab === 'annotated' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Forensic Overlay
            </button>
            <button
              onClick={() => setActiveForensicTab('ela')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${
                activeForensicTab === 'ela' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              ELA Heatmap
            </button>
            <button
              onClick={() => setActiveForensicTab('original')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${
                activeForensicTab === 'original' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Original Only
            </button>
          </div>
        </div>

        {/* Side-by-side viewports */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left Viewport: Original Document */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-300 font-semibold px-1">
              <span>Original Document (Visual Zone)</span>
              <span className="text-slate-400 text-[11px]">{caseData.document_type}</span>
            </div>
            <div className="relative rounded-xl overflow-hidden border border-slate-700/80 bg-navy-950 flex items-center justify-center p-2 min-h-[260px]">
              <img
                src={previewSrc}
                alt="Original Document Specimen"
                className="max-h-[340px] w-auto object-contain rounded shadow-lg"
              />
            </div>
          </div>

          {/* Right Viewport: Forensic Analysis / Heatmap */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-300 font-semibold px-1">
              <span className="flex items-center gap-1.5">
                <span>Forensic Analysis View ({activeForensicTab.toUpperCase()})</span>
                {tampering?.suspicious_regions?.length > 0 && (
                  <span className="px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 text-[10px] border border-rose-500/40">
                    {tampering.suspicious_regions.length} anomalies detected
                  </span>
                )}
              </span>
              <span className="text-xs font-mono text-purple-400">
                {activeForensicTab === 'ela' ? 'Compression Gradient' : 'Tamper Detection Boxes'}
              </span>
            </div>
            <div className="relative rounded-xl overflow-hidden border border-slate-700/80 bg-navy-950 flex items-center justify-center p-2 min-h-[260px]">
              <img
                src={currentForensicView}
                alt="Forensic Analysis Specimen"
                className="max-h-[340px] w-auto object-contain rounded shadow-lg"
              />
            </div>
          </div>
        </div>

        {/* Forensic Metadata & Legend */}
        <div className="pt-2 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-400 border-t border-slate-700/50">
          <div className="flex items-center gap-4">
            <span className="font-semibold text-slate-300">Severity Legend:</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Low Risk (Uniform)</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Review (Edge variance)</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> High (Localized ELA Divergence)</span>
          </div>
          {tampering?.forensic_details?.software && (
            <div className="text-amber-300 font-mono text-[11px]">
              Signature Detected: {tampering.forensic_details.software}
            </div>
          )}
        </div>
      </div>

      {/* Grid: Extracted Identity Fields Left, Multi-Layer Security Checks Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Extracted Structured Data (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-5">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-400" />
                Extracted Identity Fields (OCR)
              </h3>
              <span className="text-[11px] px-2 py-0.5 rounded bg-navy-900 text-slate-400 font-mono">
                {caseData.document_type}
              </span>
            </div>

            <div className="space-y-3.5">
              <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40 flex items-start gap-3">
                <User className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                <div className="min-w-0">
                  <p className="text-[11px] font-medium text-slate-400">Full Name</p>
                  <p className="text-xs font-bold text-white truncate mt-0.5">
                    {data.full_name || 'Unspecified'}
                  </p>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40 flex items-start gap-3">
                <CreditCard className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                <div className="min-w-0">
                  <p className="text-[11px] font-medium text-slate-400">Document Identifier</p>
                  <p className="text-xs font-bold text-white font-mono truncate mt-0.5">
                    {data.document_number || 'Unspecified'}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40 flex items-start gap-3">
                  <Calendar className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="text-[11px] font-medium text-slate-400">Date of Birth</p>
                    <p className="text-xs font-bold text-white font-mono mt-0.5">
                      {data.date_of_birth || 'Unspecified'}
                    </p>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40 flex items-start gap-3">
                  <Clock className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="text-[11px] font-medium text-slate-400">Expiry Date</p>
                    <p className="text-xs font-bold text-white font-mono mt-0.5">
                      {data.expiry_date || 'Unspecified'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40 flex items-start gap-3">
                  <MapPin className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="text-[11px] font-medium text-slate-400">Nationality</p>
                    <p className="text-xs font-bold text-white truncate mt-0.5">
                      {data.nationality || 'Unspecified'}
                    </p>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40 flex items-start gap-3">
                  <User className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="text-[11px] font-medium text-slate-400">Gender</p>
                    <p className="text-xs font-bold text-white mt-0.5">
                      {data.gender || 'Unspecified'}
                    </p>
                  </div>
                </div>
              </div>

              {data.issuing_authority && (
                <div className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40 flex items-start gap-3">
                  <Building className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="text-[11px] font-medium text-slate-400">Issuing Authority</p>
                    <p className="text-xs font-bold text-white truncate mt-0.5">
                      {data.issuing_authority}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Biometric Face Verification Card */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
                <Camera className="w-4 h-4 text-blue-400" />
                1:1 Facial Biometric Verification
              </h3>
              <span className={`text-[11px] px-2 py-0.5 rounded font-bold ${
                face?.status === 'MATCH' ? 'bg-emerald-500/20 text-emerald-300' :
                (face?.status === 'MISMATCH' ? 'bg-rose-500/20 text-rose-300' : 'bg-slate-800 text-slate-400')
              }`}>
                {face?.status || 'NOT AVAILABLE'}
              </span>
            </div>

            <div className="flex items-center justify-around py-2">
              <div className="text-center space-y-1">
                <div className="w-20 h-24 rounded-xl border border-slate-700 bg-navy-950 overflow-hidden flex items-center justify-center">
                  {caseData.face_file_url || face?.doc_face_url ? (
                    <img src={caseData.face_file_url || face?.doc_face_url} alt="Document Portrait" className="w-full h-full object-cover" />
                  ) : (
                    <User className="w-8 h-8 text-slate-600" />
                  )}
                </div>
                <p className="text-[10px] text-slate-400 font-medium">Document Portrait</p>
              </div>

              <div className="flex flex-col items-center justify-center space-y-1">
                <Fingerprint className="w-6 h-6 text-blue-400" />
                <span className="text-xs font-bold font-mono text-white">
                  {face?.similarity_percent !== undefined ? `${face.similarity_percent}%` : '--'}
                </span>
                <span className="text-[10px] text-slate-400">Cosine Match</span>
              </div>

              <div className="text-center space-y-1">
                <div className="w-20 h-24 rounded-xl border border-slate-700 bg-navy-950 overflow-hidden flex items-center justify-center">
                  {face?.probe_face_url ? (
                    <img src={face.probe_face_url} alt="Live Probe" className="w-full h-full object-cover" />
                  ) : (
                    <div className="text-center p-2">
                      <Camera className="w-6 h-6 text-slate-600 mx-auto" />
                      <span className="text-[9px] text-slate-500 mt-1 block">No Probe</span>
                    </div>
                  )}
                </div>
                <p className="text-[10px] text-slate-400 font-medium">Probe Selfie</p>
              </div>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed pt-1">
              Deep facial embeddings via OpenCV SFace. Cosine similarity threshold: <span className="text-white font-mono font-bold">80.0%</span>.
            </p>
          </div>
        </div>

        {/* Right Column: MRZ + Multi-Layer Checks + Plain Language Flags (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* ICAO 9303 MRZ Verification Card */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Machine Readable Zone (ICAO 9303)
              </h3>
              <span className={`text-[11px] px-2.5 py-0.5 rounded font-bold font-mono ${
                mrz?.overall_status === 'PASS' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                (mrz?.overall_status === 'FAIL' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-slate-800 text-slate-400')
              }`}>
                {mrz?.overall_status || 'NOT DETECTED'}
              </span>
            </div>

            {mrz?.detected ? (
              <div className="space-y-3">
                <div className="p-3 rounded-xl bg-navy-950 border border-slate-800 font-mono text-xs text-blue-300 space-y-1">
                  {mrz?.lines?.map((line: string, idx: number) => (
                    <div key={idx} className="tracking-widest overflow-x-auto">{line}</div>
                  ))}
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 text-xs">
                  <div className="p-2.5 rounded-lg bg-navy-900/60 border border-slate-700/40 flex items-center justify-between">
                    <span className="text-slate-400">Doc Number CD</span>
                    {mrz?.check_digits?.document_number ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-400" />
                    )}
                  </div>

                  <div className="p-2.5 rounded-lg bg-navy-900/60 border border-slate-700/40 flex items-center justify-between">
                    <span className="text-slate-400">DOB CD</span>
                    {mrz?.check_digits?.date_of_birth ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-400" />
                    )}
                  </div>

                  <div className="p-2.5 rounded-lg bg-navy-900/60 border border-slate-700/40 flex items-center justify-between">
                    <span className="text-slate-400">Expiry CD</span>
                    {mrz?.check_digits?.expiry_date ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-400" />
                    )}
                  </div>

                  <div className="p-2.5 rounded-lg bg-navy-900/60 border border-slate-700/40 flex items-center justify-between">
                    <span className="text-slate-400">Composite CD</span>
                    {mrz?.check_digits?.composite ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-400" />
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">
                {mrz?.notice || 'No standard Machine Readable Zone detected on this document format.'}
              </p>
            )}
          </div>

          {/* WHY WAS THIS FLAGGED? Plain-Language Suspicious Indicators */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Why Was This Flagged? (Explainable Screening Indicators)
              </h3>
              <span className="text-[11px] px-2 py-0.5 rounded bg-navy-900 text-slate-400 font-mono">
                {caseData.suspicious_indicators?.length || 0} Indicators
              </span>
            </div>

            {caseData.suspicious_indicators && caseData.suspicious_indicators.length > 0 ? (
              <div className="space-y-3">
                {caseData.suspicious_indicators.map((ind: any, i: number) => {
                  const isCrit = ind.severity === 'HIGH' || ind.severity === 'CRITICAL';
                  return (
                    <div
                      key={i}
                      className={`p-4 rounded-xl border transition ${
                        isCrit
                          ? 'bg-rose-500/10 border-rose-500/30'
                          : 'bg-amber-500/10 border-amber-500/30'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        {isCrit ? (
                          <AlertOctagon className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
                        ) : (
                          <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                        )}
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-white">{ind.title}</span>
                            <span
                              className={`text-[10px] px-1.5 py-0.5 rounded font-mono uppercase ${
                                isCrit
                                  ? 'bg-rose-500/20 text-rose-300'
                                  : 'bg-amber-500/20 text-amber-300'
                              }`}
                            >
                              {ind.severity}
                            </span>
                          </div>
                          <p className="text-xs text-slate-300 leading-relaxed">{ind.explanation}</p>
                          {ind.recommendation && (
                            <p className="text-xs text-slate-400 pt-1 font-medium">
                              <span className="text-blue-400 font-semibold">Recommended Action: </span>
                              {ind.recommendation}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                <span>No suspicious tampering or identity inconsistencies identified. Document conforms to baseline security parameters.</span>
              </div>
            )}
          </div>

          {/* Multi-Layer System Consistency Checks */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2 border-b border-slate-700/60 pb-3">
              <Sparkles className="w-4 h-4 text-purple-400" />
              Multi-Layer Verification Checks
            </h3>

            <div className="space-y-2.5">
              {caseData.consistency_checks?.map((check: any, idx: number) => {
                const isPass = check.status === 'PASS';
                const isWarn = check.status === 'WARN';
                return (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-navy-900/60 border border-slate-700/40 flex items-center justify-between text-xs gap-3"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      {isPass ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                      ) : isWarn ? (
                        <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                      )}
                      <div className="truncate">
                        <span className="font-semibold text-white">{check.check_name}</span>
                        <p className="text-[11px] text-slate-400 truncate">{check.details}</p>
                      </div>
                    </div>

                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold flex-shrink-0 ${
                        isPass
                          ? 'bg-emerald-500/15 text-emerald-300'
                          : isWarn
                          ? 'bg-amber-500/15 text-amber-300'
                          : 'bg-rose-500/15 text-rose-300'
                      }`}
                    >
                      {check.status}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
