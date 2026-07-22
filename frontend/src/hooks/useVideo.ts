import { useQuery } from '@tanstack/react-query'
import { videosApi } from '../api/videos'

const IN_PROGRESS: string[] = ['pending', 'downloading']

export function useVideo(videoId: string) {
  return useQuery({
    queryKey: ['videos', videoId],
    queryFn: () => videosApi.get(videoId),
    refetchInterval: (query) => (query.state.data && IN_PROGRESS.includes(query.state.data.status) ? 2000 : false),
  })
}
