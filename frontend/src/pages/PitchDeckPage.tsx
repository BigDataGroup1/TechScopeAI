import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import { pitchApi } from '../services/api';
import { ArrowLeft, Presentation, Clock, Download, ChevronLeft, ChevronRight, ExternalLink, Sparkles } from 'lucide-react';

type TabType = 'slides' | 'elevator';
type OutputFormat = 'pptx' | 'gamma';

const PitchDeckPage: React.FC = () => {
  const navigate = useNavigate();
  const { company, addActivity } = useApp();
  const [activeTab, setActiveTab] = useState<TabType>('slides');
  const [isLoading, setIsLoading] = useState(false);
  const [slidesResult, setSlidesResult] = useState<any>(null);
  const [elevatorResult, setElevatorResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [currentSlide, setCurrentSlide] = useState(0);
  const [duration, setDuration] = useState(60);
  const [outputFormat, setOutputFormat] = useState<OutputFormat>('pptx');

  const [settings, setSettings] = useState({
    enhance_with_ai: true,
    ai_provider: 'auto',
  });

  const handleGenerateSlides = async () => {
    if (!company) return;
    
    setIsLoading(true);
    setError('');
    setSlidesResult(null);
    
    try {
      const response = await pitchApi.generateDeck({
        company_id: company.id,
        ...settings,
        gamma_only: outputFormat === 'gamma',
      });
      setSlidesResult(response);
      // Build content summary from slides
      const slidesContent = response.slides?.map((s: any, i: number) => 
        `Slide ${i + 1}: ${s.title}\n${s.content}\n${s.key_points ? 'Key Points: ' + s.key_points.join(', ') : ''}`
      ).join('\n\n') || '';
      addActivity({
        id: Date.now().toString(),
        title: 'Pitch Deck Generated',
        description: `${response.total_slides || 'Multiple'} slides created${outputFormat === 'gamma' ? ' (Gamma)' : ''}`,
        timestamp: new Date().toISOString(),
        type: 'pitch',
        content: slidesContent,
        toolUsed: 'Pitch Deck Generator',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate pitch deck');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPptx = async () => {
    if (!slidesResult?.pptx_path) return;
    
    try {
      // Extract filename from path (e.g., "exports/Company_deck.pptx" -> "Company_deck.pptx")
      const filename = slidesResult.pptx_path.split('/').pop();
      const sessionId = localStorage.getItem('sessionId');
      
      const response = await fetch(`http://localhost:8000/api/pitch/download/${filename}`, {
        headers: {
          'X-Session-ID': sessionId || '',
        },
      });
      
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError('Failed to download PPTX: ' + (err.message || 'Unknown error'));
    }
  };

  const handleGenerateElevator = async () => {
    if (!company) return;
    
    setIsLoading(true);
    setError('');
    setElevatorResult(null);
    
    try {
      const response = await pitchApi.generateElevatorPitch({
        company_id: company.id,
        duration_seconds: duration,
      });
      setElevatorResult(response);
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

  const slides = slidesResult?.slides || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-orange-100 px-8 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-orange-100 rounded-lg transition-colors text-orange-600"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-rose-600 bg-clip-text text-transparent">
                Pitch Generator
              </h1>
              <p className="text-slate-500 text-sm">Create pitch decks and elevator pitches</p>
            </div>
          </div>
          <div className="text-sm text-orange-600 font-medium">
            {company?.company_name}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-8 bg-white p-2 rounded-xl w-fit shadow-sm">
          <button
            onClick={() => setActiveTab('slides')}
            className={`tab-btn flex items-center gap-2 ${activeTab === 'slides' ? 'active' : ''}`}
            style={activeTab === 'slides' ? { background: 'linear-gradient(135deg, #f59e0b 0%, #f43f5e 100%)' } : {}}
          >
            <Presentation size={18} />
            Generate Slides
          </button>
          <button
            onClick={() => setActiveTab('elevator')}
            className={`tab-btn flex items-center gap-2 ${activeTab === 'elevator' ? 'active' : ''}`}
            style={activeTab === 'elevator' ? { background: 'linear-gradient(135deg, #f59e0b 0%, #f43f5e 100%)' } : {}}
          >
            <Clock size={18} />
            Elevator Pitch
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="canva-card p-8">
            {activeTab === 'slides' ? (
              <>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-xl gradient-orange flex items-center justify-center">
                    <Presentation size={24} className="text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-slate-800">Generate Pitch Deck</h2>
                    <p className="text-slate-500 text-sm">Create a complete slide deck with AI</p>
                  </div>
                </div>

                <div className="space-y-6">
                  {/* Company Info Preview */}
                  <div className="bg-orange-50 rounded-xl p-4">
                    <h3 className="font-medium text-orange-800 mb-2">Using Your Company Info</h3>
                    <div className="text-sm text-orange-600 space-y-1">
                      <p><strong>Company:</strong> {company?.company_name}</p>
                      <p><strong>Industry:</strong> {company?.industry}</p>
                      <p><strong>Stage:</strong> {company?.current_stage}</p>
                      <p><strong>Problem:</strong> {company?.problem?.substring(0, 100)}...</p>
                    </div>
                  </div>

                  {/* Output Format Selection */}
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-3">
                      Output Format
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        onClick={() => setOutputFormat('pptx')}
                        className={`p-4 rounded-xl border-2 transition-all text-left ${
                          outputFormat === 'pptx'
                            ? 'border-orange-500 bg-orange-50'
                            : 'border-orange-100 hover:border-orange-300'
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <Presentation size={18} className={outputFormat === 'pptx' ? 'text-orange-600' : 'text-slate-500'} />
                          <span className={`font-semibold ${outputFormat === 'pptx' ? 'text-orange-700' : 'text-slate-700'}`}>
                            PowerPoint
                          </span>
                        </div>
                        <p className="text-xs text-slate-500">Download .pptx file</p>
                      </button>
                      <button
                        onClick={() => setOutputFormat('gamma')}
                        className={`p-4 rounded-xl border-2 transition-all text-left ${
                          outputFormat === 'gamma'
                            ? 'border-purple-500 bg-purple-50'
                            : 'border-purple-100 hover:border-purple-300'
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <Sparkles size={18} className={outputFormat === 'gamma' ? 'text-purple-600' : 'text-slate-500'} />
                          <span className={`font-semibold ${outputFormat === 'gamma' ? 'text-purple-700' : 'text-slate-700'}`}>
                            Gamma.ai
                          </span>
                        </div>
                        <p className="text-xs text-slate-500">Beautiful web slides</p>
                      </button>
                    </div>
                  </div>

                  {/* AI Enhancement Toggle */}
                  <div className="flex items-center justify-between p-4 bg-amber-50 rounded-xl">
                    <div>
                      <p className="font-medium text-slate-800">AI Enhancement</p>
                      <p className="text-sm text-slate-500">Improve content with AI suggestions</p>
                    </div>
                    <button
                      onClick={() => setSettings({ ...settings, enhance_with_ai: !settings.enhance_with_ai })}
                      className={`w-12 h-6 rounded-full transition-colors ${
                        settings.enhance_with_ai ? 'bg-orange-500' : 'bg-slate-300'
                      }`}
                    >
                      <div
                        className={`w-5 h-5 bg-white rounded-full shadow transform transition-transform ${
                          settings.enhance_with_ai ? 'translate-x-6' : 'translate-x-0.5'
                        }`}
                      />
                    </button>
                  </div>

                  {/* Generate Button */}
                  <button
                    onClick={handleGenerateSlides}
                    disabled={isLoading}
                    className="w-full canva-btn flex items-center justify-center gap-2 py-4"
                    style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #f43f5e 100%)' }}
                  >
                    {isLoading ? (
                      <>
                        <div className="spinner"></div>
                        <span>Creating your deck...</span>
                      </>
                    ) : (
                      <>
                        <Presentation size={20} />
                        <span>Generate Pitch Deck</span>
                      </>
                    )}
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-xl gradient-orange flex items-center justify-center">
                    <Clock size={24} className="text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-slate-800">Elevator Pitch</h2>
                    <p className="text-slate-500 text-sm">Create a compelling verbal pitch</p>
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
                              ? 'border-orange-500 bg-orange-50 text-orange-700'
                              : 'border-orange-100 hover:border-orange-300 text-slate-600'
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
                  <div className="bg-orange-50 rounded-xl p-4">
                    <h3 className="font-medium text-orange-800 mb-2">Using Your Company Info</h3>
                    <div className="text-sm text-orange-600 space-y-1">
                      <p><strong>Company:</strong> {company?.company_name}</p>
                      <p><strong>Industry:</strong> {company?.industry}</p>
                      <p><strong>Stage:</strong> {company?.current_stage}</p>
                    </div>
                  </div>

                  {/* Generate Button */}
                  <button
                    onClick={handleGenerateElevator}
                    disabled={isLoading}
                    className="w-full canva-btn flex items-center justify-center gap-2 py-4"
                    style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #f43f5e 100%)' }}
                  >
                    {isLoading ? (
                      <>
                        <div className="spinner"></div>
                        <span>Crafting your pitch...</span>
                      </>
                    ) : (
                      <>
                        <Clock size={20} />
                        <span>Generate Elevator Pitch</span>
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
          <div className="canva-card p-8 h-fit">
            {activeTab === 'slides' ? (
              <>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-slate-800">
                    {outputFormat === 'gamma' ? 'Gamma Presentation' : 'Generated Slides'}
                  </h2>
                  <div className="flex gap-2">
                    {/* PPTX Download */}
                    {slidesResult?.pptx_path && (
                      <button
                        onClick={handleDownloadPptx}
                        className="flex items-center gap-2 px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors"
                      >
                        <Download size={16} />
                        Download PPTX
                      </button>
                    )}
                  </div>
                </div>

                {!slidesResult && !isLoading && (
                  <div className="flex flex-col items-center justify-center h-80 text-center">
                    <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-4 ${
                      outputFormat === 'gamma' 
                        ? 'bg-gradient-to-br from-purple-100 to-violet-100' 
                        : 'bg-gradient-to-br from-orange-100 to-rose-100'
                    }`}>
                      {outputFormat === 'gamma' ? (
                        <Sparkles size={32} className="text-purple-400" />
                      ) : (
                        <Presentation size={32} className="text-orange-400" />
                      )}
                    </div>
                    <p className="text-slate-500">
                      Click generate to create<br />
                      {outputFormat === 'gamma' ? 'your Gamma.ai presentation' : 'your professional pitch deck'}
                    </p>
                  </div>
                )}

                {isLoading && activeTab === 'slides' && (
                  <div className="flex flex-col items-center justify-center h-80">
                    <div className="spinner-large mb-4"></div>
                    <p className={outputFormat === 'gamma' ? 'text-purple-600 font-medium' : 'text-orange-600 font-medium'}>
                      {outputFormat === 'gamma' ? 'Creating Gamma presentation...' : 'Creating your deck...'}
                    </p>
                    <p className="text-slate-500 text-sm mt-1">This usually takes 30-60 seconds</p>
                  </div>
                )}

                {/* Gamma Result - Show URL prominently */}
                {slidesResult && outputFormat === 'gamma' && (
                  <div className="space-y-6">
                    {slidesResult.gamma_presentation?.success && slidesResult.gamma_presentation?.presentation_url ? (
                      <>
                        <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl p-6 border border-purple-200 text-center">
                          <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-purple-400 to-violet-500 flex items-center justify-center mb-4">
                            <Sparkles size={28} className="text-white" />
                          </div>
                          <h3 className="text-xl font-semibold text-purple-800 mb-2">
                            Presentation Ready!
                          </h3>
                          <p className="text-purple-600 mb-4">
                            Your Gamma.ai presentation has been created
                          </p>
                          <a
                            href={slidesResult.gamma_presentation.presentation_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-violet-500 text-white rounded-xl hover:from-purple-600 hover:to-violet-600 transition-all font-medium shadow-lg"
                          >
                            <ExternalLink size={20} />
                            Open in Gamma.ai
                          </a>
                        </div>
                        
                        {/* URL Display */}
                        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                          <p className="text-sm text-slate-500 mb-2">Presentation URL:</p>
                          <div className="flex items-center gap-2">
                            <input
                              type="text"
                              value={slidesResult.gamma_presentation.presentation_url}
                              readOnly
                              className="flex-1 bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700"
                            />
                            <button
                              onClick={() => {
                                navigator.clipboard.writeText(slidesResult.gamma_presentation.presentation_url);
                              }}
                              className="px-3 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors text-sm"
                            >
                              Copy
                            </button>
                          </div>
                        </div>

                        {/* Slides preview if available */}
                        {slides.length > 0 && (
                          <div className="bg-purple-50 rounded-xl p-4 border border-purple-100">
                            <h4 className="font-medium text-purple-800 mb-2">Slides Generated: {slides.length}</h4>
                            <p className="text-sm text-purple-600">View them in your Gamma presentation</p>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="bg-red-50 rounded-xl p-6 border border-red-200 text-center">
                        <p className="text-red-600 font-medium mb-2">Gamma generation failed</p>
                        <p className="text-red-500 text-sm">
                          {slidesResult.gamma_presentation?.error || slidesResult.gamma_presentation?.message || 'Unknown error'}
                        </p>
                        <p className="text-slate-500 text-sm mt-3">
                          Make sure GAMMA_API_KEY is set in your .env file
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* PPTX Result - Show slide navigation */}
                {slidesResult && outputFormat === 'pptx' && slides.length > 0 && (
                  <div className="space-y-4">
                    {/* Slide Navigation */}
                    <div className="flex items-center justify-between bg-slate-100 rounded-xl p-3">
                      <button
                        onClick={() => setCurrentSlide(Math.max(0, currentSlide - 1))}
                        disabled={currentSlide === 0}
                        className="p-2 rounded-lg hover:bg-white disabled:opacity-50 transition-colors"
                      >
                        <ChevronLeft size={20} />
                      </button>
                      <span className="font-medium text-slate-700">
                        Slide {currentSlide + 1} of {slides.length}
                      </span>
                      <button
                        onClick={() => setCurrentSlide(Math.min(slides.length - 1, currentSlide + 1))}
                        disabled={currentSlide === slides.length - 1}
                        className="p-2 rounded-lg hover:bg-white disabled:opacity-50 transition-colors"
                      >
                        <ChevronRight size={20} />
                      </button>
                    </div>

                    {/* Current Slide */}
                    <div className="bg-gradient-to-br from-orange-50 to-rose-50 rounded-xl p-6 border border-orange-100">
                      <h3 className="text-lg font-semibold text-slate-800 mb-3">
                        {slides[currentSlide]?.title}
                      </h3>
                      <div className="text-slate-700 whitespace-pre-wrap">
                        {slides[currentSlide]?.content}
                      </div>
                      {slides[currentSlide]?.key_points && (
                        <div className="mt-4">
                          <h4 className="font-medium text-slate-700 mb-2">Key Points:</h4>
                          <ul className="list-disc list-inside text-slate-600 space-y-1">
                            {slides[currentSlide].key_points.map((point: string, i: number) => (
                              <li key={i}>{point}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {/* Slide Thumbnails */}
                    <div className="flex gap-2 overflow-x-auto pb-2">
                      {slides.map((slide: any, idx: number) => (
                        <button
                          key={idx}
                          onClick={() => setCurrentSlide(idx)}
                          className={`flex-shrink-0 w-24 h-16 rounded-lg border-2 p-2 text-xs text-left transition-all ${
                            currentSlide === idx
                              ? 'border-orange-500 bg-orange-50'
                              : 'border-slate-200 hover:border-orange-300'
                          }`}
                        >
                          <div className="font-medium truncate">{slide.title}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <>
                <h2 className="text-xl font-semibold text-slate-800 mb-6">Your Elevator Pitch</h2>

                {!elevatorResult && !isLoading && (
                  <div className="flex flex-col items-center justify-center h-80 text-center">
                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-orange-100 to-rose-100 flex items-center justify-center mb-4">
                      <Clock size={32} className="text-orange-400" />
                    </div>
                    <p className="text-slate-500">
                      Configure duration and click generate<br />
                      to create your elevator pitch
                    </p>
                  </div>
                )}

                {isLoading && activeTab === 'elevator' && (
                  <div className="flex flex-col items-center justify-center h-80">
                    <div className="spinner-large mb-4"></div>
                    <p className="text-orange-600 font-medium">Crafting your pitch...</p>
                    <p className="text-slate-500 text-sm mt-1">This usually takes 15-30 seconds</p>
                  </div>
                )}

                {elevatorResult && (
                  <div className="space-y-4">
                    <div className="flex items-center gap-4 text-sm text-slate-500 mb-4">
                      <span className="flex items-center gap-1">
                        <Clock size={14} />
                        {elevatorResult.duration_seconds || duration}s
                      </span>
                      <span>~{elevatorResult.estimated_words || Math.round(duration * 2.5)} words</span>
                    </div>

                    <div className="bg-gradient-to-br from-orange-50 to-rose-50 rounded-xl p-6 border border-orange-100">
                      <p className="text-slate-700 leading-relaxed text-lg">
                        {elevatorResult.elevator_pitch || elevatorResult.response}
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
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default PitchDeckPage;
