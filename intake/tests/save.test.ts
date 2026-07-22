import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../src/api', () => ({
  api: {
    submission: {
      create: vi.fn(),
      update: vi.fn(),
      submit: vi.fn(),
    },
  },
}))
vi.mock('../src/utils', () => ({
  logException: vi.fn(),
}))

import { api } from '../src/api'
import { SubmissionSaver } from '../src/form/save'
import { logException } from '../src/utils'

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

// Matches PATCH_DEBOUNCE_MS in save.ts.
const DEBOUNCE_MS = 1500

// Let promise chains settle while fake timers are active (each .then/.catch/
// .finally hop is one microtask; five ticks comfortably covers the chains).
const flushMicrotasks = async () => {
  for (let i = 0; i < 5; i++) await Promise.resolve()
}

describe('SubmissionSaver.schedulePatch', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    vi.useFakeTimers()
    submission.update.mockResolvedValue({ id: 'sub-1', answers: ANSWERS })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('debounces rapid changes and sends only the latest answers', () => {
    const saver = new SubmissionSaver('sub-1', () => {})
    saver.schedulePatch({ EMAIL: 'a@example.com' })
    vi.advanceTimersByTime(1000)
    saver.schedulePatch({ EMAIL: 'b@example.com' })
    // The first schedule's timer was cancelled, so nothing has fired yet even
    // though more than DEBOUNCE_MS has passed since the first call.
    vi.advanceTimersByTime(DEBOUNCE_MS - 1)
    expect(submission.update).not.toHaveBeenCalled()
    vi.advanceTimersByTime(1)
    expect(submission.update).toHaveBeenCalledTimes(1)
    expect(submission.update).toHaveBeenCalledWith('sub-1', {
      EMAIL: 'b@example.com',
    })
  })

  it('does nothing until the submission exists', () => {
    const saver = new SubmissionSaver(null, () => {})
    saver.schedulePatch(ANSWERS)
    vi.advanceTimersByTime(DEBOUNCE_MS * 3)
    expect(submission.update).not.toHaveBeenCalled()
  })

  it('keeps one PATCH in flight and re-sends the latest snapshot after it', async () => {
    let resolveFirst!: (value: { id: string; answers: typeof ANSWERS }) => void
    submission.update.mockImplementationOnce(
      () => new Promise((resolve) => (resolveFirst = resolve))
    )

    const saver = new SubmissionSaver('sub-1', () => {})
    saver.schedulePatch({ N: 1 })
    vi.advanceTimersByTime(DEBOUNCE_MS) // First PATCH now in flight.
    saver.schedulePatch({ N: 2 })
    saver.schedulePatch({ N: 3 })
    vi.advanceTimersByTime(DEBOUNCE_MS) // Debounce fires, but a PATCH is in flight.
    expect(submission.update).toHaveBeenCalledTimes(1)

    resolveFirst({ id: 'sub-1', answers: ANSWERS })
    await flushMicrotasks()
    // The queued snapshot goes out once the in-flight PATCH settles, and the
    // intermediate { N: 2 } snapshot was never sent.
    expect(submission.update).toHaveBeenCalledTimes(2)
    expect(submission.update.mock.calls).toEqual([
      ['sub-1', { N: 1 }],
      ['sub-1', { N: 3 }],
    ])
  })

  it('logs a failed PATCH and recovers on the next schedule', async () => {
    const boom = new Error('network down')
    submission.update.mockRejectedValueOnce(boom)
    const saver = new SubmissionSaver('sub-1', () => {})
    saver.schedulePatch({ N: 1 })
    vi.advanceTimersByTime(DEBOUNCE_MS)
    await flushMicrotasks()
    expect(logException).toHaveBeenCalledWith(boom)

    saver.schedulePatch({ N: 2 })
    vi.advanceTimersByTime(DEBOUNCE_MS)
    await flushMicrotasks()
    expect(submission.update).toHaveBeenCalledTimes(2)
    expect(submission.update).toHaveBeenLastCalledWith('sub-1', { N: 2 })
  })

  it('submit cancels a pending debounce so only the final answers are saved', async () => {
    submission.submit.mockResolvedValue(undefined)
    const saver = new SubmissionSaver('sub-1', () => {})
    saver.schedulePatch({ N: 1 })
    await saver.submit(ANSWERS)
    vi.advanceTimersByTime(DEBOUNCE_MS * 3)
    await flushMicrotasks()
    expect(submission.update).toHaveBeenCalledTimes(1)
    expect(submission.update).toHaveBeenCalledWith('sub-1', ANSWERS)
    expect(submission.submit).toHaveBeenCalledWith('sub-1')
  })

  it('submit waits out an in-flight PATCH before the final save', async () => {
    submission.submit.mockResolvedValue(undefined)
    let resolvePatch!: (value: { id: string; answers: typeof ANSWERS }) => void
    submission.update.mockImplementationOnce(
      () => new Promise((resolve) => (resolvePatch = resolve))
    )

    const saver = new SubmissionSaver('sub-1', () => {})
    saver.schedulePatch({ N: 1 })
    vi.advanceTimersByTime(DEBOUNCE_MS) // PATCH in flight.

    let submitted = false
    const submitPromise = saver.submit(ANSWERS).then(() => {
      submitted = true
    })
    await flushMicrotasks()
    // The final save must not start while the PATCH is still in flight.
    expect(submitted).toBe(false)
    expect(submission.update).toHaveBeenCalledTimes(1)

    resolvePatch({ id: 'sub-1', answers: ANSWERS })
    await submitPromise
    expect(submission.update).toHaveBeenCalledTimes(2)
    expect(submission.update).toHaveBeenLastCalledWith('sub-1', ANSWERS)
    expect(submission.submit).toHaveBeenCalledTimes(1)
  })

  it('submit still succeeds when the awaited in-flight PATCH fails', async () => {
    // Guards the runPatch construction: patchInFlight has its rejection
    // consumed by .catch(logException), so awaiting it in submit() must never
    // throw - the final update supersedes the lost snapshot.
    submission.submit.mockResolvedValue(undefined)
    let rejectPatch!: (reason: unknown) => void
    submission.update.mockImplementationOnce(
      () => new Promise((_, reject) => (rejectPatch = reject))
    )

    const saver = new SubmissionSaver('sub-1', () => {})
    saver.schedulePatch({ N: 1 })
    vi.advanceTimersByTime(DEBOUNCE_MS) // PATCH in flight.

    const submitPromise = saver.submit(ANSWERS)
    const boom = new Error('network down')
    rejectPatch(boom)
    await expect(submitPromise).resolves.toBeUndefined()
    expect(logException).toHaveBeenCalledWith(boom)
    expect(submission.update).toHaveBeenCalledTimes(2)
    expect(submission.update).toHaveBeenLastCalledWith('sub-1', ANSWERS)
    expect(submission.submit).toHaveBeenCalledWith('sub-1')
  })
})
