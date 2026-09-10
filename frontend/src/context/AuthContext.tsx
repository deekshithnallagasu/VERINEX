import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../services/types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  quickDemoLogin: (role: 'analyst' | 'reviewer' | 'admin') => Promise<void>;
  logout: () => void;
  isSessionExpired: boolean;
  triggerSessionExpired: () => void;
  dismissSessionExpired: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('verinex_user');
    try {
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('verinex_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSessionExpired, setIsSessionExpired] = useState<boolean>(false);

  useEffect(() => {
    async function verifyUser() {
      if (token) {
        try {
          const profile = await api.getMe();
          setUser(profile);
        } catch {
          // Token expired or invalid
          setUser(null);
          setToken(null);
          localStorage.removeItem('verinex_token');
          localStorage.removeItem('verinex_user');
        }
      }
      setIsLoading(false);
    }
    verifyUser();
  }, [token]);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await api.login(username, password);
      setUser(res.user);
      setToken(res.access_token);
    } finally {
      setIsLoading(false);
    }
  };

  const quickDemoLogin = async (role: 'analyst' | 'reviewer' | 'admin') => {
    setIsLoading(true);
    try {
      const res = await api.login(role, 'Verinex2026!');
      setUser(res.user);
      setToken(res.access_token);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
    setToken(null);
  };

  const triggerSessionExpired = () => {
    setIsSessionExpired(true);
    api.recordClientAudit('SESSION_EXPIRED', 'User session expired due to timeout.', undefined, 'WARNING');
  };

  const dismissSessionExpired = () => {
    setIsSessionExpired(false);
    logout();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        quickDemoLogin,
        logout,
        isSessionExpired,
        triggerSessionExpired,
        dismissSessionExpired
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};
