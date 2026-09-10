import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { SampleDocumentItem, ScreeningCase, DocumentType } from '../services/types';
import {
  UploadCloud,
  FileText,
  Sparkles,
  Shield,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  FileCheck,
  Eye,
  RefreshCw,
  Info,
  X
} from 'lucide-react';

interface ScreeningPageProps {
  onScreeningComplete: (newCase: ScreeningCase) => void;
}

export const ScreeningPage: React.FC<ScreeningPageProps> = ({ onScreeningComplete }) => {
  const [samples, setSamples] = useState<SampleDocumentItem[]>([]);
  const [selectedSample, setSelectedSample] = useState<SampleDocumentItem | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [docType, setDocType] = useState<DocumentType>('PASSPORT');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const steps = [
    { title: 'Upload & Format Validation', desc: 'Verifying file integrity and MIME type' },
    { title: 'Image Quality & Glare Inspection', desc: 'Forensic sharpness, glare, and resolution testing' },
    { title: 'Optical Character Recognition (OCR)', desc: 'Reading visual zones and machine-readable text' },
    { title: 'Structured Data Extraction', desc: 'Parsing name, DOB, doc number, and dates' },
    { title: 'Consistency & Tamper Analysis', desc: 'Cross-checking MRZ parity and temporal validity' },
    { title: 'AI-Assisted Risk Scoring', desc: 'Synthesizing explainable decision-support metrics' }
  ];

  useEffect(() => {
    async function loadSamples() {
      try {
        const list = await api.getSamplePresets();
        setSamples(list);
        if (list.length > 0) {
          setSelectedSample(list[0]);
          setDocType(list[0].document_type);
          setPreviewUrl(list[0].image_url);
        }
      } catch (err) {
        console.error('Error fetching sample presets:', err);
      }
    }
    loadSamples();
  }, []);

  const handleSelectSample = (sample: SampleDocumentItem) => {
    setSelectedFile(null);
    setSelectedSample(sample);
    setDocType(sample.document_type);
    setPreviewUrl(sample.image_url);
    setErrorMessage(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check format
    const validFormats = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];
    if (!validFormats.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png|webp|pdf)$/i)) {
      setErrorMessage('Unsupported file format! Please upload a valid JPG, PNG, or PDF identity document.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setErrorMessage('File size exceeds 10MB limit.');
      return;
    }

    setErrorMessage(null);
    setSelectedSample(null);
    setSelectedFile(file);

    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      const input = fileInputRef.current;
      if (input) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        input.files = dataTransfer.files;
        handleFileChange({ target: input } as any);
      }
    }
  };

  const runScreening = async () => {
    if (!selectedSample && !selectedFile) {
      setErrorMessage('Please choose a fictional sample document or upload a test file.');
      return;
    }

    setErrorMessage(null);
    setIsProcessing(true);
    setProcessingStep(0);

    // Animate through the workflow steps
    for (let i = 0; i < steps.length; i++) {
      setProcessingStep(i);
      await new Promise((resolve) => setTimeout(resolve, 450));
    }

    try {
      let result: ScreeningCase;
      if (selectedSample) {
        result = await api.runDemoSample(selectedSample.id);
      } else if (selectedFile) {
        result = await api.uploadAndScreen(selectedFile, docType);
      } else {
        throw new Error('No document chosen');
      }

      // Small pause for completion feedback
      await new Promise((resolve) => setTimeout(resolve, 300));
      onScreeningComplete(result);
    } catch (err: any) {
      setErrorMessage(err.message || 'Screening pipeline encountered an error.');
      setIsProcessing(false);
    }
  };

  return (
    <div className="p-6 sm:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Defensive Purpose Notice */}
      <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300 flex items-start gap-3">
        <Info className="w-5 h-5 flex-shrink-0 text-blue-400 mt-0.5" />
        <div>
          <span className="font-bold text-white">Ethical Defensive Screening Notice: </span>
          This system verifies and inspects identity documents against known tampering and quality anomalies. All test specimens provided below are fictional. VERINEX does not forge, edit, or fabricate identity papers.
        </div>
      </div>

      {/* Error state alert */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 text-xs text-rose-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Main Grid: Upload & Picker Left, Preview & Parameters Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Sample Gallery + Upload Zone (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Quick Fictional Test Specimen Gallery */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-blue-400" />
                  1-Click Fictional Test Documents
                </h3>
                <p className="text-xs text-slate-400">Select any pre-configured specimen to test immediately</p>
              </div>
              <span className="text-[11px] px-2 py-0.5 rounded bg-navy-900 text-blue-400 font-semibold border border-blue-500/20">
                4 Scenarios
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {samples.map((sample) => {
                const isSelected = selectedSample?.id === sample.id;
                return (
                  <button
                    key={sample.id}
                    type="button"
                    onClick={() => handleSelectSample(sample)}
                    className={`p-3.5 rounded-xl text-left border transition duration-200 flex flex-col justify-between ${
                      isSelected
                        ? 'bg-blue-600/15 border-blue-500 shadow-glow-sm ring-1 ring-blue-400/30'
                        : 'bg-navy-900/70 border-slate-700/60 hover:border-slate-600 hover:bg-navy-850'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-xs font-bold text-white truncate max-w-[150px]">
                          {sample.title}
                        </span>
                        <span
                          className={`text-[9px] font-semibold px-1.5 py-0.5 rounded ${
                            sample.expected_risk === 'LOW'
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : sample.expected_risk === 'MEDIUM'
                              ? 'bg-amber-500/20 text-amber-400'
                              : 'bg-rose-500/20 text-rose-400'
                          }`}
                        >
                          {sample.expected_risk} RISK
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                        {sample.description}
                      </p>
                    </div>
                    <div className="mt-2.5 pt-2 border-t border-slate-700/40 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                      <span>{sample.badge_label}</span>
                      <span className="text-blue-400 font-semibold">
                        {isSelected ? '✓ Selected' : 'Click to Load'}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Or Drag & Drop Custom Upload Area */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white tracking-wide">Or Upload Document File</h3>
                <p className="text-xs text-slate-400">Supports JPG, PNG, WEBP, or PDF up to 10MB</p>
              </div>
              {selectedFile && (
                <button
                  onClick={() => {
                    setSelectedFile(null);
                    setPreviewUrl(null);
                  }}
                  className="text-xs text-rose-400 hover:text-rose-300"
                >
                  Clear File
                </button>
              )}
            </div>

            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition duration-200 ${
                selectedFile
                  ? 'border-blue-500 bg-blue-500/5'
                  : 'border-slate-700 hover:border-blue-400/50 hover:bg-navy-750/30'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".jpg,.jpeg,.png,.webp,.pdf"
                onChange={handleFileChange}
                className="hidden"
              />
              <div className="flex flex-col items-center justify-center space-y-2.5">
                <div className="p-3.5 rounded-full bg-blue-500/10 text-blue-400 shadow-glow-sm">
                  <UploadCloud className="w-6 h-6" />
                </div>
                {selectedFile ? (
                  <div>
                    <p className="text-sm font-semibold text-white">{selectedFile.name}</p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {(selectedFile.size / 1024).toFixed(1)} KB • Click or drag to replace
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm font-semibold text-white">Drag & drop document file here</p>
                    <p className="text-xs text-slate-400 mt-1">
                      or <span className="text-blue-400 underline underline-offset-2">browse computer</span>
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Parameters & Live Processing Stepper (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Document Parameters Card */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <h3 className="text-sm font-bold text-white tracking-wide">Screening Configuration</h3>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Document Classification
              </label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value as DocumentType)}
                className="w-full px-3.5 py-2.5 bg-navy-900 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
              >
                <option value="PASSPORT">Passport (ICAO Doc 9303)</option>
                <option value="DRIVERS_LICENSE">Driver's License (State / National)</option>
                <option value="NATIONAL_ID">National Identity Card (Dual Zone)</option>
                <option value="RESIDENCE_PERMIT">Residence Permit / Work Authorization</option>
              </select>
            </div>

            {/* Document Preview Card */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Specimen Visual Preview
              </label>
              <div className="h-52 rounded-xl bg-navy-950 border border-slate-800 overflow-hidden flex items-center justify-center relative group">
                {previewUrl ? (
                  <img
                    src={previewUrl}
                    alt="Document preview"
                    className="w-full h-full object-contain p-2"
                  />
                ) : (
                  <div className="text-center text-slate-500 text-xs">
                    <FileText className="w-8 h-8 mx-auto mb-1.5 opacity-40" />
                    <span>No document selected</span>
                  </div>
                )}
                {previewUrl && (
                  <div className="absolute top-2 right-2 px-2 py-1 rounded bg-navy-900/80 backdrop-blur text-[10px] text-slate-300 border border-slate-700">
                    Live Preview
                  </div>
                )}
              </div>
            </div>

            {/* Launch Screening Button */}
            <button
              type="button"
              disabled={isProcessing || (!selectedSample && !selectedFile)}
              onClick={runScreening}
              className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-bold text-sm shadow-glow-sm transition duration-150 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-white" />
                  <span>Processing AI Screening...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Start AI Screening Pipeline</span>
                </>
              )}
            </button>
          </div>

          {/* Workflow Stepper */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <h3 className="text-sm font-bold text-white tracking-wide">Processing Workflow Pipeline</h3>
            <div className="space-y-3">
              {steps.map((step, idx) => {
                const isCurrent = isProcessing && processingStep === idx;
                const isDone = isProcessing && processingStep > idx;
                return (
                  <div key={idx} className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      {isDone ? (
                        <div className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center text-[10px] font-bold">
                          ✓
                        </div>
                      ) : isCurrent ? (
                        <div className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500 flex items-center justify-center animate-pulse">
                          <span className="w-2 h-2 rounded-full bg-blue-400"></span>
                        </div>
                      ) : (
                        <div className="w-5 h-5 rounded-full bg-slate-800 text-slate-400 border border-slate-700 flex items-center justify-center text-[10px] font-medium">
                          {idx + 1}
                        </div>
                      )}
                    </div>
                    <div>
                      <p
                        className={`text-xs font-semibold ${
                          isCurrent ? 'text-blue-400' : isDone ? 'text-slate-200' : 'text-slate-400'
                        }`}
                      >
                        {step.title}
                      </p>
                      <p className="text-[11px] text-slate-400">{step.desc}</p>
                    </div>
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
