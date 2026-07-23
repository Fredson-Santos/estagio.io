import type { Job, JobListResponse } from './types';

export function getBackendUrl(): string {
  if (typeof process !== 'undefined' && process.env && process.env.BACKEND_URL) {
    return process.env.BACKEND_URL;
  }
  return import.meta.env.BACKEND_URL || 'http://backend:8000';
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
