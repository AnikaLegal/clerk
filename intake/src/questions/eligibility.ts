import { IntakeQuestion } from '../form/types'
import { LINKS } from '../consts'

export const ELIGIBILITY_QUESTIONS: IntakeQuestion[] = [
  {
    name: 'INTRO',
    required: false,
    type: 'DISPLAY',
    html: "<h2>First of all, congratulations on taking the first step in solving your rental issues</h2><p>Once you submit this form, we'll contact you in a few business days to talk about how we can help you.</p>",
  },
  {
    name: 'ISSUES',
    required: true,
    type: 'CHOICE_SINGLE',
    choices: [
      { value: 'BONDS', text: "I'm having issues with my bond" },
      { value: 'REPAIRS', text: "My landlord won't fix repairs" },
      {
        value: 'EVICTION_RETALIATORY',
        text: "I've received an eviction notice",
      },
      {
        value: 'INELIGIBLE_COMPENSATION',
        text: 'I want compensation from my landlord',
      },
    ],
    title: 'What do you need help with?',
    description: `Anika can help with <a target="_blank" href="${LINKS.BONDS_INFO}">bond recovery</a>, <a target="_blank" href="${LINKS.REPAIRS_INFO}">rental repairs</a> and <a target="_blank" href="${LINKS.EVICTION_INFO}">retaliatory evictions</a>.`,
  },
  {
    name: 'PRE_EVICTION_NOTICE',
    required: false,
    type: 'DISPLAY',
    visibleIf: "{ISSUES} = 'EVICTION_RETALIATORY'",
    html: `<h2>Anika Legal can only help you with evictions if you believe the eviction is retaliatory</h2><p>A retaliatory eviction is when your landlord tries to evict you because you stood up for your rights - for example, asking for repairs or challenging a rent increase.</p><p>If your eviction isn't retaliatory, see what <a target="_blank" href="${LINKS.VIC_LEGAL_AID}">other legal help</a> is available in your area. Otherwise please continue.</p>`,
  },
  {
    name: 'IS_VICTORIAN_TENANT',
    required: true,
    type: 'CHOICE_SINGLE',
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
    title: 'Are you renting a property in Victoria?',
  },
  {
    name: 'ELIGIBILITY_INTRO',
    required: false,
    type: 'DISPLAY',
    html: "<h2>You're in the right place</h2><p>We just need a few more details to understand your situation and how we can help.</p>",
  },
  {
    name: 'CENTRELINK_SUPPORT',
    required: true,
    type: 'CHOICE_SINGLE',
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
    title: 'Do you currently receive any government support?',
  },
  {
    name: 'ANNUAL_INCOME_RANGE',
    required: true,
    type: 'CHOICE_SINGLE',
    colCount: 2,
    visibleIf: '{CENTRELINK_SUPPORT} = false',
    choices: [
      { value: 'UNDER_40K', text: 'Under $40,000' },
      { value: 'FROM_65K_TO_89K', text: '$65,000 - $89,999' },
      { value: 'FROM_115K_TO_139K', text: '$115,000 - $139,999' },
      { value: 'OVER_155K', text: 'Over $155,000' },
      { value: 'FROM_40K_TO_64K', text: '$40,000 - $64,999' },
      { value: 'FROM_90K_TO_114K', text: '$90,000 - $114,999' },
      { value: 'FROM_140K_TO_155K', text: '$140,000 - $155,000' },
    ],
    title: "Roughly what is your household's annual income?",
  },
  {
    name: 'NUMBER_OF_DEPENDENTS',
    required: false,
    type: 'NUMBER',
    title: 'How many dependants do you have?',
    min: 0,
    skipDefault: 0,
  },
  {
    name: 'ELIGIBILITY_CIRCUMSTANCES',
    required: false,
    type: 'CHOICE_MULTI',
    colCount: 2,
    title: 'Do any of the following apply to you?',
    description:
      'This helps us prioritise support. Please select all that apply.',
    choices: [
      { value: 'STRUGGLING', text: "I'm experiencing financial stress" },
      { value: 'HOUSING', text: 'I live in public or community housing' },
      { value: 'SINGLE_PARENT', text: "I'm a single parent" },
      { value: 'PHYSICAL_DISABILITY', text: 'I have a physical disability' },
      {
        value: 'INTELLECTUAL_DISABILITY',
        text: 'I have a cognitive disability',
      },
      { value: 'MENTAL_ILLNESS', text: 'I have a mental health condition' },
      {
        value: 'FAMILY_VIOLENCE',
        text: "I'm experiencing or at risk of family violence",
      },
      { value: 'VISA', text: "I'm on a temporary or bridging visa" },
      {
        value: 'RENTING',
        text: "I'm renting in a remote or regional location",
      },
      {
        value: 'ABORIGINAL_OR_TORRES_STRAIT',
        text: 'I identify as Aboriginal or Torres Strait Islander',
      },
    ],
  },
  {
    name: 'INELIGIBLE_CHOICE',
    required: true,
    type: 'CHOICE_SINGLE',
    visibleIf:
      'meansIneligible({CENTRELINK_SUPPORT}, {ELIGIBILITY_CIRCUMSTANCES}, {ANNUAL_INCOME_RANGE}, {NUMBER_OF_DEPENDENTS})',
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
    description:
      'If you continue with our intake form, we cannot guarantee that we can assist you.',
    title:
      "It looks like you're not eligible for our service. Would you still like to continue?",
  },
  {
    name: 'ELIGIBILITY_NOTES',
    required: true,
    type: 'TEXT',
    visibleIf:
      'meansIneligible({CENTRELINK_SUPPORT}, {ELIGIBILITY_CIRCUMSTANCES}, {ANNUAL_INCOME_RANGE}, {NUMBER_OF_DEPENDENTS})',
    multiline: true,
    title:
      'So that we can assess your circumstances holistically, please tell us if you have any other special circumstances that you would like us to consider',
  },
]
