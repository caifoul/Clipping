import { Link, useParams } from 'react-router-dom'
import { useVideo } from '../hooks/useVideo'
import { useVideoJobs } from '../hooks/useVideoJobs'
import { JobList } from '../components/JobStatus/JobList'

export function VideoDetailPage() {
  const { videoId } = useParams<{ videoId: string }>()
  const videoQuery = useVideo(videoId!)
  const jobsQuery = useVideoJobs(videoId!)

  if (videoQuery.isLoading) return <p>Loading…</p>
  if (videoQuery.isError || !videoQuery.data) return <p className="error">Video not found.</p>

  const video = videoQuery.data

  return (
    <div className="page">
      <p>
        <Link to="/videos">&larr; Back to videos</Link>
      </p>
      <h1>{video.title ?? video.original_filename ?? video.source_url}</h1>
      <dl className="video-meta">
        <dt>Status</dt>
        <dd className={`status-pill status-pill--${video.status}`}>{video.status}</dd>
        <dt>Source</dt>
        <dd>{video.source_type === 'youtube_url' ? video.source_url : video.original_filename}</dd>
        <dt>Duration</dt>
        <dd>{video.duration_seconds ? `${Math.round(video.duration_seconds)}s` : '—'}</dd>
      </dl>
      {video.error_message && <p className="error">{video.error_message}</p>}

      <h2>Jobs</h2>
      <JobList jobs={jobsQuery.data ?? []} />
    </div>
  )
}
