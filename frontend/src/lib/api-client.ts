/**
 * API Client for GalaxyRend Backend
 * Handles all HTTP requests with authentication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class APIError extends Error {
  constructor(message: string, public status: number, public data?: any) {
    super(message);
    this.name = "APIError";
  }
}

interface RequestOptions extends RequestInit {
  requiresAuth?: boolean;
}

/**
 * Base fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { requiresAuth = false, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(fetchOptions.headers as Record<string, string>),
  };

  // Add auth token if required
  if (requiresAuth) {
    const token = getAccessToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
    });

    // Handle non-JSON responses
    const contentType = response.headers.get("content-type");
    const isJson = contentType?.includes("application/json");

    if (!response.ok) {
      const errorData = isJson ? await response.json() : await response.text();
      throw new APIError(
        errorData?.detail || `API Error: ${response.status}`,
        response.status,
        errorData
      );
    }

    // Handle empty responses
    if (response.status === 204) {
      return {} as T;
    }

    return isJson ? await response.json() : ({} as T);
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      `Network error: ${
        error instanceof Error ? error.message : "Unknown error"
      }`,
      0
    );
  }
}

// Token management
function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("refresh_token");
}

export function setTokens(accessToken: string, refreshToken: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem("access_token", accessToken);
  localStorage.setItem("refresh_token", refreshToken);
}

export function clearTokens() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user_address");
  localStorage.removeItem("user_role");
}

// ============================================================================
// Authentication API
// ============================================================================

export interface ChallengeRequest {
  address: string;
}

export interface ChallengeResponse {
  message: string;
  timestamp: string;
  nonce: string;
  expires_at: string;
}

export interface AuthRequest {
  address: string;
  message: string;
  signature: string[];
  timestamp: number;
}

export interface User {
  id: string;
  address: string;
  username?: string;
  email?: string;
  bio?: string;
  avatar_url?: string;
  timezone?: string;
  language?: string;
  notifications_enabled: boolean;
  email_notifications: boolean;
  public_key?: string;
  registered_at: string;
  email_verified: boolean;
  email_verified_at?: string;
  active: boolean;
  is_admin: boolean;
  is_verified: boolean;
  verified_at?: string;
  verified_by?: string;
  last_seen?: string;
  login_count: number;
}

export interface Worker {
  id: string;
  address: string;
  reputation: number;
  jobs_completed: number;
  jobs_failed: number;
  total_earnings: number;
  verified: boolean;
  active: boolean;
  is_admin: boolean;
  registered_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export const authAPI = {
  async getChallenge(address: string): Promise<ChallengeResponse> {
    return apiFetch<ChallengeResponse>("/api/v1/auth/challenge", {
      method: "POST",
      body: JSON.stringify({ address }),
    });
  },

  async authenticate(request: AuthRequest): Promise<AuthResponse> {
    return apiFetch<AuthResponse>("/api/v1/auth/authenticate", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  async refreshToken(
    refreshToken: string
  ): Promise<{ access_token: string; expires_in: number }> {
    return apiFetch("/api/v1/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  },

  async verifyToken(
    token: string
  ): Promise<{ valid: boolean; error?: string }> {
    return apiFetch("/api/v1/auth/verify-token", {
      method: "POST",
      body: JSON.stringify({ token }),
    });
  },

  async logout(refreshToken?: string): Promise<void> {
    return apiFetch("/api/v1/auth/logout", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
      requiresAuth: true,
    });
  },

  async getCurrentUser(): Promise<User> {
    return apiFetch<User>("/api/v1/auth/me/user", {
      requiresAuth: true,
    });
  },
};

// ============================================================================
// Workers API (Nodes)
// ============================================================================

export interface WorkerRegistration {
  address: string;
  public_key?: string;
  info_cid?: string;
  capabilities?: string; // JSON string
  hardware_specs?: string; // JSON string
  contact_info?: string;
}

export const workersAPI = {
  async getWorkers(params?: {
    skip?: number;
    limit?: number;
    verified_only?: boolean;
    active_only?: boolean;
    min_reputation?: number;
  }): Promise<Worker[]> {
    const query = new URLSearchParams(
      Object.entries(params || {}).map(([k, v]) => [k, String(v)])
    );
    return apiFetch<Worker[]>(`/api/v1/workers/?${query}`);
  },

  async getWorker(address: string): Promise<Worker> {
    return apiFetch<Worker>(`/api/v1/workers/${address}`);
  },

  async registerWorker(data: WorkerRegistration): Promise<Worker> {
    return apiFetch<Worker>("/api/v1/workers/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async updateWorker(
    address: string,
    data: Partial<WorkerRegistration>
  ): Promise<Worker> {
    return apiFetch<Worker>(`/api/v1/workers/${address}`, {
      method: "PUT",
      body: JSON.stringify(data),
      requiresAuth: true,
    });
  },

  async getReputationHistory(address: string, skip = 0, limit = 50) {
    return apiFetch(
      `/api/v1/workers/${address}/reputation-history?skip=${skip}&limit=${limit}`
    );
  },

  async getWorkerJobs(address: string, status?: string, skip = 0, limit = 50) {
    const query = new URLSearchParams({
      skip: String(skip),
      limit: String(limit),
    });
    if (status) query.set("status", status);
    return apiFetch(`/api/v1/workers/${address}/jobs?${query}`);
  },

  async getWorkerStats() {
    return apiFetch("/api/v1/workers/stats/overview");
  },
};

// ============================================================================
// Jobs API
// ============================================================================

export interface Job {
  id: string;
  chain_job_id: number;
  creator_address: string;
  asset_cid_part1: string;
  asset_cid_part2?: string;
  full_asset_cid?: string;
  reward_amount: number;
  deadline: string;
  min_reputation: number;
  required_capabilities?: string;
  status: string;
  worker_id?: string;
  assigned_at?: string;
  completed_at?: string;
  result_cid_part1?: string;
  result_cid_part2?: string;
  full_result_cid?: string;
  quality_score?: number;
  created_at: string;
}

export interface JobCreate {
  chain_job_id: number;
  creator_address: string;
  asset_cid_part1: string;
  asset_cid_part2?: string;
  reward_amount: number;
  deadline: string;
  min_reputation?: number;
  required_capabilities?: string;
}

export const jobsAPI = {
  async getJobs(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    creator_address?: string;
    worker_address?: string;
    min_reward?: number;
    min_reputation_required?: number;
  }): Promise<Job[]> {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) query.set(k, String(v));
      });
    }
    return apiFetch<Job[]>(`/api/v1/jobs/?${query}`);
  },

  async getJob(jobId: string): Promise<Job> {
    return apiFetch<Job>(`/api/v1/jobs/${jobId}`);
  },

  async createJob(data: JobCreate): Promise<Job> {
    return apiFetch<Job>("/api/v1/jobs/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getAvailableJobs(
    workerAddress?: string,
    skip = 0,
    limit = 50
  ): Promise<Job[]> {
    const query = new URLSearchParams({
      skip: String(skip),
      limit: String(limit),
    });
    if (workerAddress) query.set("worker_address", workerAddress);
    return apiFetch<Job[]>(`/api/v1/jobs/available?${query}`);
  },

  async assignJob(jobId: string, workerAddress: string): Promise<Job> {
    return apiFetch<Job>(`/api/v1/jobs/${jobId}/assign`, {
      method: "POST",
      body: JSON.stringify({ worker_address: workerAddress }),
    });
  },

  async completeJob(
    jobId: string,
    data: {
      result_cid_part1: string;
      result_cid_part2?: string;
      quality_score: number;
      worker_address?: string;
    }
  ): Promise<Job> {
    return apiFetch<Job>(`/api/v1/jobs/${jobId}/complete`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getJobEvents(jobId: string, skip = 0, limit = 50) {
    return apiFetch(`/api/v1/jobs/${jobId}/events?skip=${skip}&limit=${limit}`);
  },

  async getJobStats() {
    return apiFetch("/api/v1/jobs/stats/overview");
  },
};

// ============================================================================
// Events API (Admin)
// ============================================================================

export const eventsAPI = {
  async getEvents(params?: {
    skip?: number;
    limit?: number;
    event_name?: string;
    contract_address?: string;
    processed?: boolean;
    from_block?: number;
    to_block?: number;
  }) {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) query.set(k, String(v));
      });
    }
    return apiFetch(`/api/v1/events/?${query}`);
  },

  async getUnprocessedEvents(skip = 0, limit = 50, eventName?: string) {
    const query = new URLSearchParams({
      skip: String(skip),
      limit: String(limit),
    });
    if (eventName) query.set("event_name", eventName);
    return apiFetch(`/api/v1/events/unprocessed?${query}`);
  },

  async getEventSummary(hours = 24) {
    return apiFetch(`/api/v1/events/summary/stats?hours=${hours}`);
  },

  async markEventProcessed(eventId: string) {
    return apiFetch(`/api/v1/events/${eventId}/mark-processed`, {
      method: "POST",
    });
  },
};

// ============================================================================
// Hybrid API (The Graph + Database)
// ============================================================================

export const hybridAPI = {
  async getGlobalStats() {
    return apiFetch("/api/v1/hybrid/stats/global");
  },

  async getDailyStats(days = 7) {
    return apiFetch(`/api/v1/hybrid/stats/daily?days=${days}`);
  },

  async getWorkers(params?: {
    skip?: number;
    limit?: number;
    verified_only?: boolean;
    min_reputation?: number;
  }) {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) query.set(k, String(v));
      });
    }
    return apiFetch(`/api/v1/hybrid/workers?${query}`);
  },

  async getJobs(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    creator_address?: string;
  }) {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) query.set(k, String(v));
      });
    }
    return apiFetch(`/api/v1/hybrid/jobs?${query}`);
  },
};

export { getAccessToken, getRefreshToken };
