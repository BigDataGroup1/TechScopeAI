import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Company/Signup API
export const companyAPI = {
  // Save company data
  saveCompany: async (companyId, companyData) => {
    const response = await api.post(`/api/companies/${companyId}`, companyData);
    return response.data;
  },

  // Get company data
  getCompany: async (companyId) => {
    const response = await api.get(`/api/companies/${companyId}`);
    return response.data;
  },

  // Update company data
  updateCompany: async (companyId, companyData) => {
    const response = await api.put(`/api/companies/${companyId}`, companyData);
    return response.data;
  },
};

// Pitch Agent API
export const pitchAPI = {
  // Generate pitch from company details
  generatePitch: async (companyData) => {
    const response = await api.post('/api/pitch/generate', { company_data: companyData });
    return response.data;
  },

  // Generate slides (both PowerPoint and Gamma)
  generateSlides: async (companyData) => {
    const response = await api.post('/api/pitch/slides', { company_data: companyData });
    return response.data;
  },

  // Generate Gamma presentation only
  generateGammaPresentation: async (companyData) => {
    const response = await api.post('/api/pitch/gamma', { company_data: companyData });
    return response.data;
  },

  // Generate elevator pitch
  generateElevatorPitch: async (companyData, durationSeconds = 60) => {
    const response = await api.post('/api/pitch/elevator', {
      company_data: companyData,
      duration_seconds: durationSeconds,
    });
    return response.data;
  },

  // Evaluate pitch
  evaluatePitch: async (pitchText, companyData = null) => {
    const response = await api.post('/api/pitch/evaluate', {
      pitch_text: pitchText,
      company_context: companyData,
    });
    return response.data;
  },

  // Query pitch agent
  queryPitch: async (query, companyData = null) => {
    const response = await api.post('/api/pitch/query', {
      query,
      context: companyData,
    });
    return response.data;
  },

  // Download PowerPoint file
  downloadPPT: async (filename) => {
    const response = await api.get(`/api/pitch/download/${filename}`, {
      responseType: 'blob', // Important for file downloads
    });
    return response;
  },
};

// Competitive Agent API
export const competitiveAPI = {
  analyzeCompetitors: async (companyData) => {
    const response = await api.post('/api/competitive/analyze', { company_data: companyData });
    return response.data;
  },
};

// Marketing Agent API
export const marketingAPI = {
  generateInstagramContent: async (companyData) => {
    const response = await api.post('/api/marketing/instagram', { company_data: companyData });
    return response.data;
  },

  generateLinkedInContent: async (companyData) => {
    const response = await api.post('/api/marketing/linkedin', { company_data: companyData });
    return response.data;
  },

  suggestMarketingStrategies: async (companyData) => {
    const response = await api.post('/api/marketing/strategies', { company_data: companyData });
    return response.data;
  },

  queryMarketing: async (query, companyData = null) => {
    const response = await api.post('/api/marketing/query', {
      query,
      context: companyData,
    });
    return response.data;
  },

  generateFromPrompt: async (prompt, companyData = null) => {
    const response = await api.post('/api/marketing/generate-from-prompt', {
      query: prompt,
      context: companyData,
    });
    return response.data;
  },
};

// Policy Agent API
export const policyAPI = {
  generatePrivacyPolicy: async (companyData) => {
    const response = await api.post('/api/policy/privacy', { company_data: companyData });
    return response.data;
  },

  generateTermsOfService: async (companyData) => {
    const response = await api.post('/api/policy/terms', { company_data: companyData });
    return response.data;
  },

  checkCompliance: async (companyData) => {
    const response = await api.post('/api/policy/compliance', { company_data: companyData });
    return response.data;
  },

  generateHRPolicies: async (companyData) => {
    const response = await api.post('/api/policy/hr', { company_data: companyData });
    return response.data;
  },

  queryPolicy: async (query, companyData = null) => {
    const response = await api.post('/api/policy/query', {
      query,
      context: companyData,
    });
    return response.data;
  },
};

// Patent Agent API
export const patentAPI = {
  searchPatents: async (query, companyData = null) => {
    const response = await api.post('/api/patent/search', {
      query,
      context: companyData,
    });
    return response.data;
  },

  assessPatentability: async (companyData) => {
    const response = await api.post('/api/patent/assess', { company_data: companyData });
    return response.data;
  },

  filingStrategy: async (companyData) => {
    const response = await api.post('/api/patent/strategy', { company_data: companyData });
    return response.data;
  },

  priorArtSearch: async (query, companyData = null) => {
    const response = await api.post('/api/patent/prior-art', {
      query,
      context: companyData,
    });
    return response.data;
  },

  queryPatent: async (query, companyData = null) => {
    const response = await api.post('/api/patent/query', {
      query,
      context: companyData,
    });
    return response.data;
  },
};

// Team Agent API
export const teamAPI = {
  analyzeTeamNeeds: async (companyData) => {
    const response = await api.post('/api/team/analyze', { company_data: companyData });
    return response.data;
  },

  generateJobDescription: async (payload) => {
    const response = await api.post('/api/team/job-description', { company_data: payload });
    return response.data;
  },

  getRoleMarketData: async (companyData) => {
    const response = await api.post('/api/team/market-data', { company_data: companyData });
    return response.data;
  },

  queryTeam: async (query, companyData = null) => {
    const response = await api.post('/api/team/query', {
      query,
      context: companyData,
    });
    return response.data;
  },
};

// General Chat API
export const chatAPI = {
  sendMessage: async (query, companyId = null, companyData = null) => {
    const response = await api.post('/api/chat', {
      query,
      company_id: companyId,
      context: companyData,
    });
    return response.data;
  },
};

// Questionnaire API
export const questionnaireAPI = {
  getPatentQuestionnaire: async () => {
    const response = await api.get('/api/questionnaire/patent');
    return response.data.questionnaire;
  },
  
  getMarketingQuestionnaire: async () => {
    const response = await api.get('/api/questionnaire/marketing');
    return response.data.questionnaire;
  },
  
  getPolicyQuestionnaire: async () => {
    const response = await api.get('/api/questionnaire/policy');
    return response.data.questionnaire;
  },
  
  getTeamQuestionnaire: async () => {
    const response = await api.get('/api/questionnaire/team');
    return response.data.questionnaire;
  },
  
  getJobDescriptionQuestionnaire: async () => {
    const response = await api.get('/api/questionnaire/job-description');
    return response.data.questionnaire;
  },
};

export default api;




