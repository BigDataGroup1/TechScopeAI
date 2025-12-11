import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import { policyApi } from '../services/api';
import { ArrowLeft, Shield, FileText, Copy, Check, Download } from 'lucide-react';
import ContentRenderer from '../components/ContentRenderer';

const policyTypes = [
  { id: 'privacy', title: 'Privacy Policy', description: 'GDPR/CCPA compliant privacy policy' },
  { id: 'terms', title: 'Terms of Service', description: 'User agreement and terms' },
  { id: 'cookies', title: 'Cookie Policy', description: 'Cookie usage disclosure' },
  { id: 'refund', title: 'Refund Policy', description: 'Return and refund terms' },
  { id: 'hr', title: 'Employee Handbook', description: 'HR policies and guidelines' },
];

const dataCollectionOptions = [
  'Email addresses',
  'Names',
  'Payment information',
  'Location data',
  'Usage analytics',
  'Cookies',
  'Social media data',
  'Health data',
  'Biometric data',
];

const jurisdictions = [
  'United States',
  'European Union (GDPR)',
  'California (CCPA)',
  'United Kingdom',
  'Canada',
  'Australia',
  'Global',
];

const PolicyPage: React.FC = () => {
  const navigate = useNavigate();
  const { company, addActivity } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const [formData, setFormData] = useState({
    policy_type: 'privacy',
    data_collection: [] as string[],
    jurisdiction: 'Global',
    additional_requirements: '',
    website_url: '',
    contact_email: '',
  });

  const handleGenerate = async () => {
    if (!company) return;
    
    setIsLoading(true);
    setError('');
    setResult(null);
    
    try {
      const response = await policyApi.generate({
        company_id: company.id,
        policy_type: formData.policy_type,
        additional_requirements: `
          Data collected: ${formData.data_collection.join(', ')}
          Jurisdiction: ${formData.jurisdiction}
          Website: ${formData.website_url}
          Contact: ${formData.contact_email}
          ${formData.additional_requirements}
        `,
      });
      setResult(response);
      addActivity({
        id: Date.now().toString(),
        title: `${policyTypes.find(p => p.id === formData.policy_type)?.title} Generated`,
        description: 'Document ready for review',
        timestamp: new Date().toISOString(),
        type: 'policy',
        content: response.response || response.content,
        toolUsed: 'Policy Generator Agent',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate policy');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (result?.response) {
      navigator.clipboard.writeText(result.response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const downloadAsText = () => {
    if (result?.response) {
      const blob = new Blob([result.response], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${formData.policy_type}_policy_${company?.company_name || 'company'}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const toggleDataCollection = (item: string) => {
    setFormData(prev => ({
      ...prev,
      data_collection: prev.data_collection.includes(item)
        ? prev.data_collection.filter(d => d !== item)
        : [...prev.data_collection, item]
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-violet-50">
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
              <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
                Policy & Compliance Generator
              </h1>
              <p className="text-slate-500 text-sm">Generate legal documents for your business</p>
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
                <div className="w-12 h-12 rounded-xl gradient-blue flex items-center justify-center">
                  <Shield size={24} className="text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-slate-800">Policy Configuration</h2>
                  <p className="text-slate-500 text-sm">Choose policy type and customize</p>
                </div>
              </div>

              <div className="space-y-6">
                {/* Policy Type Selection */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-3">
                    Policy Type
                  </label>
                  <div className="grid grid-cols-1 gap-3">
                    {policyTypes.map(policy => (
                      <button
                        key={policy.id}
                        onClick={() => setFormData({ ...formData, policy_type: policy.id })}
                        className={`p-4 rounded-xl border-2 text-left transition-all ${
                          formData.policy_type === policy.id
                            ? 'border-indigo-500 bg-indigo-50'
                            : 'border-slate-200 hover:border-indigo-300'
                        }`}
                      >
                        <div className="font-medium text-slate-800">{policy.title}</div>
                        <div className="text-sm text-slate-500">{policy.description}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Data Collection (for privacy/cookies) */}
                {(formData.policy_type === 'privacy' || formData.policy_type === 'cookies') && (
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-3">
                      Data You Collect (select all that apply)
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {dataCollectionOptions.map(item => (
                        <button
                          key={item}
                          onClick={() => toggleDataCollection(item)}
                          className={`chip ${formData.data_collection.includes(item) ? 'selected' : ''}`}
                        >
                          {item}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Jurisdiction */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Jurisdiction
                  </label>
                  <select
                    value={formData.jurisdiction}
                    onChange={(e) => setFormData({ ...formData, jurisdiction: e.target.value })}
                    className="canva-select w-full"
                  >
                    {jurisdictions.map(j => (
                      <option key={j} value={j}>{j}</option>
                    ))}
                  </select>
                </div>

                {/* Website URL */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Website URL
                  </label>
                  <input
                    type="text"
                    value={formData.website_url}
                    onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
                    placeholder="https://yourcompany.com"
                    className="canva-input w-full"
                  />
                </div>

                {/* Contact Email */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Contact Email
                  </label>
                  <input
                    type="email"
                    value={formData.contact_email}
                    onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                    placeholder="legal@yourcompany.com"
                    className="canva-input w-full"
                  />
                </div>

                {/* Additional Requirements */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Additional Requirements
                  </label>
                  <textarea
                    value={formData.additional_requirements}
                    onChange={(e) => setFormData({ ...formData, additional_requirements: e.target.value })}
                    placeholder="Any specific clauses or requirements..."
                    className="canva-textarea w-full"
                    rows={3}
                  />
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerate}
                  disabled={isLoading}
                  className="w-full canva-btn flex items-center justify-center gap-2 py-4"
                  style={{ background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' }}
                >
                  {isLoading ? (
                    <>
                      <div className="spinner"></div>
                      <span>Generating document...</span>
                    </>
                  ) : (
                    <>
                      <FileText size={20} />
                      <span>Generate {policyTypes.find(p => p.id === formData.policy_type)?.title}</span>
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
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-slate-800">Generated Document</h2>
              {result && (
                <div className="flex gap-2">
                  <button
                    onClick={copyToClipboard}
                    className="flex items-center gap-2 px-3 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors text-sm"
                  >
                    {copied ? <Check size={14} /> : <Copy size={14} />}
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                  <button
                    onClick={downloadAsText}
                    className="flex items-center gap-2 px-3 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors text-sm"
                  >
                    <Download size={14} />
                    Download
                  </button>
                </div>
              )}
            </div>

            {!result && !isLoading && (
              <div className="flex flex-col items-center justify-center h-96 text-center">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-100 to-violet-100 flex items-center justify-center mb-4">
                  <Shield size={32} className="text-indigo-400" />
                </div>
                <p className="text-slate-500">
                  Select a policy type and configure<br />
                  to generate your document
                </p>
              </div>
            )}

            {isLoading && (
              <div className="flex flex-col items-center justify-center h-96">
                <div className="spinner-large mb-4"></div>
                <p className="text-indigo-600 font-medium">Generating your policy...</p>
                <p className="text-slate-500 text-sm mt-1">This usually takes 30-60 seconds</p>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                <div className="bg-gradient-to-br from-indigo-50 to-violet-50 rounded-xl p-6 border border-indigo-100 max-h-[600px] overflow-y-auto">
                  <ContentRenderer content={result.response || result.content} accentColor="indigo" />
                </div>

                <div className="bg-amber-50 rounded-xl p-4 border border-amber-200">
                  <h4 className="font-medium text-amber-800 mb-2">Important Notice</h4>
                  <p className="text-sm text-amber-700">
                    This document is AI-generated and should be reviewed by a legal professional 
                    before use. Laws vary by jurisdiction.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default PolicyPage;

