import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '../services/api';
import type { Company, Activity } from '../services/api';

interface AppState {
  isAuthenticated: boolean;
  sessionId: string | null;
  company: Company | null;
  activities: Activity[];
  isLoading: boolean;
}

interface AppContextType extends AppState {
  login: (sessionId: string, company: Company) => void;
  logout: () => void;
  refreshActivities: () => Promise<void>;
  addActivity: (activity: Activity) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AppState>({
    isAuthenticated: false,
    sessionId: null,
    company: null,
    activities: [],
    isLoading: true,
  });

  // Check for existing session on mount
  useEffect(() => {
    const checkSession = async () => {
      const savedSessionId = localStorage.getItem('sessionId');
      if (savedSessionId) {
        try {
          const response = await authApi.getSession();
          setState({
            isAuthenticated: true,
            sessionId: savedSessionId,
            company: response.company,
            activities: [],
            isLoading: false,
          });
          // Load activities
          const activitiesResponse = await authApi.getActivities();
          setState(prev => ({
            ...prev,
            activities: activitiesResponse.activities,
          }));
        } catch (error) {
          // Session invalid, clear it
          localStorage.removeItem('sessionId');
          setState({
            isAuthenticated: false,
            sessionId: null,
            company: null,
            activities: [],
            isLoading: false,
          });
        }
      } else {
        setState(prev => ({ ...prev, isLoading: false }));
      }
    };
    checkSession();
  }, []);

  const login = (sessionId: string, company: Company) => {
    localStorage.setItem('sessionId', sessionId);
    setState({
      isAuthenticated: true,
      sessionId,
      company,
      activities: [],
      isLoading: false,
    });
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      // Ignore errors
    }
    localStorage.removeItem('sessionId');
    setState({
      isAuthenticated: false,
      sessionId: null,
      company: null,
      activities: [],
      isLoading: false,
    });
  };

  const refreshActivities = async () => {
    try {
      const response = await authApi.getActivities();
      setState(prev => ({
        ...prev,
        activities: response.activities,
      }));
    } catch (error) {
      console.error('Failed to refresh activities:', error);
    }
  };

  const addActivity = (activity: Activity) => {
    setState(prev => ({
      ...prev,
      activities: [activity, ...prev.activities].slice(0, 50),
    }));
  };

  return (
    <AppContext.Provider
      value={{
        ...state,
        login,
        logout,
        refreshActivities,
        addActivity,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

