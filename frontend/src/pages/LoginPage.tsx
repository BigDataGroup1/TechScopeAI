import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import { authApi } from '../services/api';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    company_name: '',
    industry: '',
    problem: '',
    solution: '',
    target_market: '',
    current_stage: 'Pre-Seed',
    traction: '',
    funding_goal: '',
  });
  const [consents, setConsents] = useState({
    data_sharing: false,
    tos: false,
    privacy: false,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await authApi.register(formData);
      localStorage.setItem('sessionId', response.session_id);
      login(response.session_id, response.company);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const stages = ['Pre-Seed', 'Seed', 'Series A', 'Series B', 'Series C+'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-fuchsia-50 via-purple-50 to-violet-100 flex items-center justify-center p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-violet-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>
      </div>

      <div className="relative w-full max-w-2xl">
        {/* Logo/Title */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold gradient-text mb-3">TechScopeAI</h1>
          <p className="text-slate-600 text-lg">Your AI-powered startup intelligence platform</p>
        </div>

        {/* Form Card */}
        <div className="canva-card p-8 shadow-2xl">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-slate-800">Get Started</h2>
            <p className="text-slate-500 mt-2">Tell us about your company to unlock AI-powered insights</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Company Name & Industry */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Company Name *
                </label>
                <input
                  type="text"
                  name="company_name"
                  value={formData.company_name}
                  onChange={handleChange}
                  required
                  placeholder="Your Company"
                  className="canva-input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Industry *
                </label>
                <input
                  type="text"
                  name="industry"
                  value={formData.industry}
                  onChange={handleChange}
                  required
                  placeholder="e.g., AI/ML, SaaS, Fintech"
                  className="canva-input w-full"
                />
              </div>
            </div>

            {/* Problem */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Problem You're Solving *
              </label>
              <textarea
                name="problem"
                value={formData.problem}
                onChange={handleChange}
                required
                rows={3}
                placeholder="Describe the problem your startup addresses..."
                className="canva-textarea w-full"
              />
            </div>

            {/* Solution */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Your Solution *
              </label>
              <textarea
                name="solution"
                value={formData.solution}
                onChange={handleChange}
                required
                rows={3}
                placeholder="Describe your product or service solution..."
                className="canva-textarea w-full"
              />
            </div>

            {/* Target Market & Stage */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Target Market
                </label>
                <input
                  type="text"
                  name="target_market"
                  value={formData.target_market}
                  onChange={handleChange}
                  placeholder="e.g., SMBs, Enterprise"
                  className="canva-input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Funding Stage
                </label>
                <select
                  name="current_stage"
                  value={formData.current_stage}
                  onChange={handleChange}
                  className="canva-select w-full"
                >
                  {stages.map((stage) => (
                    <option key={stage} value={stage}>
                      {stage}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Traction & Funding Goal */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Traction
                </label>
                <input
                  type="text"
                  name="traction"
                  value={formData.traction}
                  onChange={handleChange}
                  placeholder="e.g., 1000 users, $50k MRR"
                  className="canva-input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Funding Goal
                </label>
                <input
                  type="text"
                  name="funding_goal"
                  value={formData.funding_goal}
                  onChange={handleChange}
                  placeholder="e.g., $500k"
                  className="canva-input w-full"
                />
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
                {error}
              </div>
            )}

            {/* Consents */}
            <div className="space-y-3 bg-slate-50 border border-slate-200 rounded-xl p-4">
              <label className="flex items-start gap-3 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={consents.data_sharing}
                  onChange={(e) => setConsents({ ...consents, data_sharing: e.target.checked })}
                  className="mt-1 h-4 w-4"
                  required
                />
                <span>I consent to data sharing for improving the service *</span>
              </label>
              <label className="flex items-start gap-3 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={consents.tos}
                  onChange={(e) => setConsents({ ...consents, tos: e.target.checked })}
                  className="mt-1 h-4 w-4"
                  required
                />
                <span>I accept the Terms of Service *</span>
              </label>
              <label className="flex items-start gap-3 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={consents.privacy}
                  onChange={(e) => setConsents({ ...consents, privacy: e.target.checked })}
                  className="mt-1 h-4 w-4"
                  required
                />
                <span>I accept the Privacy Policy *</span>
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={
                isLoading ||
                !formData.company_name ||
                !formData.industry ||
                !formData.problem ||
                !formData.solution ||
                !consents.data_sharing ||
                !consents.tos ||
                !consents.privacy
              }
              className="w-full canva-btn py-4 text-lg flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="spinner"></div>
                  <span>Setting up your account...</span>
                </>
              ) : (
                <span>Get Started</span>
              )}
            </button>
          </form>

          {/* Features Preview */}
          <div className="mt-8 pt-6 border-t border-purple-100">
            <p className="text-center text-sm text-slate-500 mb-4">Unlock powerful AI tools:</p>
            <div className="grid grid-cols-4 gap-3 text-center">
              {[
                { name: 'Pitch Decks', color: 'from-orange-400 to-rose-400' },
                { name: 'Market Intel', color: 'from-indigo-400 to-purple-400' },
                { name: 'Patent Analysis', color: 'from-teal-400 to-emerald-400' },
                { name: 'Team Building', color: 'from-purple-400 to-pink-400' },
              ].map((feature) => (
                <div key={feature.name} className="p-3 rounded-xl bg-gradient-to-br from-slate-50 to-purple-50">
                  <div 
                    className={`w-8 h-8 mx-auto mb-2 rounded-lg bg-gradient-to-br ${feature.color}`}
                  ></div>
                  <span className="text-xs font-medium text-slate-600">{feature.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-slate-500 mt-6">
          Powered by advanced AI • Your data is secure
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
