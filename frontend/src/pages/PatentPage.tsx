import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import { patentApi } from '../services/api';
import { ArrowLeft, Lightbulb, Search, FileText, Globe } from 'lucide-react';
import ContentRenderer from '../components/ContentRenderer';

const industries = [
  'AI/Machine Learning',
  'Software/SaaS',
  'Hardware/IoT',
  'Biotech/Healthcare',
  'Clean Energy',
  'Fintech',
  'E-commerce',
  'Manufacturing',
  'Other',
];

const developmentStages = [
  'Concept/Idea',
  'Research Phase',
  'Prototype',
  'MVP/Beta',
  'Production Ready',
  'Already in Market',
];

const geographicOptions = [
  'USA only',
  'USA + Europe',
  'USA + Asia',
  'Global (PCT)',
  'Specific countries',
];

const budgetOptions = [
  'Under $5,000',
  '$5,000 - $15,000',
  '$15,000 - $30,000',
  '$30,000 - $50,000',
  '$50,000+',
  'Not sure yet',
];

const PatentPage: React.FC = () => {
  const navigate = useNavigate();
  const { company, addActivity } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'assess' | 'strategy'>('assess');

  const [formData, setFormData] = useState({
    invention_description: '',
    industry: '',
    novelty: '',
    development_stage: '',
    prior_art_awareness: '',
    prior_art_details: '',
    geographic_interest: [] as string[],
    budget_range: '',
  });

  const handleAssess = async () => {
    if (!company || !formData.invention_description) return;
    
    setIsLoading(true);
    setError('');
    setResult(null);
    
    try {
      const response = await patentApi.assess({
        company_id: company.id,
        invention_description: formData.invention_description,
        novelty: formData.novelty,
      });
      setResult(response);
      addActivity({
        id: Date.now().toString(),
        title: 'Patentability Assessed',
        description: 'Analysis complete',
        timestamp: new Date().toISOString(),
        type: 'patent',
        content: response.assessment || response.response,
        toolUsed: 'Patent Assessment Agent',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Assessment failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilingStrategy = async () => {
    if (!company) return;
    
    setIsLoading(true);
    setError('');
    setResult(null);
    
    try {
      const response = await patentApi.filingStrategy({
        company_id: company.id,
        geographic_interest: formData.geographic_interest,
        budget_range: formData.budget_range,
      });
      setResult(response);
      addActivity({
        id: Date.now().toString(),
        title: 'Filing Strategy Created',
        description: 'Recommendations ready',
        timestamp: new Date().toISOString(),
        type: 'patent',
        content: response.strategy || response.response,
        toolUsed: 'Patent Filing Strategy Agent',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Strategy generation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleGeographic = (option: string) => {
    setFormData(prev => ({
      ...prev,
      geographic_interest: prev.geographic_interest.includes(option)
        ? prev.geographic_interest.filter(g => g !== option)
        : [...prev.geographic_interest, option]
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-teal-100 px-8 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-teal-100 rounded-lg transition-colors text-teal-600"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-teal-600 to-emerald-600 bg-clip-text text-transparent">
                Patent & IP Analysis
              </h1>
              <p className="text-slate-500 text-sm">Assess patentability and get filing strategies</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-8 bg-white p-2 rounded-xl w-fit shadow-sm">
          <button
            onClick={() => setActiveTab('assess')}
            className={`tab-btn flex items-center gap-2 ${activeTab === 'assess' ? 'active' : ''}`}
          >
            <Lightbulb size={18} />
            Patentability Assessment
          </button>
          <button
            onClick={() => setActiveTab('strategy')}
            className={`tab-btn flex items-center gap-2 ${activeTab === 'strategy' ? 'active' : ''}`}
          >
            <Globe size={18} />
            Filing Strategy
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="canva-card p-8">
            {activeTab === 'assess' ? (
              <>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-xl gradient-green flex items-center justify-center">
                    <Search size={24} className="text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-slate-800">Describe Your Invention</h2>
                    <p className="text-slate-500 text-sm">We'll assess its patentability</p>
                  </div>
                </div>

                <div className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Invention Description *
                    </label>
                    <textarea
                      value={formData.invention_description}
                      onChange={(e) => setFormData({ ...formData, invention_description: e.target.value })}
                      placeholder="Describe your invention in detail. What does it do? How does it work?"
                      className="canva-textarea w-full"
                      rows={5}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Industry
                    </label>
                    <select
                      value={formData.industry}
                      onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                      className="canva-select w-full"
                    >
                      <option value="">Select industry</option>
                      {industries.map(ind => (
                        <option key={ind} value={ind}>{ind}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      What makes it novel? *
                    </label>
                    <textarea
                      value={formData.novelty}
                      onChange={(e) => setFormData({ ...formData, novelty: e.target.value })}
                      placeholder="What's new or different about your invention compared to existing solutions?"
                      className="canva-textarea w-full"
                      rows={3}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Development Stage
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {developmentStages.map(stage => (
                        <button
                          key={stage}
                          onClick={() => setFormData({ ...formData, development_stage: stage })}
                          className={`chip ${formData.development_stage === stage ? 'selected' : ''}`}
                        >
                          {stage}
                        </button>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={handleAssess}
                    disabled={isLoading || !formData.invention_description || !formData.novelty}
                    className="w-full canva-btn flex items-center justify-center gap-2 py-4"
                    style={{ background: 'linear-gradient(135deg, #14b8a6 0%, #10b981 100%)' }}
                  >
                    {isLoading ? (
                      <>
                        <div className="spinner"></div>
                        <span>Analyzing patentability...</span>
                      </>
                    ) : (
                      <>
                        <Search size={20} />
                        <span>Assess Patentability</span>
                      </>
                    )}
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-xl gradient-green flex items-center justify-center">
                    <Globe size={24} className="text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-slate-800">Filing Strategy</h2>
                    <p className="text-slate-500 text-sm">Get recommendations for patent filing</p>
                  </div>
                </div>

                <div className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-3">
                      Geographic Interest (select all that apply)
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {geographicOptions.map(opt => (
                        <button
                          key={opt}
                          onClick={() => toggleGeographic(opt)}
                          className={`chip ${formData.geographic_interest.includes(opt) ? 'selected' : ''}`}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-3">
                      Budget Range
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {budgetOptions.map(budget => (
                        <button
                          key={budget}
                          onClick={() => setFormData({ ...formData, budget_range: budget })}
                          className={`p-3 rounded-xl border-2 text-sm transition-all ${
                            formData.budget_range === budget
                              ? 'border-teal-500 bg-teal-50 text-teal-700'
                              : 'border-slate-200 hover:border-teal-300 text-slate-600'
                          }`}
                        >
                          {budget}
                        </button>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={handleFilingStrategy}
                    disabled={isLoading}
                    className="w-full canva-btn flex items-center justify-center gap-2 py-4"
                    style={{ background: 'linear-gradient(135deg, #14b8a6 0%, #10b981 100%)' }}
                  >
                    {isLoading ? (
                      <>
                        <div className="spinner"></div>
                        <span>Creating strategy...</span>
                      </>
                    ) : (
                      <>
                        <FileText size={20} />
                        <span>Get Filing Strategy</span>
                      </>
                    )}
                  </button>
                </div>
              </>
            )}

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
                {error}
              </div>
            )}
          </div>

          {/* Result Section */}
          <div className="canva-card p-8 h-fit sticky top-24">
            <h2 className="text-xl font-semibold text-slate-800 mb-6">Analysis Results</h2>

            {!result && !isLoading && (
              <div className="flex flex-col items-center justify-center h-80 text-center">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-teal-100 to-emerald-100 flex items-center justify-center mb-4">
                  <Lightbulb size={32} className="text-teal-400" />
                </div>
                <p className="text-slate-500">
                  Fill in the form and submit<br />
                  to get your patent analysis
                </p>
              </div>
            )}

            {isLoading && (
              <div className="flex flex-col items-center justify-center h-80">
                <div className="spinner-large mb-4"></div>
                <p className="text-teal-600 font-medium">Analyzing...</p>
                <p className="text-slate-500 text-sm mt-1">This may take 30-60 seconds</p>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => {
                      const text = result.assessment || result.strategy || result.response || '';
                      navigator.clipboard.writeText(text);
                    }}
                    className="px-4 py-2 rounded-lg bg-teal-100 text-teal-700 text-sm font-medium hover:bg-teal-200"
                  >
                    Copy
                  </button>
                  <button
                    onClick={() => {
                      const text = result.assessment || result.strategy || result.response || '';
                      const blob = new Blob([text], { type: 'text/plain' });
                      const url = window.URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = 'patent_analysis.txt';
                      document.body.appendChild(a);
                      a.click();
                      document.body.removeChild(a);
                      window.URL.revokeObjectURL(url);
                    }}
                    className="px-4 py-2 rounded-lg bg-slate-100 text-slate-700 text-sm font-medium hover:bg-slate-200"
                  >
                    Download
                  </button>
                </div>

                <div className="bg-gradient-to-br from-teal-50 to-emerald-50 rounded-xl p-6 border border-teal-100 max-h-[600px] overflow-y-auto">
                  <ContentRenderer content={result.assessment || result.strategy || result.response} accentColor="teal" />
                </div>

                {result.sources && result.sources.length > 0 && (
                  <details className="bg-slate-50 rounded-xl border border-slate-200">
                    <summary className="px-4 py-3 cursor-pointer text-sm font-medium text-slate-600 hover:text-slate-800">
                      📚 Sources ({result.sources.length})
                    </summary>
                    <div className="px-4 pb-4 space-y-2">
                      {result.sources.slice(0, 5).map((source: any, i: number) => (
                        <div key={i} className="text-sm text-slate-500 flex items-start gap-2">
                          <span className="text-teal-400">•</span>
                          <span>{source.title || source.source}</span>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default PatentPage;

