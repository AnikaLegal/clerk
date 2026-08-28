import { API_URLS } from '../consts'
import { Answers, Upload } from '../form/types'
import { http } from './client'
import { getRecaptchaToken } from './recaptcha'
import type { components } from './types.generated'

// Contract types generated from openapi/ (npm run schema). The looser
// generated `answers` object is narrowed to the form's Answers type here,
// at the API boundary.
type IntakeSubmission = components['schemas']['IntakeSubmission']

export interface Submission extends Omit<IntakeSubmission, 'answers'> {
  answers: Answers
}

export const api = {
  submission: {
    // Read an existing submission (the resume-from-email flow).
    get: async (id: string): Promise<Submission> => {
      return (await http.get(`${API_URLS.SUBMISSION}${id}/`)) as Submission
    },
    // Create a new submission, fired once the user provides their email.
    create: async (answers: Answers): Promise<Submission> => {
      return (await http.post(API_URLS.SUBMISSION, { answers })) as Submission
    },
    // Update answers as the user progresses.
    update: async (id: string, answers: Answers): Promise<Submission> => {
      return (await http.patch(`${API_URLS.SUBMISSION}${id}/`, {
        answers,
      })) as Submission
    },
    // Mark the submission complete, which queues backend processing.
    submit: async (id: string): Promise<void> => {
      await http.post(`${API_URLS.SUBMISSION}${id}/submit/`, {})
    },
    // Email the user their own resume link, so they can finish on another
    // device. Rejected (400) when the submission holds no email address.
    emailResumeLink: async (id: string): Promise<void> => {
      await http.post(`${API_URLS.SUBMISSION}${id}/email-resume-link/`, {})
    },
  },
  upload: {
    // Upload a single file. The returned object is the answer value stored
    // against UPLOAD questions.
    create: async (file: File): Promise<Upload> => {
      const form = new FormData()
      form.append('file', file)
      return (await http.postMultipart(API_URLS.UPLOAD, form)) as Upload
    },
  },
  noemail: {
    // Contact fallback for users without an email address: creates a
    // WebflowContact via the same pipeline as the site's landing contact form,
    // guarded by a reCAPTCHA v3 token.
    create: async (name: string, phone: string): Promise<void> => {
      const captcha = await getRecaptchaToken('intake_noemail')
      await http.post(API_URLS.NO_EMAIL, { name, phone, captcha })
    },
  },
}
