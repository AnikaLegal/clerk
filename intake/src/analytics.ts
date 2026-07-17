// Analytics for the intake funnel. gtag drives GA4 / Adwords, fbq the Facebook
// pixel. The Django template guarantees window.gtag / window.fbq exist (no-op
// stubs when the analytics IDs are not configured).

declare global {
  interface Window {
    gtag: (...args: unknown[]) => void
    fbq: (...args: unknown[]) => void
  }
}

// Identifies this form's events so they can be told apart from any other forms
// added later (GA4's form_* events use a form_id parameter the same way). A
// future form would send its own form_id with the same event names.
const FORM_ID = 'intake'

interface FormStep {
  // Position of the page in the survey's visible pages (survey.currentPageNo).
  index: number
  // The page's name (its UPPER_SNAKE key).
  name: string
  // Label of the section the page belongs to, if any.
  section?: string
}

export const events = {
  // User begins the questionnaire (advances off the welcome page). Named to sit
  // in the form_* funnel family without clashing with GA4's reserved
  // form_start / form_submit enhanced-measurement events.
  onFormBegin: () => window.gtag('event', 'form_begin', { form_id: FORM_ID }),
  // Fired the first time the user reaches each form page (see FormPage), for
  // per-page funnel / drop-off analysis. Build a GA4 funnel exploration on
  // step_index / step_name; the section groups the per-section drop-off.
  onFormStep: ({ index, name, section }: FormStep) =>
    window.gtag('event', 'form_step', {
      form_id: FORM_ID,
      step_index: index,
      step_name: name,
      ...(section ? { section } : {}),
    }),
  // User submits the questionnaire. Also fires the Facebook standard
  // SubmitApplication conversion.
  onFormComplete: () => {
    window.gtag('event', 'form_complete', { form_id: FORM_ID })
    window.fbq('track', 'SubmitApplication')
  },
}
