import { IntakeQuestion } from '../form/types'

// The landlord / agent contact details all live on a person's lease. The hint
// sits on the first field of each of the two groups rather than under every
// field.
const LEASE_HINT =
  'You can find this information on the first couple of pages of your lease.'

export const LANDLORD_QUESTIONS: IntakeQuestion[] = [
  {
    name: 'PROPERTY_MANAGER_INTRO',
    type: 'DISPLAY',
    required: false,
    html: '<h2>Almost done! Now just a few questions about your landlord</h2><p>We use this information to run a conflict check and to help us write letters for you. We will <strong>not</strong> contact your landlord without your permission.</p>',
  },
  {
    name: 'PROPERTY_MANAGER_IS_AGENT',
    type: 'CHOICE_SINGLE',
    required: true,
    title:
      'Does your landlord use a <strong>real estate agent</strong> to manage the property?',
    description: LEASE_HINT,
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
  },
  {
    name: 'AGENT_NAME',
    type: 'TEXT',
    required: false,
    maxLength: 256,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = true',
    title: "What is your landlord's agent's full name?",
  },
  {
    name: 'AGENT_ADDRESS',
    type: 'TEXT',
    required: false,
    maxLength: 256,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = true',
    title: "What is your landlord's agent's address?",
  },
  {
    name: 'AGENT_EMAIL',
    type: 'EMAIL',
    required: false,
    maxLength: 150,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = true',
    title: "What is your landlord's agent's email?",
  },
  {
    name: 'AGENT_PHONE',
    type: 'PHONE',
    required: false,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = true',
    title: "What is your landlord's agent's phone number?",
  },
  {
    name: 'LANDLORD_NAME',
    type: 'TEXT',
    required: false,
    maxLength: 256,
    title: "What is your landlord's full name?",
    description: LEASE_HINT,
  },
  {
    name: 'LANDLORD_ADDRESS',
    type: 'TEXT',
    required: false,
    maxLength: 256,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = false',
    title: "What is your landlord's address?",
  },
  {
    name: 'LANDLORD_EMAIL',
    type: 'EMAIL',
    required: false,
    maxLength: 150,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = false',
    title: "What is your landlord's email?",
  },
  {
    name: 'LANDLORD_PHONE',
    type: 'PHONE',
    required: false,
    visibleIf: '{PROPERTY_MANAGER_IS_AGENT} = false',
    title: "What is your landlord's phone number?",
  },
]
