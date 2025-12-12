import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import ActivityPanel from '../components/ActivityPanel';

interface FeatureCard {
  id: string;
  title: string;
  description: string;
  route: string;
  gradient: string;
}

const pitchFeatures: FeatureCard[] = [
  {
    id: 'pitch-deck',
    title: 'Generate Pitch Deck',
    description: 'Create slides and elevator pitches with AI.',
    route: '/pitch-deck',
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #f43f5e 100%)',
  },
];

const marketFeatures: FeatureCard[] = [
  {
    id: 'competitors',
    title: 'Analyze Competitors',
    description: 'Get competitive intelligence and market insights.',
    route: '/competitors',
    gradient: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
  },
  {
    id: 'marketing',
    title: 'Marketing Content',
    description: 'Generate social media posts with AI images.',
    route: '/marketing',
    gradient: 'linear-gradient(135deg, #ec4899 0%, #f43f5e 100%)',
  },
  {
    id: 'policy',
    title: 'Policy & Compliance',
    description: 'Generate privacy policy, terms of service.',
    route: '/policy',
    gradient: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
  },
];

const patentFeatures: FeatureCard[] = [
  {
    id: 'patentability',
    title: 'Patent & IP Analysis',
    description: 'Assess patentability and get filing strategies.',
    route: '/patentability',
    gradient: 'linear-gradient(135deg, #14b8a6 0%, #10b981 100%)',
  },
];

const teamFeatures: FeatureCard[] = [
  {
    id: 'team-analysis',
    title: 'Team Analysis',
    description: 'Get hiring recommendations and job descriptions.',
    route: '/team-analysis',
    gradient: 'linear-gradient(135deg, #8b5cf6 0%, #c026d3 100%)',
  },
];

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { company, logout } = useApp();

  const handleCardClick = (route: string) => {
    navigate(route);
  };

  const FeatureSection: React.FC<{
    title: string;
    features: FeatureCard[];
    accentColor: string;
  }> = ({ title, features, accentColor }) => (
    <div className="mb-8">
      <div className="flex items-center gap-3 mb-4">
        <div 
          className="w-10 h-1 rounded"
          style={{ background: accentColor }}
        ></div>
        <h2 className="text-xl font-semibold text-slate-800">{title}</h2>
      </div>
      <div className={`grid gap-4 ${features.length >= 3 ? 'grid-cols-3' : features.length === 2 ? 'grid-cols-2' : 'grid-cols-1'}`}>
        {features.map((feature) => (
          <button
            key={feature.id}
            onClick={() => handleCardClick(feature.route)}
            className="p-6 rounded-2xl text-white text-left card-hover shadow-lg"
            style={{ background: feature.gradient }}
          >
            <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
            <p className="text-sm opacity-90">{feature.description}</p>
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-fuchsia-50 via-purple-50 to-violet-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-purple-100 px-8 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold gradient-text">
              Welcome back, {company?.company_name}!
            </h1>
            <p className="text-slate-500 mt-1">Your AI-powered startup toolkit is ready.</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-100 to-pink-100 rounded-full text-sm font-medium text-purple-700">
              <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></span>
              TechScopeAI
            </div>
            <button
              onClick={logout}
              className="px-5 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:shadow-lg hover:shadow-purple-200 transition-all font-medium"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex min-h-[calc(100vh-80px)]">
        {/* Features Section - 2/3 width */}
        <main className="w-2/3 p-8">
          <FeatureSection
            title="Pitch & Presentation"
            features={pitchFeatures}
            accentColor="linear-gradient(135deg, #f59e0b 0%, #f43f5e 100%)"
          />
          <FeatureSection
            title="Market Intelligence"
            features={marketFeatures}
            accentColor="linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)"
          />
          <FeatureSection
            title="Patent & IP"
            features={patentFeatures}
            accentColor="linear-gradient(135deg, #14b8a6 0%, #10b981 100%)"
          />
          <FeatureSection
            title="Team"
            features={teamFeatures}
            accentColor="linear-gradient(135deg, #8b5cf6 0%, #c026d3 100%)"
          />

          {/* Chat Button */}
          <button
            onClick={() => navigate('/chat')}
            className="w-full mt-4 py-4 text-white font-semibold rounded-2xl btn-animate shadow-lg"
            style={{ background: 'linear-gradient(135deg, #7c3aed 0%, #c026d3 100%)' }}
          >
            Ask me anything
          </button>
        </main>

        {/* Activity Panel - 1/3 width */}
        <aside className="w-1/3 min-w-[400px] p-4 bg-gradient-to-b from-purple-900/5 to-purple-900/10">
          <ActivityPanel />
        </aside>
      </div>
    </div>
  );
};

export default Dashboard;
