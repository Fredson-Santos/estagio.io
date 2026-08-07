export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  modality?: string;
  area?: string;
  salary?: string | null;
  description?: string;
  source_url?: string;
  source_id?: string;
  source_name?: string | null;
  posted_at?: string | null;
  company_logo?: string | null;
  is_new?: boolean;
  is_featured?: boolean;
  is_active?: boolean;
  status?: string;
}

export interface JobListResponse {
  items: Job[];
  total: number;
  skip: number;
  limit: number;
}

export interface PlatformResponse {
  slug: string;
  name: string;
  count: number;
}

export interface JobWithDisplay extends Job {
  publishedAt?: string;
  logo?: string | undefined;
  modality?: string;
  isNew?: boolean;
  postedLabel?: string;
  area?: string;
  datePosted?: string;
  sourceUrl?: string;
  sourceName?: string;
}

export interface JobUpdate {
  is_featured?: boolean;
  is_active?: boolean;
}

export interface AdminStats {
  total_jobs: number;
  active_jobs: number;
  featured_jobs: number;
  sources: number;
  last_scraped_at: string | null;
}

export interface ScraperRunResponse {
  message: string;
  status: string;
}
