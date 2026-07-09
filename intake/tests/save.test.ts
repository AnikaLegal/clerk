import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../src/api', () => ({
  api: {
    submission: {
      create: vi.fn(),
      update: vi.fn(),
      submit: vi.fn(),
    },
  },
}))

import { api } from '../src/api'
import { SubmissionSaver } from '../src/form/save'

const submission = vi.mocked(api.submission)
const ANSWERS = { EMAIL: 'test@example.com', ISSUES: 'REPAIRS' }
const ALREADY_SUBMITTED = {
  status: 403,
  data: { type: 'client_error', errors: [{ code: 'already_submitted' }] },
}
const CSRF_FORBIDDEN = {
  status: 403,
  data: { type: 'client_error', errors: [{ code: 'permission_denied' }] },
}

describe('SubmissionSaver', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    submission.create.mockResolvedValue({ id: 'sub-1', answers: ANSWERS })
    submission.update.mockResolvedValue({ id: 'sub-1', answers: ANSWERS })
    submission.submit.mockResolvedValue(undefined)
  })

  it('creates the submission only once', async () => {
    const saver = new SubmissionSaver(null, () => {})
    await Promise.all([saver.create(ANSWERS), saver.create(ANSWERS)])
    await saver.create(ANSWERS)
    expect(submission.create).toHaveBeenCalledTimes(1)
    expect(saver.submissionId).toBe('sub-1')
  })

  it('submit awaits a pending create instead of creating a duplicate', async () => {
    let resolveCreate: (value: { id: string; answers: typeof ANSWERS }) => void
    submission.create.mockImplementationOnce(
      () => new Promise((resolve) => (resolveCreate = resolve))
    )
    const saver = new SubmissionSaver(null, () => {})
    const createPromise = saver.create(ANSWERS)
    const submitPromise = saver.submit(ANSWERS)
    resolveCreate!({ id: 'sub-1', answers: ANSWERS })
    await Promise.all([createPromise, submitPromise])
    expect(submission.create).toHaveBeenCalledTimes(1)
    expect(submission.update).toHaveBeenCalledWith('sub-1', ANSWERS)
    expect(submission.submit).toHaveBeenCalledWith('sub-1')
  })

  it('submit falls back to create-then-submit when no id exists', async () => {
    const saver = new SubmissionSaver(null, () => {})
    await saver.submit(ANSWERS)
    expect(submission.create).toHaveBeenCalledTimes(1)
    expect(submission.update).not.toHaveBeenCalled()
    expect(submission.submit).toHaveBeenCalledWith('sub-1')
  })

  it('treats an already-submitted 403 as success (lost-response retry)', async () => {
    submission.update.mockRejectedValueOnce(ALREADY_SUBMITTED)
    const saver = new SubmissionSaver('sub-1', () => {})
    await expect(saver.submit(ANSWERS)).resolves.toBeUndefined()
    expect(submission.submit).not.toHaveBeenCalled()
  })

  it('still fails on other 403s (e.g. CSRF)', async () => {
    submission.update.mockRejectedValueOnce(CSRF_FORBIDDEN)
    const saver = new SubmissionSaver('sub-1', () => {})
    await expect(saver.submit(ANSWERS)).rejects.toEqual(CSRF_FORBIDDEN)
  })
})
