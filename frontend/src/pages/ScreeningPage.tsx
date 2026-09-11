import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { SampleDocumentItem, ScreeningCase, DocumentType, DocumentValidationResult } from '../services/types';
import {
  UploadCloud,
  FileText,
  Sparkles,
  Shield,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  ArrowRight,
  FileCheck,
  Eye,
  RefreshCw,
  Info,
  X,
  Camera,
  User,
  Video,
  Check,
  HelpCircle,
  RotateCcw
} from 'lucide-react';

interface ScreeningPageProps {
  onScreeningComplete: (newCase: ScreeningCase) => void;
}

export const ScreeningPage: React.FC<ScreeningPageProps> = ({ onScreeningComplete }) => {
  const [samples, setSamples] = useState<SampleDocumentItem[]>([]);
  const [selectedSample, setSelectedSample] = useState<SampleDocumentItem | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [probeFaceFile, setProbeFaceFile] = useState<File | null>(null);
  const [probePreviewUrl, setProbePreviewUrl] = useState<string | null>(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [docType, setDocType] = useState<DocumentType>('PASSPORT');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Document Type Authentication State
  const [validationResult, setValidationResult] = useState<DocumentValidationResult | null>(null);
  const [isValidatingDocType, setIsValidatingDocType] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const probeInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const steps = [
    { title: 'Upload & Format Validation', desc: 'Verifying MIME type, dimensions, and payload integrity' },
    { title: 'Image Quality & Glare Inspection', desc: 'CLAHE, sharpness, glare, and resolution analysis' },
    { title: 'Document Type Classification', desc: 'Multi-modal feature inspection & independent AI type identification' },
    { title: 'Selected-vs-Detected Match', desc: 'Authoritative validation gatekeeper cross-check' },
    { title: 'RapidOCR Optical Recognition', desc: 'Deep learning OCR extraction of text lines & visual zones' },
    { title: 'Structured Field Extraction', desc: 'Parsing name, doc number, dates, and issuing authorities' },
    { title: 'Cross-Zone Parity Consistency', desc: 'Fuzzy matching visual names, doc numbers, and dates against MRZ' },
    { title: 'Tampering Forensics & ELA', desc: 'Error Level Analysis, compression anomaly clustering' },
    { title: 'Document Face & Biometrics', desc: 'YuNet face detection & SFace 1:1 biometric similarity' },
    { title: 'Multi-Signal Risk Fusion Engine', desc: 'Synthesizing explainable decision-support indicators' }
  ];

  // Helper to run independent Document Type Authentication
  const performDocTypeValidation = async (
    file: File | null,
    sample: SampleDocumentItem | null,
    selectedType: DocumentType
  ) => {
    if (!file && !sample) {
      setValidationResult(null);
      return;
    }
    setIsValidatingDocType(true);
    try {
      const res = await api.validateDocumentType(
        file || undefined,
        selectedType,
        sample ? sample.id : undefined
      );
      setValidationResult(res);
    } catch (err: any) {
      console.error('Doc type validation error:', err);
    } finally {
      setIsValidatingDocType(false);
    }
  };

  useEffect(() => {
    async function loadSamples() {
      try {
        const list = await api.getSamplePresets();
        setSamples(list);
        if (list.length > 0) {
          const first = list[0];
          setSelectedSample(first);
          setDocType(first.document_type);
          setPreviewUrl(first.image_url);
          // Run initial validation for default specimen
          performDocTypeValidation(null, first, first.document_type);
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
    // Align docType to sample's expected type initially, or keep selected
    const targetType = sample.document_type === 'UNKNOWN' ? 'PASSPORT' : sample.document_type;
    setDocType(targetType);
    setPreviewUrl(sample.image_url);
    setErrorMessage(null);
    performDocTypeValidation(null, sample, targetType);
  };

  const handleDocTypeChange = (newType: DocumentType) => {
    setDocType(newType);
    if (selectedFile || selectedSample) {
      performDocTypeValidation(selectedFile, selectedSample, newType);
    }
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

    // Trigger mandatory Document Type Authentication immediately
    performDocTypeValidation(file, null, docType);
  };

  const handleProbeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setProbeFaceFile(file);
    setProbePreviewUrl(URL.createObjectURL(file));
  };

  const startWebcam = async () => {
    try {
      setIsCameraActive(true);
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (err) {
      console.error('Webcam access error:', err);
      setIsCameraActive(false);
      setErrorMessage('Webcam access was denied or is unavailable. Please upload a selfie image instead.');
    }
  };

  const captureWebcam = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(videoRef.current, 0, 0);
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'webcam_probe.jpg', { type: 'image/jpeg' });
          setProbeFaceFile(file);
          setProbePreviewUrl(URL.createObjectURL(file));
          stopWebcam();
        }
      }, 'image/jpeg', 0.92);
    }
  };

  const stopWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
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

  const clearCurrentDocument = () => {
    setSelectedFile(null);
    setSelectedSample(null);
    setPreviewUrl(null);
    setValidationResult(null);
    setErrorMessage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const runScreening = async () => {
    if (!selectedSample && !selectedFile) {
      setErrorMessage('Please choose a fictional sample document or upload a test file.');
      return;
    }

    // Client-side guard: Cannot proceed if document type authentication failed
    if (
      validationResult &&
      (validationResult.validation_status === 'DOCUMENT_TYPE_MISMATCH' ||
        validationResult.validation_status === 'UNKNOWN_DOCUMENT')
    ) {
      setErrorMessage(
        validationResult.warning_message ||
          'Document type authentication failed. Please upload an authentic matching document before continuing.'
      );
      return;
    }

    setErrorMessage(null);
    setIsProcessing(true);
    setProcessingStep(0);

    // Animate through the workflow steps
    for (let i = 0; i < steps.length; i++) {
      setProcessingStep(i);
      await new Promise((resolve) => setTimeout(resolve, 340));
    }

    try {
      let result: ScreeningCase;
      if (selectedSample) {
        result = await api.runDemoSample(selectedSample.id);
      } else if (selectedFile) {
        result = await api.uploadAndScreen(selectedFile, docType, probeFaceFile);
      } else {
        throw new Error('No document chosen');
      }

      await new Promise((resolve) => setTimeout(resolve, 300));
      onScreeningComplete(result);
    } catch (err: any) {
      setErrorMessage(err.message || 'Screening pipeline encountered an error.');
      setIsProcessing(false);
    }
  };

  // Determine if launch button should be disabled
  const isMismatchOrInvalid = Boolean(
    validationResult &&
      (validationResult.validation_status === 'DOCUMENT_TYPE_MISMATCH' ||
        validationResult.validation_status === 'UNKNOWN_DOCUMENT')
  );

  const isLaunchDisabled = Boolean(
    isProcessing ||
      isValidatingDocType ||
      (!selectedSample && !selectedFile) ||
      isMismatchOrInvalid
  );

  return (
    <div className="p-6 sm:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Defensive Purpose Notice */}
      <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300 flex items-start gap-3">
        <Info className="w-5 h-5 flex-shrink-0 text-blue-400 mt-0.5" />
        <div>
          <span className="font-bold text-white">Ethical Defensive Screening & Authentication Notice: </span>
          VERINEX verifies and inspects identity documents against known tampering, mismatch, and quality anomalies. All test specimens are fictional. VERINEX independently classifies uploaded files and strictly rejects invalid or mismatched identity documents.
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

      {/* Main Grid: Upload & Picker Left, Parameters & Status Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Sample Gallery + Upload Zone (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Quick Fictional Test Specimen Gallery */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-blue-400" />
                  1-Click Fictional Test Specimen Gallery
                </h3>
                <p className="text-xs text-slate-400">Select any specimen to test immediate classification & validation</p>
              </div>
              <span className="text-[11px] px-2 py-0.5 rounded bg-navy-900 text-blue-400 font-semibold border border-blue-500/20">
                {samples.length} Scenarios
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[380px] overflow-y-auto pr-1">
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

          {/* Drag & Drop Custom Upload Area */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white tracking-wide">Upload Identity Document File</h3>
                <p className="text-xs text-slate-400">Supports JPG, PNG, WEBP, or PDF up to 10MB</p>
              </div>
              {selectedFile && (
                <button
                  type="button"
                  onClick={clearCurrentDocument}
                  className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1"
                >
                  <X className="w-3.5 h-3.5" /> Clear File
                </button>
              )}
            </div>

            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition duration-200 ${
                selectedFile
                  ? isMismatchOrInvalid
                    ? 'border-rose-500/80 bg-rose-500/5'
                    : 'border-blue-500 bg-blue-500/5'
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
                <div
                  className={`p-3.5 rounded-full shadow-glow-sm ${
                    isMismatchOrInvalid
                      ? 'bg-rose-500/15 text-rose-400'
                      : 'bg-blue-500/10 text-blue-400'
                  }`}
                >
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
                    <p className="text-sm font-semibold text-white">Drag & drop identity document file here</p>
                    <p className="text-xs text-slate-400 mt-1">
                      or <span className="text-blue-400 underline underline-offset-2">browse computer</span>
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Optional Biometric Probe */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
                  <User className="w-4 h-4 text-purple-400" />
                  Optional Biometric Probe (1:1 Face Verification)
                </h3>
                <p className="text-xs text-slate-400">Provide a live selfie to verify against the document photo</p>
              </div>
              {probePreviewUrl && (
                <button
                  type="button"
                  onClick={() => {
                    setProbeFaceFile(null);
                    setProbePreviewUrl(null);
                    stopWebcam();
                  }}
                  className="text-xs text-rose-400 hover:text-rose-300"
                >
                  Remove Probe
                </button>
              )}
            </div>

            {isCameraActive ? (
              <div className="space-y-3">
                <div className="relative rounded-xl overflow-hidden bg-black border border-slate-700 aspect-video flex items-center justify-center">
                  <video ref={videoRef} className="w-full h-full object-cover" autoPlay playsInline muted />
                  <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-rose-500/80 text-[10px] text-white font-mono flex items-center gap-1.5 animate-pulse">
                    <span className="w-2 h-2 rounded-full bg-white"></span> LIVE CAMERA
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={captureWebcam}
                    className="flex-1 py-2 px-4 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs flex items-center justify-center gap-2"
                  >
                    <Camera className="w-4 h-4" /> Capture Photo
                  </button>
                  <button
                    type="button"
                    onClick={stopWebcam}
                    className="py-2 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : probePreviewUrl ? (
              <div className="flex items-center gap-4 p-3 rounded-xl bg-navy-900/80 border border-purple-500/30">
                <img
                  src={probePreviewUrl}
                  alt="Probe selfie preview"
                  className="w-16 h-16 rounded-lg object-cover border border-purple-500/40"
                />
                <div className="space-y-1">
                  <p className="text-xs font-bold text-white flex items-center gap-1.5">
                    <Check className="w-3.5 h-3.5 text-emerald-400" /> Probe Photo Ready
                  </p>
                  <p className="text-[11px] text-slate-400">
                    Will be matched against document portrait with SFace 128D embeddings.
                  </p>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <input
                  ref={probeInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleProbeChange}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => probeInputRef.current?.click()}
                  className="p-3.5 rounded-xl border border-slate-700 hover:border-purple-400/50 bg-navy-900/60 hover:bg-navy-850 flex items-center gap-3 transition"
                >
                  <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
                    <User className="w-4 h-4" />
                  </div>
                  <div className="text-left">
                    <p className="text-xs font-semibold text-white">Upload Selfie</p>
                    <p className="text-[10px] text-slate-400">JPG, PNG from disk</p>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={startWebcam}
                  className="p-3.5 rounded-xl border border-slate-700 hover:border-purple-400/50 bg-navy-900/60 hover:bg-navy-850 flex items-center gap-3 transition"
                >
                  <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
                    <Video className="w-4 h-4" />
                  </div>
                  <div className="text-left">
                    <p className="text-xs font-semibold text-white">Use Webcam</p>
                    <p className="text-[10px] text-slate-400">Capture live selfie</p>
                  </div>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Parameters, Immediate Document Type Validation, & Stepper (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Document Parameters Card */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-5">
            <h3 className="text-sm font-bold text-white tracking-wide flex items-center justify-between">
              <span>Screening Configuration</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono">
                Mandatory Type Auth
              </span>
            </h3>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Expected Document Type (User Selection)
              </label>
              <select
                value={docType}
                onChange={(e) => handleDocTypeChange(e.target.value as DocumentType)}
                className="w-full px-3.5 py-2.5 bg-navy-900 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500 font-medium"
              >
                <option value="PASSPORT">Passport (ICAO Doc 9303)</option>
                <option value="AADHAAR">Aadhaar Card (UIDAI / India)</option>
                <option value="PAN_CARD">Permanent Account Number (PAN Card)</option>
                <option value="DRIVERS_LICENSE">Driver's License / Driving Licence</option>
                <option value="VOTER_ID">Voter ID Card (Election Commission / EPIC)</option>
                <option value="NATIONAL_ID">National Identity Card (Dual Zone)</option>
                <option value="RESIDENCE_PERMIT">Residence Permit / Work Authorization</option>
              </select>
            </div>

            {/* MANDATORY DOCUMENT TYPE AUTHENTICATION STATUS CARD */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <Shield className="w-3.5 h-3.5 text-blue-400" /> Document Type Authentication
                </span>
                {validationResult && (
                  <span className="text-[10px] font-mono text-slate-400">
                    Threshold: {validationResult.confidence_threshold}%
                  </span>
                )}
              </div>

              {isValidatingDocType ? (
                <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center gap-3 animate-pulse">
                  <RefreshCw className="w-4 h-4 text-blue-400 animate-spin flex-shrink-0" />
                  <div className="space-y-0.5">
                    <p className="text-xs font-bold text-white">Detecting Document Type...</p>
                    <p className="text-[10px] text-slate-400">
                      Analyzing visual features, card layout, and text signals before OCR.
                    </p>
                  </div>
                </div>
              ) : validationResult ? (
                validationResult.validation_status === 'DOCUMENT_TYPE_CONFIRMED' ? (
                  /* Confirmed Match State */
                  <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-2.5">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                        <span className="text-xs font-bold text-emerald-300">Document Type Confirmed</span>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono font-bold">
                        {validationResult.classification_confidence}% CONFIDENCE
                      </span>
                    </div>

                    <div className="text-xs font-mono space-y-1 bg-navy-950/70 p-2.5 rounded-lg border border-emerald-500/20">
                      <div className="flex items-center justify-between text-slate-300">
                        <span>Selected:</span>
                        <span className="font-bold text-white">{validationResult.selected_document_type} ✓</span>
                      </div>
                      <div className="flex items-center justify-between text-slate-300">
                        <span>Detected:</span>
                        <span className="font-bold text-emerald-400">{validationResult.detected_document_name} ✓</span>
                      </div>
                    </div>

                    <p className="text-[11px] text-slate-300">
                      Document type verified. Ready to proceed to genuine OCR, forensic analysis, and tamper screening.
                    </p>
                  </div>
                ) : validationResult.validation_status === 'DOCUMENT_TYPE_MISMATCH' ? (
                  /* Type Mismatch State */
                  <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 space-y-2.5">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <AlertOctagon className="w-4 h-4 text-rose-400 flex-shrink-0" />
                        <span className="text-xs font-bold text-rose-300">Document Type Mismatch</span>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-mono font-bold">
                        {validationResult.classification_confidence}% CONFIDENCE
                      </span>
                    </div>

                    <div className="text-xs font-mono space-y-1 bg-navy-950/70 p-2.5 rounded-lg border border-rose-500/20">
                      <div className="flex items-center justify-between text-slate-300">
                        <span>Selected:</span>
                        <span className="font-bold text-rose-400">{validationResult.selected_document_type} ✕</span>
                      </div>
                      <div className="flex items-center justify-between text-slate-300">
                        <span>Detected:</span>
                        <span className="font-bold text-amber-300">{validationResult.detected_document_name}</span>
                      </div>
                    </div>

                    <p className="text-[11px] text-rose-200 leading-relaxed font-medium">
                      {validationResult.warning_message ||
                        `Document type mismatch: ${validationResult.selected_document_type} was selected, but the uploaded file does not appear to be a ${validationResult.selected_document_type}.`}
                    </p>

                    <div className="pt-1 flex items-center gap-2">
                      {validationResult.detected_document_type !== 'UNKNOWN' && (
                        <button
                          type="button"
                          onClick={() => handleDocTypeChange(validationResult.detected_document_type as DocumentType)}
                          className="py-1.5 px-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-[10px] flex items-center gap-1.5 transition"
                        >
                          <RotateCcw className="w-3 h-3" />
                          <span>Switch to {validationResult.detected_document_type}</span>
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={clearCurrentDocument}
                        className="py-1.5 px-3 rounded-lg bg-navy-900 border border-slate-700 hover:bg-navy-850 text-slate-300 text-[10px] transition"
                      >
                        Upload Correct Document
                      </button>
                    </div>
                  </div>
                ) : validationResult.validation_status === 'UNKNOWN_DOCUMENT' ? (
                  /* Unknown / Invalid Specimen State */
                  <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 space-y-2.5">
                    <div className="flex items-center gap-2">
                      <AlertOctagon className="w-4 h-4 text-rose-400 flex-shrink-0" />
                      <span className="text-xs font-bold text-rose-300">Unrecognized / Non-Document Input</span>
                    </div>

                    <div className="text-xs font-mono bg-navy-950/70 p-2.5 rounded-lg border border-rose-500/20 text-slate-300">
                      <span>Classification: </span>
                      <span className="font-bold text-rose-400">{validationResult.detected_document_name}</span>
                    </div>

                    <p className="text-[11px] text-rose-200 leading-relaxed font-medium">
                      {validationResult.warning_message ||
                        'The uploaded file does not appear to be an authentic identity document. Standalone signatures, selfies, blank sheets, and screenshots are rejected.'}
                    </p>

                    <button
                      type="button"
                      onClick={clearCurrentDocument}
                      className="py-1.5 px-3 rounded-lg bg-navy-900 border border-slate-700 hover:bg-navy-850 text-slate-300 text-[10px] transition"
                    >
                      Upload Valid Identity Document
                    </button>
                  </div>
                ) : (
                  /* Manual Review Required State */
                  <div className="p-4 rounded-xl bg-amber-500/15 border border-amber-500/30 space-y-2.5">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                      <span className="text-xs font-bold text-amber-300">Manual Review Required</span>
                    </div>

                    <p className="text-[11px] text-amber-200 leading-relaxed font-medium">
                      {validationResult.warning_message ||
                        `Unable to confidently determine document type (${validationResult.classification_confidence}% < ${validationResult.confidence_threshold}%). Compliance officer manual review will be required.`}
                    </p>
                  </div>
                )
              ) : (
                <div className="p-3.5 rounded-xl bg-navy-900/60 border border-slate-800 text-slate-400 text-xs flex items-center gap-2">
                  <HelpCircle className="w-4 h-4 text-slate-500" />
                  <span>Select a sample or upload a document to run automatic type authentication.</span>
                </div>
              )}
            </div>

            {/* Document Preview Card */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Specimen Visual Preview
              </label>
              <div className="h-48 rounded-xl bg-navy-950 border border-slate-800 overflow-hidden flex items-center justify-center relative group">
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
            <div>
              <button
                type="button"
                disabled={isLaunchDisabled}
                onClick={runScreening}
                className={`w-full py-3 rounded-xl font-bold text-sm shadow-glow-sm transition duration-150 flex items-center justify-center gap-2 ${
                  isMismatchOrInvalid
                    ? 'bg-slate-800 text-slate-400 border border-rose-500/40 cursor-not-allowed opacity-75'
                    : 'bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white disabled:opacity-50'
                }`}
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-white" />
                    <span>Processing AI Screening...</span>
                  </>
                ) : isMismatchOrInvalid ? (
                  <>
                    <AlertOctagon className="w-4 h-4 text-rose-400" />
                    <span>Document Type Mismatch — Cannot Proceed</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Start AI Screening Pipeline</span>
                  </>
                )}
              </button>
              {isMismatchOrInvalid && (
                <p className="text-[10px] text-rose-400 text-center mt-1.5">
                  Resolution required: Switch document type or upload the correct specimen.
                </p>
              )}
            </div>
          </div>

          {/* Workflow Stepper (10 Stages) */}
          <div className="p-6 rounded-2xl bg-navy-800/80 border border-slate-700/60 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white tracking-wide">Processing Workflow Pipeline</h3>
              <span className="text-[10px] font-mono text-slate-400">10 Verified Stages</span>
            </div>
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
