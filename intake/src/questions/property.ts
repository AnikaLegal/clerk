import { IntakeQuestion } from '../form/types'

export const PROPERTY_QUESTIONS: IntakeQuestion[] = [
  {
    name: 'PROPERTY_INTRO',
    type: 'DISPLAY',
    required: false,
    html: '<h2>Your rental property</h2><p>Thanks for your answers so far. We have a few questions about the home that you are renting.</p>',
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
    description: 'You can find this written on your lease',
  },
  {
    name: 'SUBURB',
    type: 'TEXT',
    required: true,
    title: 'What suburb do you live in?',
  },
  {
    name: 'POSTCODE',
    type: 'NUMBER',
    required: true,
    title: 'What is your postcode?',
  },
  {
    name: 'ADDRESS',
    type: 'TEXT',
    required: true,
    title: 'What is your street address?',
  },
  {
    name: 'WEEKLY_RENT',
    type: 'NUMBER',
    required: true,
    title: 'How much is your weekly rent?',
  },
]
