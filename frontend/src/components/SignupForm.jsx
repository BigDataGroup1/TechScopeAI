import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import { formatCompanyData, validateFormData } from '../utils/formatters';
import { companyAPI } from '../services/api';

const SignupForm = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Step 1: Basic Info
    companyName: '',
    location: '',
    startupDescription: '',
    valuation: '',
    teamSize: '1',
    companyStage: 'Pre-Seed',
    industry: '',
    website: '',
    foundedDate: '',
    
    // Step 2: Problem & Vision
    targetAudience: '',
    vision: '',
    problemStatement: '',
    painPoints: '',
    
    // Step 3: Solution
    solution: '',
    uniqueValue: '',
    keyFeatures: '',
    
    // Step 4: Market
    targetMarket: '',
    competitiveAdvantage: '',
    
    // Step 5: Preferences
    dataConsent: false,
    termsAccepted: false,
    privacyAccepted: false,
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  const totalSteps = 3;

  const updateFormData = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleNext = () => {
    const stepErrors = validateFormData(formData, currentStep);
    if (Object.keys(stepErrors).length > 0) {
      setErrors(stepErrors);
      return;
    }
    setErrors({});
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    const stepErrors = validateFormData(formData, currentStep);
    if (Object.keys(stepErrors).length > 0) {
      setErrors(stepErrors);
      return;
    }

    setIsSubmitting(true);
    setSubmitStatus(null);

    try {
      const companyData = formatCompanyData(formData);
      const companyId = companyData.company_id;

      // Save to FastAPI backend (primary)
      try {
        await companyAPI.saveCompany(companyId, companyData);
        console.log('Company data saved to backend successfully');
      } catch (apiError) {
        console.warn('Backend save failed, using localStorage backup:', apiError);
        // Fallback to localStorage if backend is not available (no file download)
        localStorage.setItem(`techscope_company_${companyId}`, JSON.stringify(companyData));
      }

      // Always save to localStorage as backup (no file download for better UX)
      localStorage.setItem(`techscope_company_${companyId}`, JSON.stringify(companyData));
      console.log('Company data saved to localStorage as backup');
      
      // Success - proceed to dashboard
      setSubmitStatus('success');
      setTimeout(() => {
        onComplete(companyId, companyData);
      }, 1500);
    } catch (error) {
      console.error('Error saving company data:', error);
      setSubmitStatus('error');
      setIsSubmitting(false);
    }
  };

  const stepVariants = {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
  };

  return (
    <div className="min-h-screen relative overflow-hidden py-12 px-4 sm:px-6 lg:px-8">
      {/* Vibrant animated background overlay */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Animated gradient orbs */}
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-blob animation-delay-4000"></div>
        <div className="absolute top-1/4 right-1/4 w-72 h-72 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-6000"></div>
        
        {/* Geometric pattern overlay */}
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, rgba(255,255,255,0.3) 1px, transparent 0)`,
          backgroundSize: '40px 40px'
        }}></div>
      </div>
      <div className="max-w-4xl mx-auto relative z-10">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Welcome to <span className="text-primary-600">TechScope AI</span>
          </h1>
          <p className="text-lg text-gray-600">
            Tell us about your technical startup
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Step {currentStep} of {totalSteps}
            </span>
            <span className="text-sm text-gray-500">
              {Math.round((currentStep / totalSteps) * 100)}% Complete
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <motion.div
              className="bg-primary-600 h-2.5 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${(currentStep / totalSteps) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        {/* Form Card */}
        <div className="card">
          <AnimatePresence mode="wait">
            {/* Step 1: Basic Information + Problem & Vision (Combined) */}
            {currentStep === 1 && (
              <motion.div
                key="step1"
                variants={stepVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="space-y-6"
              >
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    Company Overview
                  </h2>
                  <p className="text-sm text-gray-600">Tell us about your startup and the problem you're solving</p>
                </div>

                {/* Basic Information Section */}
                <div className="bg-blue-50 p-4 rounded-lg mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Company Name <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        className={`input-field ${errors.companyName ? 'border-red-500' : ''}`}
                        value={formData.companyName}
                        onChange={(e) => updateFormData('companyName', e.target.value)}
                        placeholder="Enter your company name"
                      />
                      {errors.companyName && (
                        <p className="mt-1 text-sm text-red-600">{errors.companyName}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Location <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        className={`input-field ${errors.location ? 'border-red-500' : ''}`}
                        value={formData.location}
                        onChange={(e) => updateFormData('location', e.target.value)}
                        placeholder="City, State, Country"
                      />
                      {errors.location && (
                        <p className="mt-1 text-sm text-red-600">{errors.location}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Industry
                      </label>
                      <input
                        type="text"
                        className="input-field"
                        value={formData.industry}
                        onChange={(e) => updateFormData('industry', e.target.value)}
                        placeholder="e.g., SaaS, AI/ML, DevTools"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Company Stage <span className="text-red-500">*</span>
                      </label>
                      <select
                        className="input-field"
                        value={formData.companyStage}
                        onChange={(e) => updateFormData('companyStage', e.target.value)}
                      >
                        <option value="Pre-Seed">Pre-Seed</option>
                        <option value="Seed">Seed</option>
                        <option value="Series A">Series A</option>
                        <option value="Series B">Series B</option>
                        <option value="Series C+">Series C+</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Valuation <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        className={`input-field ${errors.valuation ? 'border-red-500' : ''}`}
                        value={formData.valuation}
                        onChange={(e) => updateFormData('valuation', e.target.value)}
                        placeholder="e.g., $2.5M, $10M"
                      />
                      {errors.valuation && (
                        <p className="mt-1 text-sm text-red-600">{errors.valuation}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Team Size <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="number"
                        min="1"
                        className={`input-field ${errors.teamSize ? 'border-red-500' : ''}`}
                        value={formData.teamSize}
                        onChange={(e) => updateFormData('teamSize', e.target.value)}
                        placeholder="Number of team members"
                      />
                      {errors.teamSize && (
                        <p className="mt-1 text-sm text-red-600">{errors.teamSize}</p>
                      )}
                    </div>
                  </div>

                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tell us about your startup (2-3 lines) <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      rows="3"
                      className={`input-field ${errors.startupDescription ? 'border-red-500' : ''}`}
                      value={formData.startupDescription}
                      onChange={(e) => updateFormData('startupDescription', e.target.value)}
                      placeholder="Brief description of what your startup does..."
                    />
                    {errors.startupDescription && (
                      <p className="mt-1 text-sm text-red-600">{errors.startupDescription}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Website (optional)
                      </label>
                      <input
                        type="url"
                        className="input-field"
                        value={formData.website}
                        onChange={(e) => updateFormData('website', e.target.value)}
                        placeholder="https://yourcompany.com"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Founded Date (optional)
                      </label>
                      <input
                        type="date"
                        className="input-field"
                        value={formData.foundedDate}
                        onChange={(e) => updateFormData('foundedDate', e.target.value)}
                      />
                    </div>
                  </div>
                </div>

                {/* Problem Section */}
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">The Problem</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Problem You Are Solving <span className="text-red-500">*</span>
                      </label>
                      <textarea
                        rows="4"
                        className={`input-field ${errors.problemStatement ? 'border-red-500' : ''}`}
                        value={formData.problemStatement}
                        onChange={(e) => updateFormData('problemStatement', e.target.value)}
                        placeholder="Describe the problem your startup solves..."
                      />
                      {errors.problemStatement && (
                        <p className="mt-1 text-sm text-red-600">{errors.problemStatement}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Pain Points (comma-separated)
                      </label>
                      <input
                        type="text"
                        className="input-field"
                        value={formData.painPoints}
                        onChange={(e) => updateFormData('painPoints', e.target.value)}
                        placeholder="e.g., High costs, Time-consuming, Poor user experience"
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Step 2: Solution + Vision + Market */}
            {currentStep === 2 && (
              <motion.div
                key="step2"
                variants={stepVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="space-y-6"
              >
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    Solution & Vision
                  </h2>
                  <p className="text-sm text-gray-600">Describe your solution, vision, and market position</p>
                </div>

                {/* Solution Section */}
                <div className="bg-green-50 p-4 rounded-lg mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Solution</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Solution Description <span className="text-red-500">*</span>
                      </label>
                      <textarea
                        rows="4"
                        className={`input-field ${errors.solution ? 'border-red-500' : ''}`}
                        value={formData.solution}
                        onChange={(e) => updateFormData('solution', e.target.value)}
                        placeholder="How does your product/service solve the problem?"
                      />
                      {errors.solution && (
                        <p className="mt-1 text-sm text-red-600">{errors.solution}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Unique Value Proposition <span className="text-red-500">*</span>
                      </label>
                      <textarea
                        rows="3"
                        className={`input-field ${errors.uniqueValue ? 'border-red-500' : ''}`}
                        value={formData.uniqueValue}
                        onChange={(e) => updateFormData('uniqueValue', e.target.value)}
                        placeholder="What makes your solution unique?"
                      />
                      {errors.uniqueValue && (
                        <p className="mt-1 text-sm text-red-600">{errors.uniqueValue}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Key Features (comma-separated)
                      </label>
                      <input
                        type="text"
                        className="input-field"
                        value={formData.keyFeatures}
                        onChange={(e) => updateFormData('keyFeatures', e.target.value)}
                        placeholder="e.g., Real-time analytics, AI-powered insights, Cloud-native"
                      />
                    </div>
                  </div>
                </div>

                {/* Vision & Market Section */}
                <div className="bg-orange-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Vision & Market Position</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Vision <span className="text-red-500">*</span>
                      </label>
                      <textarea
                        rows="3"
                        className={`input-field ${errors.vision ? 'border-red-500' : ''}`}
                        value={formData.vision}
                        onChange={(e) => updateFormData('vision', e.target.value)}
                        placeholder="What is your long-term vision for the company?"
                      />
                      {errors.vision && (
                        <p className="mt-1 text-sm text-red-600">{errors.vision}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Target Audience <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        className={`input-field ${errors.targetAudience ? 'border-red-500' : ''}`}
                        value={formData.targetAudience}
                        onChange={(e) => updateFormData('targetAudience', e.target.value)}
                        placeholder="Who is your target customer? (e.g., Remote software teams, 10-50 employees)"
                      />
                      {errors.targetAudience && (
                        <p className="mt-1 text-sm text-red-600">{errors.targetAudience}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Competitive Advantage
                      </label>
                      <textarea
                        rows="3"
                        className="input-field"
                        value={formData.competitiveAdvantage}
                        onChange={(e) => updateFormData('competitiveAdvantage', e.target.value)}
                        placeholder="What gives you a competitive edge over competitors?"
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Step 3: Terms & Preferences */}
            {currentStep === 3 && (
              <motion.div
                key="step3"
                variants={stepVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="space-y-6"
              >
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    Terms & Preferences
                  </h2>
                  <p className="text-sm text-gray-600">Please review and accept our terms to continue</p>
                </div>

                <div className="space-y-4">
                  <label className="flex items-start">
                    <input
                      type="checkbox"
                      className="mt-1 mr-3 w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                      checked={formData.dataConsent}
                      onChange={(e) => updateFormData('dataConsent', e.target.checked)}
                    />
                    <span className="text-sm text-gray-700">
                      I consent to data sharing for improving the service <span className="text-red-500">*</span>
                    </span>
                  </label>

                  <label className="flex items-start">
                    <input
                      type="checkbox"
                      className="mt-1 mr-3 w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                      checked={formData.termsAccepted}
                      onChange={(e) => updateFormData('termsAccepted', e.target.checked)}
                    />
                    <span className="text-sm text-gray-700">
                      I accept the Terms of Service <span className="text-red-500">*</span>
                    </span>
                  </label>

                  <label className="flex items-start">
                    <input
                      type="checkbox"
                      className="mt-1 mr-3 w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                      checked={formData.privacyAccepted}
                      onChange={(e) => updateFormData('privacyAccepted', e.target.checked)}
                    />
                    <span className="text-sm text-gray-700">
                      I accept the Privacy Policy <span className="text-red-500">*</span>
                    </span>
                  </label>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Navigation Buttons */}
          <div className="mt-8 flex justify-between">
            <button
              type="button"
              onClick={handleBack}
              disabled={currentStep === 1}
              className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Back
            </button>

            {currentStep < totalSteps ? (
              <button
                type="button"
                onClick={handleNext}
                className="btn-primary"
              >
                Next
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isSubmitting || !formData.dataConsent || !formData.termsAccepted || !formData.privacyAccepted}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Submitting...' : 'Submit & Continue'}
              </button>
            )}
          </div>

          {/* Submit Status */}
          {submitStatus && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-4 rounded-lg flex items-center space-x-3"
              style={{
                backgroundColor: submitStatus === 'success' ? '#d1fae5' : '#fee2e2',
                color: submitStatus === 'success' ? '#065f46' : '#991b1b',
              }}
            >
              {submitStatus === 'success' ? (
                <>
                  <CheckCircleIcon className="w-6 h-6" />
                  <span>Company data saved successfully! Redirecting...</span>
                </>
              ) : (
                <>
                  <XCircleIcon className="w-6 h-6" />
                  <span>Error saving data. Please try again.</span>
                </>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SignupForm;




