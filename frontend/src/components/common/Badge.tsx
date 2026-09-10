import React from 'react';
import { RiskLevel, CaseStatus } from '../../services/types';
import { ShieldCheck, AlertTriangle, AlertOctagon, CheckCircle2, Clock, XCircle, ShieldAlert } from 'lucide-react';

interface RiskBadgeProps {
  level: RiskLevel;
  score?: number;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, size = 'md' }) => {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3.5 py-1.5 font-semibold'
  };

  if (level === 'LOW') {
    return (
      <span className={`inline-flex items-center gap-1.5 rounded-full font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 ${sizeClasses[size]}`}>
        <ShieldCheck className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
        <span>LOW RISK {score !== undefined && `(${score})`}</span>
      </span>
    );
  }

  if (level === 'MEDIUM') {
    return (
      <span className={`inline-flex items-center gap-1.5 rounded-full font-medium bg-amber-500/15 text-amber-400 border border-amber-500/30 ${sizeClasses[size]}`}>
        <AlertTriangle className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
        <span>MEDIUM RISK {score !== undefined && `(${score})`}</span>
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-medium bg-rose-500/15 text-rose-400 border border-rose-500/30 shadow-glow-danger ${sizeClasses[size]}`}>
      <AlertOctagon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      <span>HIGH RISK {score !== undefined && `(${score})`}</span>
    </span>
  );
};

interface StatusBadgeProps {
  status: CaseStatus;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-xs px-2.5 py-1';

  switch (status) {
    case 'VERIFIED':
      return (
        <span className={`inline-flex items-center gap-1 rounded-full font-medium bg-emerald-950/80 text-emerald-300 border border-emerald-800 ${sizeClass}`}>
          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
          Verified
        </span>
      );
    case 'IN_REVIEW':
      return (
        <span className={`inline-flex items-center gap-1 rounded-full font-medium bg-blue-950/80 text-blue-300 border border-blue-800 ${sizeClass}`}>
          <Clock className="w-3 h-3 text-blue-400" />
          In Review
        </span>
      );
    case 'FLAGGED':
      return (
        <span className={`inline-flex items-center gap-1 rounded-full font-medium bg-rose-950/80 text-rose-300 border border-rose-800 ${sizeClass}`}>
          <ShieldAlert className="w-3 h-3 text-rose-400" />
          Flagged
        </span>
      );
    case 'REJECTED':
      return (
        <span className={`inline-flex items-center gap-1 rounded-full font-medium bg-red-950/80 text-red-300 border border-red-800 ${sizeClass}`}>
          <XCircle className="w-3 h-3 text-red-400" />
          Rejected
        </span>
      );
    default:
      return (
        <span className={`inline-flex items-center gap-1 rounded-full font-medium bg-slate-800 text-slate-300 border border-slate-700 ${sizeClass}`}>
          <Clock className="w-3 h-3 text-slate-400" />
          Pending
        </span>
      );
  }
};
