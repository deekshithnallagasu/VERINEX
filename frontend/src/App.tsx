import React, { useState } from 'react';
import { useAuth, AuthProvider } from './context/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ScreeningPage } from './pages/ScreeningPage';
import { ScreeningResultPage } from './pages/ScreeningResultPage';
import { CaseReviewPage } from './pages/CaseReviewPage';
import { ReportsPage } from './pages/ReportsPage';
import { AuditLogPage } from './pages/AuditLogPage';
import { SettingsPage } from './pages/SettingsPage';
import { Sidebar } from './components/common/Sidebar';
import { Header } from './components/common/Header';
import { Modal } from './components/common/Modal';
import { ScreeningCase } from './services/types';
import { api } from './services/api';
import { ShieldAlert, LogIn, Lock } from 'lucide-react';

const MainApp: React.FC = () => {
  const { user, isLoading, isSessionExpired, dismissSessionExpired } = useAuth();
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [activeResultCase, setActiveResultCase] = useState<ScreeningCase | null>(null);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-navy-950 flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <div className="text-sm font-semibold tracking-wider text-slate-400">INITIALIZING VERINEX ENGINE...</div>
      </div>
    );
  }

  // If not logged in, display the Login Page
  if (!user) {
    return <LoginPage />;
  }

  const handleNavigate = (tab: string, caseId?: string) => {
    if (caseId) {
      setSelectedCaseId(caseId);
    }
    setCurrentTab(tab);
  };

  const handleScreeningComplete = (newCase: ScreeningCase) => {
    setActiveResultCase(newCase);
    setCurrentTab('results');
  };

  const handleStatusUpdate = async (caseId: string, status: any) => {
    try {
      const updated = await api.updateCaseStatus(caseId, status, 'Adjudicated by operator');
      setActiveResultCase(updated);
    } catch (err) {
      console.error('Error updating status:', err);
    }
  };

  return (
    <div className="flex min-h-screen bg-navy-950 text-slate-100 selection:bg-blue-600/30">
      {/* Left Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onNavigate={handleNavigate}
        pendingCount={2}
      />

      {/* Main Workspace Column */}
      <div className="flex-1 flex flex-col min-w-0 overflow-x-hidden">
        {/* Top Header */}
        <Header currentTab={currentTab} onNavigate={handleNavigate} />

        {/* Dynamic Page Views */}
        <main className="flex-1 overflow-y-auto pb-12">
          {currentTab === 'dashboard' && (
            <DashboardPage onNavigate={handleNavigate} />
          )}

          {currentTab === 'screening' && (
            <ScreeningPage onScreeningComplete={handleScreeningComplete} />
          )}

          {currentTab === 'results' && activeResultCase && (
            <ScreeningResultPage
              caseData={activeResultCase}
              onNavigate={handleNavigate}
              onStatusUpdate={handleStatusUpdate}
            />
          )}

          {currentTab === 'cases' && (
            <CaseReviewPage
              initialCaseId={selectedCaseId}
              onNavigate={handleNavigate}
            />
          )}

          {currentTab === 'reports' && (
            <ReportsPage />
          )}

          {currentTab === 'audit' && (
            <AuditLogPage />
          )}

          {currentTab === 'settings' && (
            <SettingsPage />
          )}
        </main>
      </div>

      {/* Session Expired Simulated Modal */}
      <Modal
        isOpen={isSessionExpired}
        onClose={dismissSessionExpired}
        title="Session Expired: Security Timeout"
        maxWidth="md"
      >
        <div className="space-y-4 text-center py-2">
          <div className="inline-flex p-3 rounded-2xl bg-amber-500/10 text-amber-400 border border-amber-500/30 mb-1">
            <Lock className="w-8 h-8" />
          </div>
          <div>
            <h4 className="text-base font-bold text-white">Compliance Inactivity Timeout</h4>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              In accordance with enterprise banking and regulatory compliance policies, your authenticated operator session has expired. All unsaved forensic drafts remain protected.
            </p>
          </div>
          <div className="pt-2">
            <button
              onClick={dismissSessionExpired}
              className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-glow-sm transition flex items-center justify-center gap-2"
            >
              <LogIn className="w-4 h-4" />
              <span>Re-Authenticate Session</span>
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}

export default App;
