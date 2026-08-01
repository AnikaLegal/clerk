import { IntakeQuestion } from '../form/types'

export const ABOUT_QUESTIONS: IntakeQuestion[] = [
  {
    name: 'EMAIL',
    required: false,
    type: 'EMAIL',
    maxLength: 150,
    title: "What's the best <strong>email</strong> to reach you?",
    description:
      "We'll only use this to contact you about your request. We won't share your details.",
    // Disabled (and no longer required) while the no-email escape hatch below
    // is ticked, so the page visibly reflects the choice - and any typed email
    // is cleared, so a contradictory address can't linger in the answers.
    enableIf: '{NO_EMAIL} <> true',
    requiredIf: '{NO_EMAIL} <> true',
    resetValueIf: '{NO_EMAIL} = true',
  },
  {
    // The escape hatch for users without an email address, rendered as a
    // selectable row under the field. Ticking it disables the email field, and
    // Continue exits to the no-email contact fallback (see exits.ts). Never
    // serialized: the wire contract has no such field.
    name: 'NO_EMAIL',
    type: 'BOOLEAN',
    required: false,
    uiOnly: true,
    title: "I don't have an email address",
  },
  {
    name: 'FIRST_NAME',
    required: true,
    type: 'TEXT',
    maxLength: 150,
    title: "What's your <strong>first name?</strong>",
  },
  {
    name: 'LAST_NAME',
    required: true,
    type: 'TEXT',
    maxLength: 150,
    title: 'And your <strong>last name?</strong>',
  },
  {
    name: 'PREFERRED_NAME',
    required: false,
    type: 'TEXT',
    maxLength: 150,
    title:
      'Do you have a <strong>preferred name</strong> that you would like us to use?',
  },
  {
    name: 'PHONE',
    required: true,
    type: 'PHONE',
    title: 'What is the best <strong>phone number</strong> to contact you on?',
    description:
      "We'll only use this to contact you about your request. We won't share your details.",
  },
  {
    name: 'AVAILABILITY',
    required: true,
    type: 'CHOICE_MULTI',
    choices: [
      { value: 'WEEK_DAY', text: 'Weekdays (9am to 5pm)' },
      { value: 'WEEK_EVENING', text: 'Weekdays (5pm to 8pm)' },
      { value: 'SATURDAY', text: 'Saturday (9am to 5pm)' },
      { value: 'SUNDAY', text: 'Sunday (9am to 5pm)' },
    ],
    title: 'What are the best times for us to call you?',
    description:
      "We know you're busy: we'll try to call you during these times. Please select all that apply.",
  },
]
