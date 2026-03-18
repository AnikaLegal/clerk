// Facebook events should be one of the "standard events": https://www.facebook.com/business/help/402791146561655?id=1205376682832142
// gtag used for Adwords conversion tracking.
// fbq used for Facebook ads
export const events = {
  onStartIntake: () => {
    // User starts the questionnaire
    gtag('event', 'startIntake', {
      event_category: 'questionnaire',
    })
  },
  onFirstSave: () => {
    // User save the questionnaire for the 1st time
    gtag('event', 'firstSave', {
      event_category: 'questionnaire',
    })
  },
  // Intake / Section 1 Complete (Basic Details)
  onBasicDetailsComplete: () => {
    gtag('event', 'basicDetailsSection', {
      event_category: 'questionnaire',
    })
  },
  // Intake / Section 2 Complete (Eligibility)
  onEligibilityComplete: () => {
    gtag('event', 'eligibilitySection', {
      event_category: 'questionnaire',
    })
  },
  // Intake / Section 3 Complete (Issues)
  onIssueDetailsComplete: () => {
    gtag('event', 'issueSection', {
      event_category: 'questionnaire',
    })
  },
  // Intake / Section 4 Complete (Landlord)
  onLandlordDetailsComplete: () => {
    gtag('event', 'landlordSection', {
      event_category: 'questionnaire',
    })
  },
  // Intake / Section 5 Complete (Personal Details)
  onPersonalDetailsComplete: () => {
    gtag('event', 'personalDetailsSection', {
      event_category: 'questionnaire',
    })
  },
  onFinishIntake: () => {
    // User submits the questionnaire
    gtag('event', 'finishIntake', {
      event_category: 'questionnaire',
    })
    fbq('track', 'SubmitApplication')
  },
}
