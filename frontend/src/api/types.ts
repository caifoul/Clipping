export type User = {
  id: string
  email: string
}

export type SourceType = 'youtube_url' | 'upload'
export type SourceVideoStatus = 'pending' | 'downloading' | 'downloaded' | 'failed'

export type SourceVideo = {
  id: string
  source_type: SourceType
  source_url: string | null
  original_filename: string | null
  title: string | null
  duration_seconds: number | null
  status: SourceVideoStatus
  error_message: string | null
  created_at: string
}

export type JobType =
  | 'ingest'
  | 'transcribe'
  | 'detect_silence'
  | 'detect_music'
  | 'analyze'
  | 'render_longform'
  | 'select_tiktok'
  | 'render_tiktok'
  | 'select_micro'
  | 'render_micro'

export type JobStatus = 'queued' | 'running' | 'succeeded' | 'failed'

export type Job = {
  id: string
  job_type: JobType
  status: JobStatus
  progress_pct: number | null
  error_message: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string
}
