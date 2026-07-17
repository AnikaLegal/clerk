// Funnel events, ported verbatim from the old intake repo's
// analytics/events.js so reporting continuity is preserved.
// gtag is used for Adwords conversion tracking, fbq for Facebook ads.
// The Django template guarantees window.gtag / window.fbq exist (no-op
// stubs when analytics IDs are not configured).

declare global {
  interface Window {
    gtag: (...args: unknown[]) => void
    fbq: (...args: unknown[]) => void
  }
}

const questionnaireEvent = (action: string) => {
  window.gtag('event', action, { event_category: 'questionnaire' })
}

// Identifies this form's events so they can be told apart from any other forms
// added later (GA4's form_start / form_submit use a form_id parameter the same
// way). A future form would send its own form_id with the same event names.
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
  // User starts the questionnaire
  onStartIntake: () => questionnaireEvent('startIntake'),
  // When we first get the user's email and save the form for the first time.
  onFirstSave: () => questionnaireEvent('firstSave'),
  // Intake / Section 1 Complete (Eligibility)
  onEligibilityComplete: () => questionnaireEvent('eligibilitySection'),
  // Intake / Section 2 Complete (Basic Details)
  onBasicDetailsComplete: () => questionnaireEvent('basicDetailsSection'),
  // Intake / Section 3 Complete (Issues)
  onIssueDetailsComplete: () => questionnaireEvent('issueSection'),
  // Intake / Section 4 Complete (Landlord)
  onLandlordDetailsComplete: () => questionnaireEvent('landlordSection'),
  // Intake / Section 5 Complete (Personal Details)
  onPersonalDetailsComplete: () => questionnaireEvent('personalDetailsSection'),
  // User submits the questionnaire
  onFinishIntake: () => {
    questionnaireEvent('finishIntake')
    window.fbq('track', 'SubmitApplication')
  },
  // Fired the first time the user reaches each form page (see FormPage), for
  // per-page funnel / drop-off analysis. Finer-grained than the section events
  // above; build a GA4 funnel exploration on step_index / step_name.
  onFormStep: ({ index, name, section }: FormStep) =>
    window.gtag('event', 'form_step', {
      form_id: FORM_ID,
      step_index: index,
      step_name: name,
      ...(section ? { section } : {}),
    }),
}
