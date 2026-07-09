import { IntakeQuestion } from '../form/types'

export const LANDLORD_QUESTIONS: IntakeQuestion[] = [
  {
    name: 'PROPERTY_MANAGER_INTRO',
    type: 'DISPLAY',
    required: false,
    html: '<h2>Almost done! Now just a few questions about your landlord.</h2><p>We use this information to run a conflict check and to help us write letters for you. We will <strong>not</strong> contact your landlord without your permission.</p>',
  },
  {
    name: 'PROPERTY_MANAGER_IS_AGENT',
    type: 'CHOICE_SINGLE',
    required: true,
    title:
      'Does your landlord use a <strong>real estate agent</strong> to manage the property?',
    description:
      'You can find this information on the first couple of pages of your lease.',
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
  },
  {
    name: 'AGENT_NAME',
    type: 'TEXT',
    required: false,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = true',
    title: "What is your landlord's agent's full name?",
    description:
      'You can find this information on the first couple of pages of your lease.',
  },
  {
    name: 'AGENT_ADDRESS',
    type: 'TEXT',
    required: false,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = true',
    title: "What is your landlord's agent's address?",
    description:
      'You can find this information on the first couple of pages of your lease.',
  },
  {
    name: 'AGENT_EMAIL',
    type: 'EMAIL',
    required: false,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = true',
    title: "What is your landlord's agent's email?",
    description:
      'You can find this information on the first couple of pages of your lease.',
  },
  {
    name: 'AGENT_PHONE',
    type: 'PHONE',
    required: false,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = true',
    title: "What is your landlord's agent's phone number?",
    description:
      'You can find this information on the first couple of pages of your lease.',
  },
  {
    name: 'LANDLORD_NAME',
    type: 'TEXT',
    required: false,
    title: "What is your landlord's full name?",
    description:
      'You can find this information on the first couple of pages of your lease.',
  },
  {
    name: 'LANDLORD_ADDRESS',
    type: 'TEXT',
    required: false,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = false',
    title: "What is your landlord's address?",
    description:
      'You can find this information on the first couple of pages of your lease.',
  },
  {
    name: 'LANDLORD_EMAIL',
    type: 'EMAIL',
    required: false,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = false',
    title: "What is your landlord's email?",
    description:
      'You can find this information on the first couple of pages of your lease.',
  },
  {
    name: 'LANDLORD_PHONE',
    type: 'PHONE',
    required: false,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = false',
    title: "What is your landlord's phone number?",
    description:
      'You can find this information on the first couple of pages of your lease.',
  },
]
