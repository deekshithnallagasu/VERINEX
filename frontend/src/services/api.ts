import {
  User,
  ScreeningCase,
  SampleDocumentItem,
  AuditLog,
  DashboardStats,
  CaseStatus
} from './types';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('verinex_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  // --- Authentication ---
  async login(username: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(err.detail || 'Authentication failed');
    }
    const data = await res.json();
    localStorage.setItem('verinex_token', data.access_token);
    localStorage.setItem('verinex_user', JSON.stringify(data.user));
    return data;
  },

  async register(username: string, email: string, full_name: string, password: string, role?: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, full_name, password, role })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(err.detail || 'Registration failed');
    }
    const data = await res.json();
    localStorage.setItem('verinex_token', data.access_token);
    localStorage.setItem('verinex_user', JSON.stringify(data.user));
    return data;
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch user');
    return res.json();
  },

  async forgotPassword(email: string): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    return res.json();
  },

  async resetPassword(email: string, reset_code: string, new_password: string): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, reset_code, new_password })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Reset failed' }));
      throw new Error(err.detail || 'Password reset failed');
    }
    return res.json();
  },

  logout(): void {
    localStorage.removeItem('verinex_token');
    localStorage.removeItem('verinex_user');
  },

  // --- Dashboard & Stats ---
  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/stats/dashboard`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to load dashboard metrics');
    return res.json();
  },

  // --- Screenings & Samples ---
  async getSamplePresets(): Promise<SampleDocumentItem[]> {
    const res = await fetch(`${API_BASE}/screenings/samples/list`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to load sample documents');
    return res.json();
  },

  async runDemoSample(sampleId: string): Promise<ScreeningCase> {
    const formData = new FormData();
    formData.append('sample_id', sampleId);

    const res = await fetch(`${API_BASE}/screenings/demo-sample`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Screening failed' }));
      throw new Error(err.detail || 'Demo screening failed');
    }
    return res.json();
  },

  async uploadAndScreen(file: File, documentType: string, probeFace?: File | Blob | null): Promise<ScreeningCase> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    if (probeFace) {
      formData.append('probe_face', probeFace, 'probe_selfie.png');
    }

    const res = await fetch(`${API_BASE}/screenings/upload`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload screening failed' }));
      throw new Error(err.detail || 'Document upload failed');
    }
    return res.json();
  },

  async getScreeningCase(id: string): Promise<ScreeningCase> {
    const res = await fetch(`${API_BASE}/screenings/${id}`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error(`Failed to load case ${id}`);
    return res.json();
  },

  async listScreenings(params?: { status?: string; risk_level?: string; doc_type?: string; search?: string }): Promise<ScreeningCase[]> {
    const query = new URLSearchParams();
    if (params?.status && params.status !== 'ALL') query.append('status', params.status);
    if (params?.risk_level && params.risk_level !== 'ALL') query.append('risk_level', params.risk_level);
    if (params?.doc_type && params.doc_type !== 'ALL') query.append('doc_type', params.doc_type);
    if (params?.search) query.append('search', params.search);

    const res = await fetch(`${API_BASE}/screenings?${query.toString()}`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to list screenings');
    return res.json();
  },

  // --- Case Management ---
  async updateCaseStatus(caseId: string, status: CaseStatus, decisionReason?: string): Promise<ScreeningCase> {
    const res = await fetch(`${API_BASE}/cases/${caseId}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ status, decision_reason: decisionReason })
    });
    if (!res.ok) throw new Error('Failed to update case status');
    return res.json();
  },

  async addCaseNote(caseId: string, noteText: string, authorName?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/cases/${caseId}/notes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ note_text: noteText, author_name: authorName })
    });
    if (!res.ok) throw new Error('Failed to add reviewer note');
    return res.json();
  },

  // --- Reports ---
  async listReports(params?: { status?: string; risk_level?: string; doc_type?: string; search?: string }): Promise<any> {
    const query = new URLSearchParams();
    if (params?.status && params.status !== 'ALL') query.append('status', params.status);
    if (params?.risk_level && params.risk_level !== 'ALL') query.append('risk_level', params.risk_level);
    if (params?.doc_type && params.doc_type !== 'ALL') query.append('doc_type', params.doc_type);
    if (params?.search) query.append('search', params.search);

    const res = await fetch(`${API_BASE}/reports?${query.toString()}`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to load reports');
    return res.json();
  },

  async getReportDetail(caseId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/reports/${caseId}`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch report detail');
    return res.json();
  },

  getReportExportUrl(caseId: string, format: 'json' | 'csv'): string {
    return `${API_BASE}/reports/${caseId}/export?format=${format}`;
  },

  // --- Audit Logs ---
  async listAuditLogs(params?: { action?: string; severity?: string; search?: string }): Promise<AuditLog[]> {
    const query = new URLSearchParams();
    if (params?.action && params.action !== 'ALL') query.append('action', params.action);
    if (params?.severity && params.severity !== 'ALL') query.append('severity', params.severity);
    if (params?.search) query.append('search', params.search);

    const res = await fetch(`${API_BASE}/audit-logs?${query.toString()}`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to load audit logs');
    return res.json();
  },

  async recordClientAudit(action: string, details: string, caseId?: string, severity?: string): Promise<any> {
    try {
      await fetch(`${API_BASE}/audit-logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader()
        },
        body: JSON.stringify({ action, details, case_id: caseId, severity })
      });
    } catch {
      // Non-blocking
    }
  },

  // --- Settings ---
  async getSettings(): Promise<Record<string, { value: string; description: string; category: string }>> {
    const res = await fetch(`${API_BASE}/settings`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to load settings');
    return res.json();
  },

  async updateSettings(settings: Record<string, string>): Promise<any> {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ settings })
    });
    if (!res.ok) throw new Error('Failed to update settings');
    return res.json();
  }
};
