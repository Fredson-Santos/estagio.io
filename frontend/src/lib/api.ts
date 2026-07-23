import type { Job, JobListResponse } from './types';

const DEFAULT_BACKEND_URL = 'http://localhost:8000';
const BACKEND_URL = (typeof process !== 'undefined' && process.env.BACKEND_URL) || DEFAULT_BACKEND_URL;

const REQUEST_TIMEOUT_MS = 8000;

export async function fetchJobs(path: string): Promise<JobListResponse> {
  const url = `${BACKEND_URL}/api/v1${path}`;
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
  const url = `${BACKEND_URL}/api/v1/jobs/${id}`;
  const response = await fetch(url, {
    headers: { Accept: 'application/json' },
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  });
  if (!response.ok) {
    throw new Error(`Backend ${response.status}`);
  }
  return (await response.json()) as Job;
}

export { BACKEND_URL };
