import { useQuery } from '@tanstack/react-query'
import { videosApi } from '../api/videos'
import type { Job } from '../api/types'

const TERMINAL: Job['status'][] = ['succeeded', 'failed']

export function useVideoJobs(videoId: string) {
  return useQuery({
    queryKey: ['videos', videoId, 'jobs'],
    queryFn: () => videosApi.jobs(videoId),
    refetchInterval: (query) => {
      const jobs = query.state.data
      if (!jobs || jobs.length === 0) return 2000
      const allDone = jobs.every((j) => TERMINAL.includes(j.status))
      return allDone ? false : 2000
    },
  })
}
