import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import { marketingApi } from '../services/api';
import { ArrowLeft, Sparkles, Image, Instagram, Linkedin, Download } from 'lucide-react';
import ContentRenderer from '../components/ContentRenderer';

const platformOptions = ['Instagram', 'LinkedIn', 'Both'];
const contentTypeOptions = [
  'Single Post',
  'Carousel Post',
  'Story',
  'Reel/Video Script',
  'Content Series',
];
const styleOptions = ['Quirky/Fun', 'Professional', 'Trendy/Modern', 'Mix of styles'];

const MarketingPage: React.FC = () => {
  const navigate = useNavigate();
  const { company, addActivity } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    platform: 'Instagram',
    content_type: 'Single Post',
    style: 'Professional',
    description: '',
    target_audience: '',
    campaign_goal: '',
    generate_image: true,
  });

  const handleGenerate = async () => {
    if (!company || !formData.description) return;
    
    setIsLoading(true);
    setError('');
    setResult(null);
    
    try {
      const response = await marketingApi.generateContent({
        company_id: company.id,
        platform: formData.platform,
        content_type: formData.content_type,
        description: formData.description,
        generate_image: formData.generate_image,
        image_provider: 'openai',
      });
      setResult(response);
      addActivity({
        id: Date.now().toString(),
        title: 'Marketing Content Created',
        description: `${formData.platform} ${formData.content_type}`,
        timestamp: new Date().toISOString(),
        type: 'marketing',
        content: response.response || response.content,
        toolUsed: 'Marketing Content Agent',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate content');
    } finally {
      setIsLoading(false);
    }
  };

  const ChipSelect: React.FC<{
    options: string[];
    value: string;
    onChange: (val: string) => void;
  }> = ({ options, value, onChange }) => (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => (
        <button
          key={opt}
          onClick={() => onChange(opt)}
          className={`chip ${value === opt ? 'selected' : ''}`}
        >
          {opt}
        </button>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-fuchsia-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-pink-100 px-8 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-pink-100 rounded-lg transition-colors text-pink-600"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold gradient-text">Marketing Content Generator</h1>
              <p className="text-slate-500 text-sm">Create engaging social media content with AI</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="space-y-6">
            <div className="canva-card p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-xl gradient-pink flex items-center justify-center">
                  <Sparkles size={24} className="text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-slate-800">Content Settings</h2>
                  <p className="text-slate-500 text-sm">Configure your marketing content</p>
                </div>
              </div>

              <div className="space-y-6">
                {/* Platform */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-3">
                    Platform
                  </label>
                  <div className="flex gap-4">
                    {platformOptions.map((platform) => (
                      <button
                        key={platform}
                        onClick={() => setFormData({ ...formData, platform })}
                        className={`flex-1 p-4 rounded-xl border-2 transition-all flex items-center justify-center gap-2 ${
                          formData.platform === platform
                            ? 'border-pink-500 bg-pink-50 text-pink-700'
                            : 'border-pink-100 hover:border-pink-300 text-slate-600'
                        }`}
                      >
                        {platform === 'Instagram' && <Instagram size={20} />}
                        {platform === 'LinkedIn' && <Linkedin size={20} />}
                        {platform === 'Both' && (
                          <>
                            <Instagram size={16} />
                            <Linkedin size={16} />
                          </>
                        )}
                        <span className="font-medium">{platform}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Content Type */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-3">
                    Content Type
                  </label>
                  <ChipSelect
                    options={contentTypeOptions}
                    value={formData.content_type}
                    onChange={(val) => setFormData({ ...formData, content_type: val })}
                  />
                </div>

                {/* Style */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-3">
                    Content Style
                  </label>
                  <ChipSelect
                    options={styleOptions}
                    value={formData.style}
                    onChange={(val) => setFormData({ ...formData, style: val })}
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Content Description *
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe what you want to post about... e.g., 'Announce our new AI feature that helps users save time'"
                    className="canva-textarea w-full"
                    rows={4}
                  />
                </div>

                {/* Target Audience */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Target Audience
                  </label>
                  <input
                    type="text"
                    value={formData.target_audience}
                    onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
                    placeholder="e.g., Tech professionals, Small business owners"
                    className="canva-input w-full"
                  />
                </div>

                {/* Generate Image Toggle */}
                <div className="flex items-center justify-between p-4 bg-purple-50 rounded-xl">
                  <div className="flex items-center gap-3">
                    <Image size={20} className="text-purple-600" />
                    <div>
                      <p className="font-medium text-slate-800">Generate AI Image</p>
                      <p className="text-sm text-slate-500">Create a matching image with DALL-E</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setFormData({ ...formData, generate_image: !formData.generate_image })}
                    className={`w-12 h-6 rounded-full transition-colors ${
                      formData.generate_image ? 'bg-purple-500' : 'bg-slate-300'
                    }`}
                  >
                    <div
                      className={`w-5 h-5 bg-white rounded-full shadow transform transition-transform ${
                        formData.generate_image ? 'translate-x-6' : 'translate-x-0.5'
                      }`}
                    />
                  </button>
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerate}
                  disabled={isLoading || !formData.description}
                  className="w-full canva-btn flex items-center justify-center gap-2 py-4"
                >
                  {isLoading ? (
                    <>
                      <div className="spinner"></div>
                      <span>Creating your content...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles size={20} />
                      <span>Generate Content</span>
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
          </div>

          {/* Result Section */}
          <div className="canva-card p-8 h-fit sticky top-24">
            <h2 className="text-xl font-semibold text-slate-800 mb-6">Generated Content</h2>

            {!result && !isLoading && (
              <div className="flex flex-col items-center justify-center h-96 text-center">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-pink-100 to-purple-100 flex items-center justify-center mb-4">
                  <Sparkles size={32} className="text-purple-400" />
                </div>
                <p className="text-slate-500">
                  Configure your content settings<br />
                  and click generate to create posts
                </p>
              </div>
            )}

            {isLoading && (
              <div className="flex flex-col items-center justify-center h-96">
                <div className="spinner-large mb-4 pulse-generating"></div>
                <p className="text-purple-600 font-medium">Creating your content...</p>
                <p className="text-slate-500 text-sm mt-1">
                  {formData.generate_image 
                    ? 'Generating text and image (30-60s)'
                    : 'This usually takes 15-30 seconds'
                  }
                </p>
              </div>
            )}

            {result && (
              <div className="space-y-6">
                {/* Generated Image */}
                {result.image_path && (
                  <div className="image-preview">
                    <img
                      src={`http://localhost:8000${result.image_path}`}
                      alt="Generated marketing image"
                      className="w-full rounded-lg"
                    />
                    <div className="p-4 bg-slate-50 flex justify-between items-center">
                      <span className="text-sm text-slate-500">AI Generated Image</span>
                      <a
                        href={`http://localhost:8000${result.image_path}`}
                        download
                        className="flex items-center gap-2 text-purple-600 hover:text-purple-800"
                      >
                        <Download size={16} />
                        Download
                      </a>
                    </div>
                  </div>
                )}

                {/* Content Text */}
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-100">
                  <h3 className="font-semibold text-slate-800 mb-3">
                    {formData.platform} Post
                  </h3>
                  <ContentRenderer content={result.response || result.content} accentColor="purple" />
                </div>

                {/* Hashtags */}
                {result.hashtags && (
                  <div className="p-4 bg-blue-50 rounded-xl">
                    <h4 className="font-medium text-blue-800 mb-2">Suggested Hashtags</h4>
                    <p className="text-blue-600 text-sm">{result.hashtags}</p>
                  </div>
                )}

                {/* Sources */}
                {result.sources && result.sources.length > 0 && (
                  <details className="sources-section">
                    <summary className="sources-header">
                      <span className="font-medium text-slate-700">Sources ({result.sources.length})</span>
                    </summary>
                    <div className="p-4 space-y-2">
                      {result.sources.map((source: any, i: number) => (
                        <div key={i} className="text-sm text-slate-600">
                          {source.title || source.source}
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

export default MarketingPage;

