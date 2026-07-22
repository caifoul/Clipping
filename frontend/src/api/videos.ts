import { api } from './client'
import type { Job, SourceVideo } from './types'

export const videosApi = {
  list: () => api.get<SourceVideo[]>('/api/videos'),
  get: (id: string) => api.get<SourceVideo>(`/api/videos/${id}`),
  createFromUrl: (url: string) => {
    const form = new FormData()
    form.set('url', url)
    return api.post<{ source_video_id: string }>('/api/videos', form)
  },
  createFromUpload: (file: File) => {
    const form = new FormData()
    form.set('file', file)
    return api.post<{ source_video_id: string }>('/api/videos', form)
  },
  jobs: (id: string) => api.get<Job[]>(`/api/videos/${id}/jobs`),
}
