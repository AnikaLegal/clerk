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
}
