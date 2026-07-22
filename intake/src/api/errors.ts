// Shared API error predicates. Deliberately import-free so that pure logic
// modules (e.g. form/resume.ts) can be imported in node tests without pulling
// in the browser-only api client chain.

interface ApiErrorLike {
  status?: number
  data?: unknown
}

// True when the backend refuses because the submission is already complete
// (SubmittedException, code "already_submitted"). A plain 403 is NOT enough:
// CSRF failures are 403 too and must stay errors.
export const isAlreadySubmitted = (error: unknown): boolean => {
  const apiError = error as ApiErrorLike
  if (apiError?.status !== 403) return false
  const errors = (apiError.data as { errors?: { code?: string }[] })?.errors
  return errors?.some((e) => e.code === 'already_submitted') ?? false
}

// True for a plain HTTP 404 (e.g. a resume link whose submission is gone).
export const isNotFound = (error: unknown): boolean =>
  (error as ApiErrorLike)?.status === 404
