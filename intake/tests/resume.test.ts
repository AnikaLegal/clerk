import { describe, expect, it } from 'vitest'

import { classifyResumeError, shouldKeepLocalState } from '../src/form/resume'
import { StoredState } from '../src/form/storage'

const local = (overrides: Partial<StoredState>): StoredState => ({
  submissionId: 'sub-1',
  data: {},
  visited: [],
  currentPage: null,
  session: null,
  ...overrides,
})

describe('shouldKeepLocalState', () => {
  it('keeps local state for the same submission with more progress', () => {
    expect(
      shouldKeepLocalState(
        local({ visited: ['EMAIL', 'ISSUES', 'PHONE'] }),
        'sub-1',
        { EMAIL: 'a@example.com', ISSUES: 'REPAIRS' }
      )
    ).toBe(true)
  })

  it('keeps local state on equal progress (local is same-device richer)', () => {
    expect(
      shouldKeepLocalState(local({ visited: ['EMAIL'] }), 'sub-1', {
        EMAIL: 'a@example.com',
      })
    ).toBe(true)
  })

  it('takes the server copy when it has more progress', () => {
    expect(
      shouldKeepLocalState(local({ visited: ['EMAIL'] }), 'sub-1', {
        EMAIL: 'a@example.com',
        ISSUES: 'REPAIRS',
      })
    ).toBe(false)
  })

  it('takes the server copy for a different submission', () => {
    expect(
      shouldKeepLocalState(
        local({ submissionId: 'sub-2', visited: ['EMAIL', 'ISSUES'] }),
        'sub-1',
        { EMAIL: 'a@example.com' }
      )
    ).toBe(false)
  })

  it('takes the server copy when there is no local state', () => {
    expect(
      shouldKeepLocalState(local({ submissionId: null }), 'sub-1', {
        EMAIL: 'a@example.com',
      })
    ).toBe(false)
  })
})

describe('classifyResumeError', () => {
  it('treats a 404 as a dead link', () => {
    expect(classifyResumeError({ status: 404 })).toBe('not-found')
  })

  it('recognises the already-submitted 403', () => {
    expect(
      classifyResumeError({
        status: 403,
        data: { errors: [{ code: 'already_submitted' }] },
      })
    ).toBe('already-submitted')
  })

  it('keeps other 403s (e.g. CSRF) as retryable errors', () => {
    expect(
      classifyResumeError({
        status: 403,
        data: { errors: [{ code: 'permission_denied' }] },
      })
    ).toBe('error')
  })

  it('treats network failures as retryable errors', () => {
    expect(classifyResumeError(new TypeError('Failed to fetch'))).toBe('error')
  })
})
