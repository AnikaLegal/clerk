import { IntakeQuestion } from '../../form/types'

export const REPAIRS_QUESTIONS: IntakeQuestion[] = [
  {
    name: 'REPAIRS_INTRO',
    required: false,
    type: 'DISPLAY',
    visibleIf: "{ISSUES} = 'REPAIRS'",
    html: '<h2>Rental repairs</h2><p>Thanks for your answers so far. We have a few questions around your rental repairs.</p>',
  },
  {
    name: 'REPAIRS_ISSUE_PHOTO',
    required: false,
    type: 'UPLOAD',
    visibleIf: "{ISSUES} = 'REPAIRS'",
    title: 'Do you have any photos of the problems that you could upload?',
  },
  {
    name: 'REPAIRS_ISSUE_START',
    required: true,
    type: 'DATE',
    visibleIf: "{ISSUES} = 'REPAIRS'",
    title: 'When did these problems first happen?',
    description:
      "If you don't know the exact date, that's okay. An approximate date is fine.",
  },
  {
    name: 'REPAIRS_VCAT',
    required: true,
    type: 'CHOICE_MULTI',
    visibleIf: "{ISSUES} = 'REPAIRS'",
    choices: [
      { value: 'Landlord', text: 'I told the landlord verbally' },
      { value: 'Breaches', text: "I've issued formal notices of breaches" },
      { value: 'CAV', text: "I've applied to CAV for a report" },
      { value: 'APPLIED_VCAT', text: "I've applied to VCAT" },
      { value: 'GOTTEN_VCAT', text: "I've already gotten a VCAT order" },
    ],
    title: 'Have you done any of the following?',
    description:
      'Please select all that apply. CAV is Consumer Affairs Victoria; VCAT is the Victorian Civil and Administrative Tribunal.',
  },
  {
    name: 'REPAIRS_APPLIED_VCAT',
    required: true,
    type: 'CHOICE_SINGLE',
    visibleIf:
      "{ISSUES} = 'REPAIRS' and {REPAIRS_VCAT} contains 'APPLIED_VCAT'",
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
    title:
      'Our Repairs service focuses on helping renters write a formal compliance request to their real estate agent and/or rental provider. Due to limited capacity, we can only provide support once the matter is at VCAT stage by providing you with a self-representation guide. We cannot represent you at VCAT.',
    description: 'Would you still like to continue?',
  },
]
