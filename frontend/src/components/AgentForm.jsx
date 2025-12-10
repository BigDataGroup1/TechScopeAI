import { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

const AgentForm = ({ questionnaire, title, onClose, onSubmit, loading = false }) => {
  const [formData, setFormData] = useState({});
  const [currentStep, setCurrentStep] = useState(0);
  const [errors, setErrors] = useState({});

  // Initialize form data
  useEffect(() => {
    const initialData = {};
    questionnaire.forEach((q) => {
      if (q.type === 'multiselect') {
        initialData[q.id] = [];
      } else {
        initialData[q.id] = '';
      }
    });
    setFormData(initialData);
  }, [questionnaire]);

  // Filter questions based on dependencies and current step
  const getVisibleQuestions = () => {
    return questionnaire.filter((q) => {
      // Check dependencies
      if (q.depends_on) {
        const [key, value] = Object.entries(q.depends_on)[0];
        const formValue = formData[key];
        
        if (Array.isArray(value)) {
          if (!value.includes(formValue)) return false;
        } else {
          if (formValue !== value) return false;
        }
      }
      
      // Check conditional
      if (q.conditional) {
        const [key, values] = Object.entries(q.conditional)[0];
        const formValue = formData[key];
        if (!values.includes(formValue)) return false;
      }
      
      return true;
    });
  };

  const visibleQuestions = getVisibleQuestions();
  const questionsPerStep = 3;
  const totalSteps = Math.ceil(visibleQuestions.length / questionsPerStep);
  const startIdx = currentStep * questionsPerStep;
  const endIdx = startIdx + questionsPerStep;
  const currentQuestions = visibleQuestions.slice(startIdx, endIdx);

  const updateFormData = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validateStep = () => {
    const stepErrors = {};
    currentQuestions.forEach((q) => {
      if (q.required) {
        const value = formData[q.id];
        if (!value || (Array.isArray(value) && value.length === 0)) {
          stepErrors[q.id] = 'This field is required';
        }
      }
    });
    setErrors(stepErrors);
    return Object.keys(stepErrors).length === 0;
  };

  const handleNext = () => {
    if (!validateStep()) return;
    if (currentStep < totalSteps - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = () => {
    // Validate all required fields
    const allErrors = {};
    visibleQuestions.forEach((q) => {
      if (q.required) {
        const value = formData[q.id];
        if (!value || (Array.isArray(value) && value.length === 0)) {
          allErrors[q.id] = 'This field is required';
        }
      }
    });
    
    if (Object.keys(allErrors).length > 0) {
      setErrors(allErrors);
      // Go to first step with error
      const firstErrorIdx = visibleQuestions.findIndex(q => allErrors[q.id]);
      if (firstErrorIdx >= 0) {
        setCurrentStep(Math.floor(firstErrorIdx / questionsPerStep));
      }
      return;
    }
    
    onSubmit(formData);
  };

  const renderField = (question) => {
    const value = formData[question.id] || '';
    const error = errors[question.id];

    switch (question.type) {
      case 'text':
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => updateFormData(question.id, e.target.value)}
            placeholder={question.placeholder || ''}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none ${
              error ? 'border-red-300' : 'border-gray-300'
            }`}
          />
        );
      
      case 'textarea':
        return (
          <textarea
            value={value}
            onChange={(e) => updateFormData(question.id, e.target.value)}
            placeholder={question.placeholder || ''}
            rows={4}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none ${
              error ? 'border-red-300' : 'border-gray-300'
            }`}
          />
        );
      
      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => updateFormData(question.id, e.target.value)}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none ${
              error ? 'border-red-300' : 'border-gray-300'
            }`}
          >
            <option value="">Select an option...</option>
            {question.options.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        );
      
      case 'multiselect':
        const selectedValues = Array.isArray(value) ? value : [];
        return (
          <div className="space-y-2">
            {question.options.map((opt) => (
              <label key={opt} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedValues.includes(opt)}
                  onChange={(e) => {
                    const newValues = e.target.checked
                      ? [...selectedValues, opt]
                      : selectedValues.filter((v) => v !== opt);
                    updateFormData(question.id, newValues);
                  }}
                  className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <span className="text-sm text-gray-700">{opt}</span>
              </label>
            ))}
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-500 to-violet-600 text-white p-4 rounded-t-xl flex items-center justify-between">
          <h3 className="text-xl font-semibold">{title}</h3>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-4 pt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">
              Step {currentStep + 1} of {totalSteps}
            </span>
            <span className="text-sm text-gray-600">
              {Math.round(((currentStep + 1) / totalSteps) * 100)}% Complete
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-purple-500 to-violet-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        {/* Form Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-6">
            {currentQuestions.map((question) => (
              <div key={question.id}>
                <label className="block text-sm font-semibold text-gray-800 mb-2">
                  {question.question}
                  {question.required && <span className="text-red-500 ml-1">*</span>}
                </label>
                {renderField(question)}
                {errors[question.id] && (
                  <p className="mt-1 text-sm text-red-600">{errors[question.id]}</p>
                )}
                {question.help && (
                  <p className="mt-1 text-xs text-gray-500">{question.help}</p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Footer Buttons */}
        <div className="border-t border-gray-200 p-4 flex gap-3">
          <button
            onClick={handleBack}
            disabled={currentStep === 0}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Back
          </button>
          <div className="flex-1" />
          {currentStep < totalSteps - 1 ? (
            <button
              onClick={handleNext}
              className="px-6 py-2 bg-gradient-to-r from-purple-500 to-violet-600 text-white rounded-lg hover:from-purple-600 hover:to-violet-700 transition-all font-medium"
            >
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-6 py-2 bg-gradient-to-r from-purple-500 to-violet-600 text-white rounded-lg hover:from-purple-600 hover:to-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
            >
              {loading ? 'Submitting...' : 'Submit'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AgentForm;

