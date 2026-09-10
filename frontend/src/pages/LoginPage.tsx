import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Shield, Lock, Mail, Eye, EyeOff, CheckCircle2, ShieldAlert, Sparkles, ArrowRight, KeyRound } from 'lucide-react';
import { Modal } from '../components/common/Modal';
import { api } from '../services/api';

export const LoginPage: React.FC = () => {
  const { login, quickDemoLogin } = useAuth();
  const [username, setUsername] = useState('analyst');
  const [password, setPassword] = useState('Verinex2026!');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Modal states for Forgot / Reset Password
  const [isForgotModalOpen, setIsForgotModalOpen] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotSuccess, setForgotSuccess] = useState<string | null>(null);
  const [isResetStep, setIsResetStep] = useState(false);
  const [resetCode, setResetCode] = useState('772910');
  const [newPassword, setNewPassword] = useState('');
  const [resetSuccess, setResetSuccess] = useState<string | null>(null);

  // Registration modal
  const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
  const [regUsername, setRegUsername] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regName, setRegName] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regRole, setRegRole] = useState('Compliance Analyst');
  const [regError, setRegError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(username, password);
    } catch (err: any) {
      setError(err.message || 'Invalid credentials. Please verify your username and password.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.forgotPassword(forgotEmail);
      setForgotSuccess(res.message);
      setIsResetStep(true);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.resetPassword(forgotEmail, resetCode, newPassword);
      setResetSuccess(res.message);
      setTimeout(() => {
        setIsForgotModalOpen(false);
        setIsResetStep(false);
        setForgotSuccess(null);
        setResetSuccess(null);
      }, 2000);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegError(null);
    try {
      await api.register(regUsername, regEmail, regName, regPassword, regRole);
      setIsRegisterModalOpen(false);
    } catch (err: any) {
      setRegError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-navy-950 text-slate-100 relative overflow-hidden">
      {/* Subtle background ambient cyber glow */}
      <div className="absolute top-[-15%] left-[-10%] w-[500px] h-[500px] rounded-full bg-blue-600/10 blur-[130px] pointer-events-none"></div>
      <div className="absolute bottom-[-15%] right-[-10%] w-[500px] h-[500px] rounded-full bg-purple-600/10 blur-[130px] pointer-events-none"></div>

      {/* Top Brand Bar */}
      <div className="p-6 sm:px-12 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 shadow-glow-sm text-white">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xl font-black tracking-widest text-white">VERINEX</span>
            <span className="text-xs text-blue-400 font-semibold ml-2">SECURITY SUITE</span>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-400 bg-navy-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Defensive Screening Prototype v1.0</span>
        </div>
      </div>

      {/* Main Login Card Area */}
      <div className="flex-1 flex items-center justify-center p-4 z-10">
        <div className="w-full max-w-md">
          {/* Card Container */}
          <div className="bg-navy-900/90 border border-slate-800 rounded-2xl p-8 shadow-2xl backdrop-blur-xl">
            {/* Header */}
            <div className="text-center mb-6">
              <div className="inline-flex p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 mb-3 shadow-glow-sm">
                <Shield className="w-7 h-7" />
              </div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Operator Sign In</h2>
              <p className="text-xs text-slate-400 mt-1">AI-Powered Identity & Document Screening</p>
            </div>

            {/* Error Notification */}
            {error && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 flex-shrink-0 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            {/* Login Form */}
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Email or Username
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="analyst@verinex.ai"
                    className="w-full pl-10 pr-4 py-2.5 bg-navy-800 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-semibold text-slate-300">Password</label>
                  <button
                    type="button"
                    onClick={() => { setIsForgotModalOpen(true); setForgotEmail(username.includes('@') ? username : 'analyst@verinex.ai'); }}
                    className="text-xs text-blue-400 hover:text-blue-300 font-medium transition"
                  >
                    Forgot Password?
                  </button>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full pl-10 pr-10 py-2.5 bg-navy-800 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-200 transition"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-400 hover:text-slate-300 select-none">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded bg-navy-800 border-slate-700 text-blue-600 focus:ring-blue-500/20 focus:ring-offset-0"
                  />
                  <span>Remember this device</span>
                </label>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full mt-2 py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-semibold text-sm shadow-glow-sm transition duration-150 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isSubmitting ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <>
                    <span>Authenticate & Enter</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            {/* Quick 1-Click Demo Login Personas */}
            <div className="mt-6 pt-5 border-t border-slate-800">
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-[11px] uppercase tracking-wider font-bold text-slate-400 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                  Quick Demo Accounts
                </span>
                <span className="text-[10px] text-slate-400">1-Click Login</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => quickDemoLogin('analyst')}
                  className="p-2 rounded-lg bg-navy-800 hover:bg-blue-600/20 border border-slate-700/80 hover:border-blue-500/40 text-center transition group"
                >
                  <div className="text-[11px] font-semibold text-slate-200 group-hover:text-blue-300">Analyst</div>
                  <div className="text-[9px] text-slate-400">Sarah Chen</div>
                </button>
                <button
                  type="button"
                  onClick={() => quickDemoLogin('reviewer')}
                  className="p-2 rounded-lg bg-navy-800 hover:bg-blue-600/20 border border-slate-700/80 hover:border-blue-500/40 text-center transition group"
                >
                  <div className="text-[11px] font-semibold text-slate-200 group-hover:text-blue-300">Reviewer</div>
                  <div className="text-[9px] text-slate-400">David Vance</div>
                </button>
                <button
                  type="button"
                  onClick={() => quickDemoLogin('admin')}
                  className="p-2 rounded-lg bg-navy-800 hover:bg-blue-600/20 border border-slate-700/80 hover:border-blue-500/40 text-center transition group"
                >
                  <div className="text-[11px] font-semibold text-slate-200 group-hover:text-blue-300">Admin</div>
                  <div className="text-[9px] text-slate-400">Alex Mercer</div>
                </button>
              </div>
            </div>

            {/* Create Account & Footer Links */}
            <div className="mt-5 text-center">
              <button
                type="button"
                onClick={() => setIsRegisterModalOpen(true)}
                className="text-xs text-slate-400 hover:text-white transition"
              >
                Don't have an operator credential? <span className="text-blue-400 font-semibold underline underline-offset-2">Create Account</span>
              </button>
            </div>
          </div>

          {/* Privacy & Defensive Guard Footer Notice */}
          <div className="mt-6 text-center space-y-2">
            <div className="flex items-center justify-center gap-4 text-[11px] text-slate-400">
              <span className="flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                SOC2 Type II
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ISO 27001
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                Defensive Boundary
              </span>
            </div>
            <p className="text-[10px] text-slate-400 max-w-sm mx-auto leading-relaxed">
              VERINEX is strictly a defensive verification system. Fictional test data only. No forged document creation tools provided.
            </p>
          </div>
        </div>
      </div>

      {/* Forgot / Reset Password Modal */}
      <Modal
        isOpen={isForgotModalOpen}
        onClose={() => { setIsForgotModalOpen(false); setIsResetStep(false); }}
        title={isResetStep ? "Set New Password" : "Reset Operator Password"}
        maxWidth="md"
      >
        {!isResetStep ? (
          <form onSubmit={handleForgotPassword} className="space-y-4">
            <p className="text-xs text-slate-300 leading-relaxed">
              Enter your registered corporate email to receive a secure password reset token.
            </p>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Corporate Email</label>
              <input
                type="email"
                required
                value={forgotEmail}
                onChange={(e) => setForgotEmail(e.target.value)}
                placeholder="analyst@verinex.ai"
                className="w-full px-3.5 py-2 bg-navy-900 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            {forgotSuccess && (
              <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs">
                {forgotSuccess}
              </div>
            )}
            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition"
            >
              Send Reset Instructions
            </button>
          </form>
        ) : (
          <form onSubmit={handleResetPassword} className="space-y-4">
            <p className="text-xs text-slate-300">
              Enter the reset verification code dispatched to <span className="text-blue-400 font-semibold">{forgotEmail}</span>.
            </p>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Verification Code</label>
              <input
                type="text"
                required
                value={resetCode}
                onChange={(e) => setResetCode(e.target.value)}
                placeholder="772910"
                className="w-full px-3.5 py-2 bg-navy-900 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">New Password</label>
              <input
                type="password"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter strong password"
                className="w-full px-3.5 py-2 bg-navy-900 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            {resetSuccess && (
              <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs">
                {resetSuccess}
              </div>
            )}
            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition"
            >
              Update Password
            </button>
          </form>
        )}
      </Modal>

      {/* Create Account Modal */}
      <Modal
        isOpen={isRegisterModalOpen}
        onClose={() => setIsRegisterModalOpen(false)}
        title="Create New Operator Account"
        maxWidth="md"
      >
        <form onSubmit={handleRegister} className="space-y-4">
          {regError && (
            <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs">
              {regError}
            </div>
          )}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Username</label>
            <input
              type="text"
              required
              value={regUsername}
              onChange={(e) => setRegUsername(e.target.value)}
              placeholder="jdoe"
              className="w-full px-3.5 py-2 bg-navy-900 border border-slate-700 rounded-xl text-sm text-white"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Full Legal Name</label>
            <input
              type="text"
              required
              value={regName}
              onChange={(e) => setRegName(e.target.value)}
              placeholder="Jane Doe"
              className="w-full px-3.5 py-2 bg-navy-900 border border-slate-700 rounded-xl text-sm text-white"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Email Address</label>
            <input
              type="email"
              required
              value={regEmail}
              onChange={(e) => setRegEmail(e.target.value)}
              placeholder="jane.doe@verinex.ai"
              className="w-full px-3.5 py-2 bg-navy-900 border border-slate-700 rounded-xl text-sm text-white"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Role</label>
            <select
              value={regRole}
              onChange={(e) => setRegRole(e.target.value)}
              className="w-full px-3.5 py-2 bg-navy-900 border border-slate-700 rounded-xl text-sm text-white"
            >
              <option value="Compliance Analyst">Compliance Analyst</option>
              <option value="Senior Reviewer">Senior Reviewer</option>
              <option value="Risk Administrator">Risk Administrator</option>
              <option value="Auditor">Auditor</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
            <input
              type="password"
              required
              value={regPassword}
              onChange={(e) => setRegPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full px-3.5 py-2 bg-navy-900 border border-slate-700 rounded-xl text-sm text-white"
            />
          </div>
          <button
            type="submit"
            className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition shadow-glow-sm"
          >
            Register Account
          </button>
        </form>
      </Modal>
    </div>
  );
};
