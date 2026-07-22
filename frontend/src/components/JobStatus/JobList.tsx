import type { Job } from '../../api/types'

const STATUS_LABEL: Record<Job['status'], string> = {
  queued: 'Queued',
  running: 'Running',
  succeeded: 'Done',
  failed: 'Failed',
}

export function JobList({ jobs }: { jobs: Job[] }) {
  if (jobs.length === 0) {
    return <p className="muted">No jobs yet.</p>
  }

  return (
    <ul className="job-list">
      {jobs.map((job) => (
        <li key={job.id} className={`job-row job-row--${job.status}`}>
          <span className="job-row__type">{job.job_type}</span>
          <span className="job-row__status">{STATUS_LABEL[job.status]}</span>
          {job.error_message && <span className="job-row__error">{job.error_message}</span>}
        </li>
      ))}
    </ul>
  )
}
