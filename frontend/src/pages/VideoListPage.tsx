import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { videosApi } from '../api/videos'
import { ApiError } from '../api/client'
import { useAuth } from '../hooks/useAuth'

export function VideoListPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [url, setUrl] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const videosQuery = useQuery({ queryKey: ['videos'], queryFn: videosApi.list })

  const createMutation = useMutation({
    mutationFn: () => (file ? videosApi.createFromUpload(file) : videosApi.createFromUrl(url)),
    onSuccess: async ({ source_video_id }) => {
      setUrl('')
      setFile(null)
      await queryClient.invalidateQueries({ queryKey: ['videos'] })
      navigate(`/videos/${source_video_id}`)
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : 'Could not add video'),
  })

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    if (!url && !file) {
      setError('Paste a YouTube URL or choose a file')
      return
    }
    createMutation.mutate()
  }

  return (
    <div className="page">
      <header className="page__header">
        <h1>Your videos</h1>
        <div>
          <span className="muted">{user?.email}</span>{' '}
          <button onClick={() => logout()}>Log out</button>
        </div>
      </header>

      <form onSubmit={onSubmit} className="add-video-form">
        <label>
          YouTube URL (including ended livestream VODs)
          <input
            type="url"
            placeholder="https://www.youtube.com/watch?v=..."
            value={url}
            onChange={(e) => {
              setUrl(e.target.value)
              setFile(null)
            }}
            disabled={!!file}
          />
        </label>
        <div className="or-divider">or</div>
        <label>
          Upload a video file
          <input
            type="file"
            accept="video/*"
            onChange={(e) => {
              setFile(e.target.files?.[0] ?? null)
              setUrl('')
            }}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={createMutation.isPending}>
          {createMutation.isPending ? 'Adding…' : 'Add video'}
        </button>
      </form>

      {videosQuery.isLoading && <p>Loading…</p>}
      {videosQuery.data && videosQuery.data.length === 0 && (
        <p className="muted">No videos yet — add one above.</p>
      )}
      <ul className="video-list">
        {videosQuery.data?.map((video) => (
          <li key={video.id}>
            <Link to={`/videos/${video.id}`}>
              {video.title ?? video.original_filename ?? video.source_url ?? video.id}
            </Link>
            <span className={`status-pill status-pill--${video.status}`}>{video.status}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
