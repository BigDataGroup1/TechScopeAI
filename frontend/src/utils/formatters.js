/**
 * Format company data for API submission
 */
export const formatCompanyData = (formData) => {
  const now = new Date().toISOString();
  const companyId = `company_${Date.now()}`;

  return {
    company_id: companyId,
    created_at: now,
    updated_at: now,
    basic_info: {
      company_name: formData.companyName || '',
      legal_name: formData.legalName || formData.companyName || '',
      website: formData.website || '',
      founded_date: formData.foundedDate || new Date().toISOString().split('T')[0],
      headquarters_location: formData.location || '',
      company_stage: formData.companyStage || 'Pre-Seed',
      industry: formData.industry || '',
      company_description: formData.startupDescription || '',
    },
    problem: {
      problem_statement: formData.problemStatement || '',
      pain_points: formData.painPoints ? formData.painPoints.split(',').map(p => p.trim()) : [],
    },
    solution: {
      solution_description: formData.solution || '',
      key_features: formData.keyFeatures ? formData.keyFeatures.split(',').map(f => f.trim()) : [],
      unique_value_proposition: formData.uniqueValue || '',
    },
    market: {
      target_audience: formData.targetAudience || '',
      vision: formData.vision || '',
      competitive_advantage: formData.competitiveAdvantage || '',
    },
    team: {
      team_size: parseInt(formData.teamSize) || 1,
      founders: formData.founders || [],
    },
    funding: {
      current_stage: formData.companyStage || 'Pre-Seed',
      valuation: formData.valuation || '',
    },
    preferences: {
      data_sharing_consent: formData.dataConsent || false,
      terms_accepted: formData.termsAccepted || false,
      privacy_policy_accepted: formData.privacyAccepted || false,
    },
  };
};

/**
 * Validate form data
 * Updated for 3-step form structure:
 * Step 1: Basic Info + Problem
 * Step 2: Solution + Vision + Target Audience + Competitive Advantage
 * Step 3: Terms & Preferences
 */
export const validateFormData = (formData, step) => {
  const errors = {};

  if (step === 1) {
    // Basic Information
    if (!formData.companyName?.trim()) errors.companyName = 'Company name is required';
    if (!formData.location?.trim()) errors.location = 'Location is required';
    if (!formData.startupDescription?.trim()) errors.startupDescription = 'Startup description is required';
    if (!formData.valuation?.trim()) errors.valuation = 'Valuation is required';
    if (!formData.teamSize || parseInt(formData.teamSize) < 1) errors.teamSize = 'Team size must be at least 1';
    // Problem
    if (!formData.problemStatement?.trim()) errors.problemStatement = 'Problem statement is required';
  }

  if (step === 2) {
    // Solution
    if (!formData.solution?.trim()) errors.solution = 'Solution description is required';
    if (!formData.uniqueValue?.trim()) errors.uniqueValue = 'Unique value proposition is required';
    // Vision & Market
    if (!formData.vision?.trim()) errors.vision = 'Vision is required';
    if (!formData.targetAudience?.trim()) errors.targetAudience = 'Target audience is required';
    // Competitive advantage is optional
  }

  if (step === 3) {
    // Terms & Preferences - checkboxes are validated in the submit handler
    // No field-level validation needed here
  }

  return errors;
};




