import axios from 'axios';

// Use environment variable in production, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add session ID to requests
api.interceptors.request.use((config) => {
  const sessionId = localStorage.getItem('sessionId');
  if (sessionId) {
    config.headers['X-Session-ID'] = sessionId;
  }
  return config;
});

// Types
export interface Company {
  id: string;
  company_name: string;
  industry: string;
  problem: string;
  solution: string;
  target_market?: string;
  current_stage: string;
  traction?: string;
  funding_goal?: string;
  created_at: string;
}

export interface Activity {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  type: string;
  content?: string; // The actual generated content
  toolUsed?: string; // Which agent/tool was used
}

export interface SessionResponse {
  session_id: string;
  company: Company;
  message: string;
}

// Auth API
export const authApi = {
  register: async (data: {
    company_name: string;
    industry: string;
    problem: string;
    solution: string;
    target_market?: string;
    current_stage?: string;
    traction?: string;
    funding_goal?: string;
  }): Promise<SessionResponse> => {
    // Clean up data: convert empty strings to undefined for optional fields
    const cleanedData: any = {
      company_name: data.company_name.trim(),
      industry: data.industry.trim(),
      problem: data.problem.trim(),
      solution: data.solution.trim(),
    };
    
    // Only include optional fields if they have values
    if (data.target_market?.trim()) {
      cleanedData.target_market = data.target_market.trim();
    }
    if (data.current_stage) {
      cleanedData.current_stage = data.current_stage;
    }
    if (data.traction?.trim()) {
      cleanedData.traction = data.traction.trim();
    }
    if (data.funding_goal?.trim()) {
      cleanedData.funding_goal = data.funding_goal.trim();
    }
    
    const response = await api.post('/auth/register', cleanedData);
    return response.data;
  },

  getSession: async (): Promise<SessionResponse> => {
    const response = await api.get('/auth/session');
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem('sessionId');
  },

  getActivities: async (limit = 20): Promise<{ activities: Activity[]; total: number }> => {
    const response = await api.get(`/auth/activities?limit=${limit}`);
    return response.data;
  },
};

// Pitch API
export const pitchApi = {
  generateDeck: async (data: {
    company_id: string;
    enhance_with_ai?: boolean;
    ai_provider?: string;
    gamma_only?: boolean;
  }) => {
    const response = await api.post('/pitch/deck', data);
    return response.data;
  },

  generateElevatorPitch: async (data: {
    company_id: string;
    duration_seconds?: number;
  }) => {
    const response = await api.post('/pitch/elevator', data);
    return response.data;
  },
};

// Marketing API
export const marketingApi = {
  generateContent: async (data: {
    company_id: string;
    platform: string;
    content_type: string;
    description: string;
    generate_image?: boolean;
    image_provider?: string;
  }) => {
    const response = await api.post('/marketing/content', data);
    return response.data;
  },

  getStrategies: async () => {
    const response = await api.post('/marketing/strategies');
    return response.data;
  },
};

// Patent API
export const patentApi = {
  assess: async (data: {
    company_id: string;
    invention_description: string;
    novelty?: string;
  }) => {
    const response = await api.post('/patent/assess', data);
    return response.data;
  },

  filingStrategy: async (data: {
    company_id: string;
    geographic_interest?: string[];
    budget_range?: string;
  }) => {
    const response = await api.post('/patent/filing-strategy', data);
    return response.data;
  },
};

// Policy API
export const policyApi = {
  generate: async (data: {
    company_id: string;
    policy_type: string;
    additional_requirements?: string;
  }) => {
    const response = await api.post('/policy/generate', data);
    return response.data;
  },
};

// Team API
export const teamApi = {
  analyze: async (data: {
    company_id: string;
    current_team?: string;
    challenges?: string;
  }) => {
    const response = await api.post('/team/analyze', data);
    return response.data;
  },

  generateJobDescription: async (data: {
    company_id: string;
    role_title: string;
    role_type?: string;
    experience_level?: string;
    responsibilities?: string;
    required_skills?: string;
  }) => {
    const response = await api.post('/team/job-description', data);
    return response.data;
  },
};

// Competitive API
export const competitiveApi = {
  analyze: async (data: {
    company_id: string;
    specific_competitors?: string[];
  }) => {
    const response = await api.post('/competitive/analyze', data);
    return response.data;
  },

  getMarketOverview: async () => {
    const response = await api.get('/competitive/market-overview');
    return response.data;
  },
};

// Chat API
export const chatApi = {
  sendMessage: async (data: {
    company_id: string;
    message: string;
  }) => {
    const response = await api.post('/chat/message', data);
    return response.data;
  },
};

export default api;

