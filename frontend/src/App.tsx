import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider, useApp } from './store/AppContext';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import PitchDeckPage from './pages/PitchDeckPage';
import ElevatorPitchPage from './pages/ElevatorPitchPage';
import MarketingPage from './pages/MarketingPage';
import PatentPage from './pages/PatentPage';
import PolicyPage from './pages/PolicyPage';
import TeamAnalysisPage from './pages/TeamAnalysisPage';
import CompetitivePage from './pages/CompetitivePage';
import ChatPage from './pages/ChatPage';
import './index.css';

// Protected Route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useApp();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-fuchsia-50 via-purple-50 to-violet-50">
        <div className="text-center">
          <div className="spinner-large mx-auto mb-4"></div>
          <p className="text-purple-600 font-medium">Loading TechScopeAI...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Public Route wrapper (redirect to dashboard if already logged in)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useApp();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-fuchsia-50 via-purple-50 to-violet-50">
        <div className="text-center">
          <div className="spinner-large mx-auto mb-4"></div>
          <p className="text-purple-600 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />

      {/* Protected Routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/pitch-deck"
        element={
          <ProtectedRoute>
            <PitchDeckPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/elevator-pitch"
        element={
          <ProtectedRoute>
            <ElevatorPitchPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/competitors"
        element={
          <ProtectedRoute>
            <CompetitivePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/marketing"
        element={
          <ProtectedRoute>
            <MarketingPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/policy"
        element={
          <ProtectedRoute>
            <PolicyPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/patentability"
        element={
          <ProtectedRoute>
            <PatentPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/filing-strategy"
        element={
          <ProtectedRoute>
            <PatentPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/team-analysis"
        element={
          <ProtectedRoute>
            <TeamAnalysisPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        }
      />

      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <AppRoutes />
      </AppProvider>
    </BrowserRouter>
  );
}

export default App;
