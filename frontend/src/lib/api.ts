import type { AdminStats, Job, JobListResponse, PlatformResponse } from './types';

export function getBackendUrl(): string {
  if (typeof process !== 'undefined' && process.env && process.env.BACKEND_URL) {
    return process.env.BACKEND_URL;
  }
  return import.meta.env.BACKEND_URL || 'http://127.0.0.1:8000';
}

export function getAdminApiKey(): string {
  if (typeof process !== 'undefined' && process.env && process.env.ADMIN_API_KEY) {
    return process.env.ADMIN_API_KEY;
  }
  return import.meta.env.ADMIN_API_KEY || '';
}

const REQUEST_TIMEOUT_MS = 8000;

export async function fetchJobs(path: string): Promise<JobListResponse> {
  const backendUrl = getBackendUrl();
  const url = `${backendUrl}/api/v1${path}`;
  const response = await fetch(url, {
    headers: { Accept: 'application/json' },
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  });
  if (!response.ok) {
    throw new Error(`Backend ${response.status}`);
  }
  return (await response.json()) as JobListResponse;
}

export async function fetchJob(id: string): Promise<Job> {
  const backendUrl = getBackendUrl();
  const url = `${backendUrl}/api/v1/jobs/${id}`;
  const response = await fetch(url, {
    headers: { Accept: 'application/json' },
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  });
  if (!response.ok) {
    throw new Error(`Backend ${response.status}`);
  }
  return (await response.json()) as Job;
}

export async function fetchPlatforms(): Promise<PlatformResponse[]> {
  const backendUrl = getBackendUrl();
  const url = `${backendUrl}/api/v1/jobs/platforms`;
  const response = await fetch(url, {
    headers: { Accept: 'application/json' },
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  });
  if (!response.ok) return [];
  return (await response.json()) as PlatformResponse[];
}

export async function fetchAdminStats(): Promise<AdminStats> {
  const backendUrl = getBackendUrl();
  const url = `${backendUrl}/api/v1/admin/stats`;
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
      'X-Admin-Key': getAdminApiKey(),
    },
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  });
  if (!response.ok) {
    throw new Error(`Backend ${response.status}`);
  }
  return (await response.json()) as AdminStats;
}
