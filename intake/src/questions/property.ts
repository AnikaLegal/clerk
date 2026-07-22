import { IntakeQuestion } from '../form/types'

export const PROPERTY_QUESTIONS: IntakeQuestion[] = [
  {
    name: 'PROPERTY_INTRO',
    type: 'DISPLAY',
    required: false,
    visibleIf: "{ISSUES} <> 'BONDS'",
    html: '<h2>Your rental property</h2><p>Thanks for your answers so far. We have a few questions about the home that you are renting.</p>',
  },
  {
    // Bonds users may already have moved out, so this variant avoids assuming
    // a current tenancy.
    name: 'PROPERTY_INTRO_BONDS',
    type: 'DISPLAY',
    required: false,
    visibleIf: "{ISSUES} = 'BONDS'",
    html: '<h2>Your rental property</h2><p>Thanks for your answers so far. We have a few questions about the rental property your bond relates to.</p>',
  },
  {
    name: 'RENTAL_CIRCUMSTANCES',
    type: 'CHOICE_SINGLE',
    required: true,
    title: 'Who are you renting with?',
    choices: [
      { value: 'SOLO', text: 'Renting by myself' },
      { value: 'FLATMATES', text: 'Renting with flatmates' },
      { value: 'PARTNER', text: 'Renting with partner' },
      { value: 'FAMILY', text: 'Renting with family / children' },
      { value: 'OTHER', text: 'Other' },
    ],
  },
  {
    name: 'IS_ON_LEASE',
    type: 'CHOICE_SINGLE',
    required: true,
    title: 'Are you named as a tenant on the lease?',
    description:
      'If you signed the lease, it is likely that you are named as a tenant.',
    choices: [
      { value: 'YES', text: 'Yes' },
      { value: 'NO', text: 'No' },
      { value: 'VERBAL', text: 'I have a verbal lease agreement' },
    ],
  },
  {
    name: 'START_DATE',
    type: 'DATE',
    required: true,
    title: 'When did you start living at this property?',
    description: 'You can find this written on your lease.',
  },
  // The home address block (grouped by the HOME_ADDRESS panel in pages.ts).
  // With Google Places available, the search box drives the read-only street/
  // suburb/postcode fields below it; the manual checkbox flips them editable
  // (and required) instead. Without Places (no key: dev/CI, or script failure)
  // MAPS_AVAILABLE is unset/false, so the search box and checkbox hide and the
  // three fields are editable and required - plain manual entry.
  // MAPS_AVAILABLE / ADDRESS_SEARCH / ADDRESS_MANUAL never reach the backend:
  // the first is a bare survey.data key, the others are uiOnly questions.
  {
    name: 'ADDRESS_SEARCH',
    type: 'TEXT',
    required: false,
    uiOnly: true,
    // No maxLength: the search text is never submitted (uiOnly), and a cap
    // would render SurveyJS's character counter on the field.
    title: 'Find your address',
    placeholder: 'Start typing your address...',
    visibleIf: '{MAPS_AVAILABLE} = true',
    enableIf: '{ADDRESS_MANUAL} <> true',
    requiredIf: '{MAPS_AVAILABLE} = true and {ADDRESS_MANUAL} <> true',
    validators: [
      {
        type: 'expression',
        expression: '{ADDRESS} notempty or {ADDRESS_MANUAL} = true',
        text: 'Please choose an address from the suggestions',
      },
    ],
  },
  {
    name: 'ADDRESS_MANUAL',
    type: 'BOOLEAN',
    required: false,
    uiOnly: true,
    title: 'Enter address manually',
    visibleIf: '{MAPS_AVAILABLE} = true',
  },
  {
    name: 'ADDRESS',
    type: 'TEXT',
    required: false,
    requiredIf: '{ADDRESS_MANUAL} = true or {MAPS_AVAILABLE} <> true',
    enableIf: '{ADDRESS_MANUAL} = true or {MAPS_AVAILABLE} <> true',
    maxLength: 256,
    title: 'Street address',
  },
  {
    name: 'SUBURB',
    type: 'TEXT',
    required: false,
    requiredIf: '{ADDRESS_MANUAL} = true or {MAPS_AVAILABLE} <> true',
    enableIf: '{ADDRESS_MANUAL} = true or {MAPS_AVAILABLE} <> true',
    maxLength: 128,
    title: 'Suburb',
  },
  {
    name: 'POSTCODE',
    type: 'NUMBER',
    required: false,
    requiredIf: '{ADDRESS_MANUAL} = true or {MAPS_AVAILABLE} <> true',
    enableIf: '{ADDRESS_MANUAL} = true or {MAPS_AVAILABLE} <> true',
    max: 999999,
    title: 'Postcode',
  },
  {
    name: 'WEEKLY_RENT',
    type: 'NUMBER',
    required: true,
    max: 100000,
    // {RENT_IS} renders as 'is (or was)' on the bonds branch and 'is'
    // elsewhere (see calculatedValues in form/model.ts).
    title: 'How much {RENT_IS} your weekly rent?',
  },
]
