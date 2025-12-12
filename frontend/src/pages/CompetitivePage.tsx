import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import { competitiveApi } from '../services/api';
import { ArrowLeft, Target, TrendingUp, BarChart3 } from 'lucide-react';
import ContentRenderer from '../components/ContentRenderer';

const analysisTypes = [
  { id: 'full', title: 'Full Competitive Analysis', description: 'Comprehensive competitor landscape analysis' },
  { id: 'specific', title: 'Specific Competitors', description: 'Analyze specific competitors you know' },
  { id: 'market', title: 'Market Overview', description: 'Industry trends and market positioning' },
];

const CompetitivePage: React.FC = () => {
  const navigate = useNavigate();
  const { company, addActivity } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    analysis_type: 'full',
    known_competitors: '',
    differentiation: '',
    focus_areas: [] as string[],
  });

  const focusOptions = [
    'Pricing Strategy',
    'Feature Comparison',
    'Market Position',
    'Marketing Approach',
    'Customer Segments',
    'Technology Stack',
    'Funding & Growth',
    'Strengths/Weaknesses',
  ];

  const handleAnalyze = async () => {
    if (!company) return;
    
    setIsLoading(true);
    setError('');
    setResult(null);
    
    try {
      const competitors = formData.known_competitors
        ? formData.known_competitors.split(',').map(c => c.trim()).filter(Boolean)
        : undefined;

      const response = await competitiveApi.analyze({
        company_id: company.id,
        specific_competitors: competitors,
      });
      setResult(response);
      addActivity({
        id: Date.now().toString(),
        title: 'Competitive Analysis Complete',
        description: `Analyzed ${competitors?.length || 'market'} competitors`,
        timestamp: new Date().toISOString(),
        type: 'competitive',
        content: response.analysis || response.response,
        toolUsed: 'Competitive Analysis Agent',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleFocus = (area: string) => {
    setFormData(prev => ({
      ...prev,
      focus_areas: prev.focus_areas.includes(area)
        ? prev.focus_areas.filter(a => a !== area)
        : [...prev.focus_areas, area]
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-indigo-100 px-8 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-indigo-100 rounded-lg transition-colors text-indigo-600"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Competitive Analysis
              </h1>
              <p className="text-slate-500 text-sm">Understand your competitive landscape</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="canva-card p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl gradient-blue flex items-center justify-center">
                <Target size={24} className="text-white" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-slate-800">Analysis Configuration</h2>
                <p className="text-slate-500 text-sm">Choose how you want to analyze competitors</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Analysis Type */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Analysis Type
                </label>
                <div className="space-y-3">
                  {analysisTypes.map(type => (
                    <button
                      key={type.id}
                      onClick={() => setFormData({ ...formData, analysis_type: type.id })}
                      className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
                        formData.analysis_type === type.id
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-slate-200 hover:border-indigo-300'
                      }`}
                    >
                      <div className="font-medium text-slate-800">{type.title}</div>
                      <div className="text-sm text-slate-500">{type.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Known Competitors (conditional) */}
              {formData.analysis_type === 'specific' && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Competitors (comma-separated)
                  </label>
                  <textarea
                    value={formData.known_competitors}
                    onChange={(e) => setFormData({ ...formData, known_competitors: e.target.value })}
                    placeholder="e.g., Competitor A, Competitor B, Competitor C"
                    className="canva-textarea w-full"
                    rows={3}
                  />
                </div>
              )}

              {/* Your Company Info Preview */}
              <div className="bg-indigo-50 rounded-xl p-4">
                <h3 className="font-medium text-indigo-800 mb-2">Analyzing For</h3>
                <div className="text-sm text-indigo-600 space-y-1">
                  <p><strong>Company:</strong> {company?.company_name}</p>
                  <p><strong>Industry:</strong> {company?.industry}</p>
                  <p><strong>Solution:</strong> {company?.solution?.substring(0, 100)}...</p>
                </div>
              </div>

              {/* Focus Areas */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Focus Areas (optional)
                </label>
                <div className="flex flex-wrap gap-2">
                  {focusOptions.map(area => (
                    <button
                      key={area}
                      onClick={() => toggleFocus(area)}
                      className={`chip ${formData.focus_areas.includes(area) ? 'selected' : ''}`}
                    >
                      {area}
                    </button>
                  ))}
                </div>
              </div>

              {/* Differentiation */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Your Key Differentiators
                </label>
                <textarea
                  value={formData.differentiation}
                  onChange={(e) => setFormData({ ...formData, differentiation: e.target.value })}
                  placeholder="What makes you different or better than competitors?"
                  className="canva-textarea w-full"
                  rows={3}
                />
              </div>

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={isLoading}
                className="w-full canva-btn flex items-center justify-center gap-2 py-4"
                style={{ background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' }}
              >
                {isLoading ? (
                  <>
                    <div className="spinner"></div>
                    <span>Analyzing competitors...</span>
                  </>
                ) : (
                  <>
                    <BarChart3 size={20} />
                    <span>Run Competitive Analysis</span>
                  </>
                )}
              </button>

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Result Section */}
          <div className="canva-card p-8 h-fit sticky top-24">
            <h2 className="text-xl font-semibold text-slate-800 mb-6">Analysis Results</h2>

            {!result && !isLoading && (
              <div className="flex flex-col items-center justify-center h-80 text-center">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center mb-4">
                  <TrendingUp size={32} className="text-indigo-400" />
                </div>
                <p className="text-slate-500">
                  Configure your analysis<br />
                  and click analyze to get insights
                </p>
              </div>
            )}

            {isLoading && (
              <div className="flex flex-col items-center justify-center h-80">
                <div className="spinner-large mb-4"></div>
                <p className="text-indigo-600 font-medium">Analyzing competitive landscape...</p>
                <p className="text-slate-500 text-sm mt-1">This may take 45-90 seconds</p>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => {
                      const text = result.analysis || result.response || '';
                      navigator.clipboard.writeText(text);
                    }}
                    className="px-4 py-2 rounded-lg bg-indigo-100 text-indigo-700 text-sm font-medium hover:bg-indigo-200"
                  >
                    Copy
                  </button>
                  <button
                    onClick={() => {
                      const text = result.analysis || result.response || '';
                      const blob = new Blob([text], { type: 'text/plain' });
                      const url = window.URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = 'competitive_analysis.txt';
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

                <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-6 border border-indigo-100 max-h-[600px] overflow-y-auto">
                  <ContentRenderer content={result.analysis || result.response} accentColor="indigo" />
                </div>

                {result.sources && result.sources.length > 0 && (
                  <details className="bg-slate-50 rounded-xl border border-slate-200">
                    <summary className="px-4 py-3 cursor-pointer text-sm font-medium text-slate-600 hover:text-slate-800">
                      📚 Sources ({result.sources.length})
                    </summary>
                    <div className="px-4 pb-4 space-y-2">
                      {result.sources.slice(0, 5).map((source: any, i: number) => (
                        <div key={i} className="text-sm text-slate-500 flex items-start gap-2">
                          <span className="text-indigo-400">•</span>
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

export default CompetitivePage;

