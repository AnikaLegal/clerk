import { IntakeQuestion } from '../form/types'

export const ABOUT_QUESTIONS: IntakeQuestion[] = [
  {
    name: 'EMAIL',
    required: true,
    type: 'EMAIL',
    maxLength: 150,
    title: "What's the best <strong>email</strong> to reach you?",
    description:
      "We'll only use this to contact you about your request. We won't share your details.",
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
