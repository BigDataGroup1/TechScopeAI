import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import { teamApi } from '../services/api';
import { ArrowLeft, Users, TrendingUp, Star } from 'lucide-react';
import ContentRenderer from '../components/ContentRenderer';

const teamSizes = ['Just founders', '2-5 people', '6-10 people', '11-20 people', '20+ people'];

const existingRoles = [
  'CEO/Founder',
  'CTO/Technical Lead',
  'CMO/Marketing Lead',
  'CFO/Finance',
  'Sales Lead',
  'Product Manager',
  'Engineers/Developers',
  'Designers',
  'Operations',
  'Customer Success',
];

const teamGaps = [
  'Technical/Engineering',
  'Product Management',
  'Marketing/Growth',
  'Sales/Business Development',
  'Design/UX',
  'Operations',
  'Finance/Accounting',
  'Customer Success/Support',
  'Data Science/Analytics',
  'DevOps/Infrastructure',
];

const priorities = [
  'Immediate (within 1 month)',
  'Short-term (1-3 months)',
  'Medium-term (3-6 months)',
  'Long-term (6+ months)',
];

const TeamAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const { company, addActivity } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    current_team_size: '',
    existing_roles: [] as string[],
    team_gaps: [] as string[],
    hiring_priority: '',
    challenges: '',
    budget_constraints: '',
  });

  const handleAnalyze = async () => {
    if (!company) return;
    
    setIsLoading(true);
    setError('');
    setResult(null);
    
    try {
      const response = await teamApi.analyze({
        company_id: company.id,
        current_team: `
          Team size: ${formData.current_team_size}
          Existing roles: ${formData.existing_roles.join(', ')}
          Budget constraints: ${formData.budget_constraints}
        `,
        challenges: `
          Team gaps: ${formData.team_gaps.join(', ')}
          Hiring priority: ${formData.hiring_priority}
          Challenges: ${formData.challenges}
        `,
      });
      setResult(response);
      addActivity({
        id: Date.now().toString(),
        title: 'Team Analysis Complete',
        description: 'Hiring recommendations ready',
        timestamp: new Date().toISOString(),
        type: 'team',
        content: response.analysis || response.response,
        toolUsed: 'Team Analysis Agent',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleRole = (role: string) => {
    setFormData(prev => ({
      ...prev,
      existing_roles: prev.existing_roles.includes(role)
        ? prev.existing_roles.filter(r => r !== role)
        : [...prev.existing_roles, role]
    }));
  };

  const toggleGap = (gap: string) => {
    setFormData(prev => ({
      ...prev,
      team_gaps: prev.team_gaps.includes(gap)
        ? prev.team_gaps.filter(g => g !== gap)
        : [...prev.team_gaps, gap]
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-fuchsia-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-purple-100 px-8 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-purple-100 rounded-lg transition-colors text-purple-600"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold gradient-text">Team Analysis</h1>
              <p className="text-slate-500 text-sm">Get hiring recommendations and job descriptions</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="canva-card p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl gradient-purple flex items-center justify-center">
                <Users size={24} className="text-white" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-slate-800">Your Team Profile</h2>
                <p className="text-slate-500 text-sm">Tell us about your current team</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Team Size */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Current Team Size
                </label>
                <div className="flex flex-wrap gap-2">
                  {teamSizes.map(size => (
                    <button
                      key={size}
                      onClick={() => setFormData({ ...formData, current_team_size: size })}
                      className={`chip ${formData.current_team_size === size ? 'selected' : ''}`}
                    >
                      {size}
                    </button>
                  ))}
                </div>
              </div>

              {/* Existing Roles */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Existing Roles (select all that apply)
                </label>
                <div className="flex flex-wrap gap-2">
                  {existingRoles.map(role => (
                    <button
                      key={role}
                      onClick={() => toggleRole(role)}
                      className={`chip ${formData.existing_roles.includes(role) ? 'selected' : ''}`}
                    >
                      {role}
                    </button>
                  ))}
                </div>
              </div>

              {/* Team Gaps */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Team Gaps/Needs (select all that apply)
                </label>
                <div className="flex flex-wrap gap-2">
                  {teamGaps.map(gap => (
                    <button
                      key={gap}
                      onClick={() => toggleGap(gap)}
                      className={`chip ${formData.team_gaps.includes(gap) ? 'selected' : ''}`}
                    >
                      {gap}
                    </button>
                  ))}
                </div>
              </div>

              {/* Hiring Priority */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Hiring Priority
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {priorities.map(priority => (
                    <button
                      key={priority}
                      onClick={() => setFormData({ ...formData, hiring_priority: priority })}
                      className={`p-3 rounded-xl border-2 text-sm transition-all ${
                        formData.hiring_priority === priority
                          ? 'border-purple-500 bg-purple-50 text-purple-700'
                          : 'border-slate-200 hover:border-purple-300 text-slate-600'
                      }`}
                    >
                      {priority}
                    </button>
                  ))}
                </div>
              </div>

              {/* Challenges */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Current Challenges
                </label>
                <textarea
                  value={formData.challenges}
                  onChange={(e) => setFormData({ ...formData, challenges: e.target.value })}
                  placeholder="What challenges is your team facing? What bottlenecks do you have?"
                  className="canva-textarea w-full"
                  rows={3}
                />
              </div>

              {/* Budget */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Budget Constraints
                </label>
                <input
                  type="text"
                  value={formData.budget_constraints}
                  onChange={(e) => setFormData({ ...formData, budget_constraints: e.target.value })}
                  placeholder="e.g., $50k-80k per hire, limited runway"
                  className="canva-input w-full"
                />
              </div>

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={isLoading || !formData.current_team_size || formData.team_gaps.length === 0}
                className="w-full canva-btn flex items-center justify-center gap-2 py-4"
              >
                {isLoading ? (
                  <>
                    <div className="spinner"></div>
                    <span>Analyzing team needs...</span>
                  </>
                ) : (
                  <>
                    <TrendingUp size={20} />
                    <span>Get Hiring Recommendations</span>
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
          <div className="canva-card p-8 h-fit">
            <h2 className="text-xl font-semibold text-slate-800 mb-6 flex items-center gap-2">
              <Star className="text-purple-500" size={22} />
              Hiring Recommendations
            </h2>

            {!result && !isLoading && (
              <div className="flex flex-col items-center justify-center h-80 text-center">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-violet-100 to-purple-100 flex items-center justify-center mb-4">
                  <Users size={32} className="text-purple-400" />
                </div>
                <p className="text-slate-500">
                  Fill in your team profile<br />
                  to get personalized recommendations
                </p>
                <p className="text-slate-400 text-sm mt-2">
                  Including job roles & descriptions
                </p>
              </div>
            )}

            {isLoading && (
              <div className="flex flex-col items-center justify-center h-80">
                <div className="spinner-large mb-4"></div>
                <p className="text-purple-600 font-medium">Analyzing your team...</p>
                <p className="text-slate-500 text-sm mt-1">Generating role recommendations</p>
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
                    className="px-4 py-2 rounded-lg bg-purple-100 text-purple-700 text-sm font-medium hover:bg-purple-200"
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
                      a.download = 'team_analysis.txt';
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

                <div className="max-h-[700px] overflow-y-auto pr-2">
                  <ContentRenderer content={result.analysis || result.response} accentColor="purple" />
                </div>

                {result.sources && result.sources.length > 0 && (
                  <details className="bg-slate-50 rounded-xl border border-slate-200 mt-4">
                    <summary className="px-4 py-3 cursor-pointer text-sm font-medium text-slate-600 hover:text-slate-800">
                      📚 Sources ({result.sources.length})
                    </summary>
                    <div className="px-4 pb-4 space-y-2">
                      {result.sources.slice(0, 5).map((source: any, i: number) => (
                        <div key={i} className="text-sm text-slate-500 flex items-start gap-2">
                          <span className="text-purple-400">•</span>
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

export default TeamAnalysisPage;
