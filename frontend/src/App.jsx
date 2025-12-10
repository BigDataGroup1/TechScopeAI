import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import SignupForm from './components/SignupForm';
import Dashboard from './components/Dashboard';

function App() {
  const [companyId, setCompanyId] = useState(null);
  const [companyData, setCompanyData] = useState(null);
  const [isSignedUp, setIsSignedUp] = useState(false);

  // Check if user has already signed up (from localStorage)
  useEffect(() => {
    const savedCompanyId = localStorage.getItem('techscope_company_id');
    const savedCompanyData = localStorage.getItem('techscope_company_data');
    
    if (savedCompanyId && savedCompanyData) {
      try {
        setCompanyId(savedCompanyId);
        setCompanyData(JSON.parse(savedCompanyData));
        setIsSignedUp(true);
      } catch (error) {
        console.error('Error loading saved company data:', error);
        localStorage.removeItem('techscope_company_id');
        localStorage.removeItem('techscope_company_data');
      }
    }
  }, []);

  const handleSignupComplete = (id, data) => {
    setCompanyId(id);
    setCompanyData(data);
    setIsSignedUp(true);
    
    // Save to localStorage
    localStorage.setItem('techscope_company_id', id);
    localStorage.setItem('techscope_company_data', JSON.stringify(data));
  };

  const handleSignOut = () => {
    setCompanyId(null);
    setCompanyData(null);
    setIsSignedUp(false);
    localStorage.removeItem('techscope_company_id');
    localStorage.removeItem('techscope_company_data');
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            isSignedUp ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <SignupForm onComplete={handleSignupComplete} />
            )
          }
        />
        <Route
          path="/dashboard"
          element={
            isSignedUp && companyData ? (
              <div>
                <button
                  onClick={handleSignOut}
                  className="fixed top-4 right-4 z-50 bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Sign Out
                </button>
                <Dashboard companyId={companyId} companyData={companyData} />
              </div>
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
