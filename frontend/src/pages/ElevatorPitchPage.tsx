import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import { pitchApi } from '../services/api';
import { ArrowLeft, Clock, FileText, Copy, Check } from 'lucide-react';

const ElevatorPitchPage: React.FC = () => {
  const navigate = useNavigate();
  const { company, addActivity } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [duration, setDuration] = useState(60);

  const handleGenerate = async () => {
    if (!company) return;
    
    setIsLoading(true);
    setError('');
    setResult(null);
    
    try {
      const response = await pitchApi.generateElevatorPitch({
        company_id: company.id,
        duration_seconds: duration,
      });
      setResult(response);
      addActivity({
        id: Date.now().toString(),
        title: 'Elevator Pitch Generated',
        description: `${duration}-second pitch created`,
        timestamp: new Date().toISOString(),
        type: 'elevator',
        content: response.elevator_pitch || response.response,
        toolUsed: 'Elevator Pitch Generator',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate elevator pitch');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (result?.elevator_pitch) {
      navigator.clipboard.writeText(result.elevator_pitch);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-fuchsia-50 via-purple-50 to-violet-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-purple-100 px-8 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-purple-100 rounded-lg transition-colors text-purple-600"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold gradient-text">Elevator Pitch Generator</h1>
              <p className="text-slate-500 text-sm">Create a compelling pitch in seconds</p>
            </div>
          </div>
          <div className="text-sm text-purple-600 font-medium">
            {company?.company_name}
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="canva-card p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl gradient-pink flex items-center justify-center">
                <Clock size={24} className="text-white" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-slate-800">Configure Your Pitch</h2>
                <p className="text-slate-500 text-sm">Choose duration and style</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Duration Selection */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Pitch Duration
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[30, 60, 90].map((sec) => (
                    <button
                      key={sec}
                      onClick={() => setDuration(sec)}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        duration === sec
                          ? 'border-purple-500 bg-purple-50 text-purple-700'
                          : 'border-purple-100 hover:border-purple-300 text-slate-600'
                      }`}
                    >
                      <div className="text-2xl font-bold">{sec}s</div>
                      <div className="text-xs mt-1">
                        {sec === 30 ? 'Quick' : sec === 60 ? 'Standard' : 'Detailed'}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Company Info Preview */}
              <div className="bg-purple-50 rounded-xl p-4">
                <h3 className="font-medium text-purple-800 mb-2">Using Your Company Info</h3>
                <div className="text-sm text-purple-600 space-y-1">
                  <p><strong>Company:</strong> {company?.company_name}</p>
                  <p><strong>Industry:</strong> {company?.industry}</p>
                  <p><strong>Stage:</strong> {company?.current_stage}</p>
                </div>
              </div>

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={isLoading}
                className="w-full canva-btn flex items-center justify-center gap-2 py-4"
              >
                {isLoading ? (
                  <>
                    <div className="spinner"></div>
                    <span>Crafting your pitch...</span>
                  </>
                ) : (
                  <>
                    <FileText size={20} />
                    <span>Generate Elevator Pitch</span>
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
          <div className="canva-card p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-slate-800">Your Elevator Pitch</h2>
              {result && (
                <button
                  onClick={copyToClipboard}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
                >
                  {copied ? <Check size={16} /> : <Copy size={16} />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              )}
            </div>

            {!result && !isLoading && (
              <div className="flex flex-col items-center justify-center h-64 text-center">
                <div className="w-20 h-20 rounded-full bg-purple-100 flex items-center justify-center mb-4">
                  <FileText size={32} className="text-purple-400" />
                </div>
                <p className="text-slate-500">
                  Configure your settings and click generate<br />
                  to create your elevator pitch
                </p>
              </div>
            )}

            {isLoading && (
              <div className="flex flex-col items-center justify-center h-64">
                <div className="spinner-large mb-4"></div>
                <p className="text-purple-600 font-medium">Crafting your pitch...</p>
                <p className="text-slate-500 text-sm mt-1">This usually takes 10-20 seconds</p>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                <div className="flex items-center gap-4 text-sm text-slate-500 mb-4">
                  <span className="flex items-center gap-1">
                    <Clock size={14} />
                    {result.duration_seconds || duration}s
                  </span>
                  <span>~{result.estimated_words || Math.round(duration * 2.5)} words</span>
                </div>

                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-100">
                  <p className="text-slate-700 leading-relaxed text-lg">
                    {result.elevator_pitch || result.response}
                  </p>
                </div>

                {/* Tips */}
                <div className="bg-amber-50 rounded-xl p-4 border border-amber-200">
                  <h4 className="font-medium text-amber-800 mb-2">Delivery Tips</h4>
                  <ul className="text-sm text-amber-700 space-y-1">
                    <li>• Speak confidently and maintain eye contact</li>
                    <li>• Practice until it feels natural, not memorized</li>
                    <li>• Adjust your energy to match the setting</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default ElevatorPitchPage;

