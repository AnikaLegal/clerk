import { IntakeQuestion } from '../../form/types'
import { LINKS } from '../../consts'
import noticeToVacatePdf from '../../assets/notice-to-vacate-example.pdf'

export const EVICTION_RETALIATORY_QUESTIONS: IntakeQuestion[] = [
  {
    name: 'EVICTION_RETALIATORY_INTRO',
    required: false,
    type: 'DISPLAY',
    visibleIf: "{ISSUES} = 'EVICTION_RETALIATORY'",
    html: `<h2>Retaliatory Eviction</h2><p>Anika Legal can help you negotiate with your landlord, and self-represent at VCAT.</p><p>Please be aware we cannot represent you at VCAT. If you need representation, you may wish to contact your <a target="_blank" href="${LINKS.VIC_LEGAL_AID}">local community legal centres</a> who will be better placed to look into your matter.</p><p>If you would like us to support you to self-represent at VCAT, please continue and make sure you have your Notice to Vacate with you.</p>`,
  },
  {
    name: 'EVICTION_RETALIATORY_IS_ALREADY_REMOVED',
    required: true,
    type: 'CHOICE_SINGLE',
    visibleIf: "{ISSUES} = 'EVICTION_RETALIATORY'",
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
    title: 'Have you been removed from your home?',
  },
  {
    name: 'EVICTION_RETALIATORY_HAS_NOTICE',
    required: true,
    type: 'CHOICE_SINGLE',
    visibleIf: "{ISSUES} = 'EVICTION_RETALIATORY'",
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
    title:
      'Have you received a Notice to Vacate from your landlord or your real estate agent?',
    description: `It's a specific kind of legal document that <a target="_blank" href="${noticeToVacatePdf}">looks like this</a>.`,
  },
  {
    name: 'EVICTION_RETALIATORY_DOCUMENTS_UPLOAD',
    required: true,
    type: 'UPLOAD',
    visibleIf: "{ISSUES} = 'EVICTION_RETALIATORY'",
    title:
      'Please upload a copy of the Notice to Vacate that your landlord or agent has given you.',
    description:
      'If you have received multiple Notices to Vacate, please upload all that have not been withdrawn. Please also upload all supporting documents attached to the Notice to Vacate.',
  },
  {
    name: 'EVICTION_RETALIATORY_DATE_RECEIVED_NTV',
    required: true,
    type: 'DATE',
    visibleIf: "{ISSUES} = 'EVICTION_RETALIATORY'",
    title: 'What date did you receive the Notice to Vacate?',
  },
  {
    name: 'EVICTION_RETALIATORY_NTV_TYPE',
    required: true,
    type: 'CHOICE_SINGLE',
    colCount: 2,
    visibleIf: "{ISSUES} = 'EVICTION_RETALIATORY'",
    choices: [
      { value: '91ZM - Arrears', text: 'You owe at least two weeks rent' },
      {
        value: '91ZX - Repairs',
        text: 'Rental Provider intends to repair or renovate the Property',
      },
      {
        value: '91ZZA - Moving in',
        text: 'Rental Provider or their family intend to move in',
      },
      {
        value: '91ZZB - Selling',
        text: 'Rental Provider intends to sell the Property',
      },
      {
        value: '91ZZD - DA - End of lease',
        text: 'Your lease is ending and the Rental Provider does not want to renew it',
      },
      {
        value: '91ZW - Principal place of residence',
        text: 'Your lease is ending and the Rental Provider wants to move back in',
      },
      {
        value: '91ZY - Demolition',
        text: 'Rental Provider intends to demolish the Property',
      },
      {
        value: '91ZL - Uninhabitable',
        text: 'Rental Provider has deemed the Property unfit for habitation',
      },
      {
        value: '91ZK - Threats and intimidation',
        text: 'Rental Provider claims you have threatened or intimidated them or their staff',
      },
      {
        value: '91ZI - Damage',
        text: 'Rental Provider claims you have damaged the Property',
      },
      {
        value: '91ZJ - Danger',
        text: 'Rental Provider claims you have endangered safety',
      },
      {
        value: '91ZP - Breaches',
        text: 'Rental Provider claims you have breached the lease or law',
      },
      {
        value: '91ZQ - Illegal use',
        text: 'Rental Provider claims you have used the Property for illegal purposes',
      },
      {
        value: '91ZZ - Business',
        text: 'Rental Provider would like to use the Property for their business',
      },
      { value: 'Unsure', text: "I'm not sure" },
    ],
    title: 'What is the reason given on the Notice to Vacate?',
    description:
      "If you've received multiple Notices to Vacate, please select the reason on the Notice to Vacate with the earliest Termination Date.",
  },
  {
    name: 'EVICTION_RETALIATORY_RETALIATORY_REASON',
    required: true,
    type: 'CHOICE_MULTI',
    colCount: 2,
    visibleIf: "{ISSUES} = 'EVICTION_RETALIATORY'",
    choices: [
      { value: 'Repairs', text: 'I asked for repairs' },
      { value: 'Modifications', text: 'I asked for modifications' },
      { value: 'Damage', text: 'I reported damage to the property' },
      { value: 'Rent Increase', text: 'I challenged a rent increase' },
      {
        value: 'No notice access',
        text: 'I asked the rental provider or their agent to not enter the property without notice',
      },
      { value: 'Other', text: 'Something else' },
    ],
    title: 'Why do you believe that the Notice to Vacate is retaliatory?',
    description: 'Please select all that apply.',
  },
  {
    name: 'EVICTION_RETALIATORY_RETALIATORY_REASON_OTHER',
    required: true,
    type: 'TEXT',
    multiline: true,
    visibleIf:
      "{ISSUES} = 'EVICTION_RETALIATORY' and {EVICTION_RETALIATORY_RETALIATORY_REASON} contains 'Other'",
    title:
      'What are the other reasons that you believe that the Notice to Vacate is retaliatory?',
  },
  {
    name: 'EVICTION_RETALIATORY_VCAT_HEARING',
    required: true,
    type: 'CHOICE_SINGLE',
    visibleIf: "{ISSUES} = 'EVICTION_RETALIATORY'",
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
    title: 'Have you been given a date for an evictions hearing at VCAT?',
  },
  {
    name: 'EVICTION_RETALIATORY_VCAT_HEARING_DATE',
    required: true,
    type: 'DATE',
    visibleIf:
      "{ISSUES} = 'EVICTION_RETALIATORY' and {EVICTION_RETALIATORY_VCAT_HEARING} = true",
    title: 'What date is the VCAT hearing?',
  },
  {
    name: 'EVICTION_RETALIATORY_TERMINATION_DATE',
    required: true,
    type: 'DATE',
    visibleIf: "{ISSUES} = 'EVICTION_RETALIATORY'",
    title: 'What is the date that you are required to vacate the property?',
    description:
      'You will be able to find this information on the Notice to Vacate, under "Termination Date".',
  },
]
