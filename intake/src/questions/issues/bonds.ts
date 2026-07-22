import { IntakeQuestion } from '../../form/types'

const RTBA_LINK = 'https://rentalbonds.vic.gov.au/'
const VCAT_LINK = 'https://www.vcat.vic.gov.au/'

const REASONS = {
  DAMAGE: 'Damage',
  MONEY_OWED: 'Rent or other money owing',
  CLEANING: 'Cleaning',
  LOCKS: 'Locks and security devices',
  OTHER: 'Other reason',
}

const IS_BONDS = "{ISSUES} = 'BONDS'"
// The claim branch: only claims the landlord has actually lodged with VCAT
// continue (a "No" / "I don't know" answer exits to the bond-recovery page,
// see form/exits.ts).
const IS_BONDS_WITH_APPLICATION = `${IS_BONDS} and {BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION} = true`
const isClaimReason = (reason: string) =>
  `${IS_BONDS_WITH_APPLICATION} and {BONDS_CLAIM_REASONS} contains '${reason}'`

export const BONDS_QUESTIONS: IntakeQuestion[] = [
  {
    name: 'BONDS_INTRO',
    visibleIf: IS_BONDS,
    required: false,
    type: 'DISPLAY',
    html: '<h2>Bond recovery</h2><p>Thanks for your answers so far. We have a few questions about your bond.</p>',
  },
  {
    name: 'BONDS_MOVE_OUT_DATE',
    visibleIf: IS_BONDS,
    // Required: users who are not moving out take the dedicated "I'm not
    // moving out" button on this page (see views/FormPage.tsx), which exits to
    // the bond-recovery resources page instead of answering.
    required: true,
    type: 'DATE',
    title:
      'When was, or what will be, the date you move out of your rental property?',
  },
  {
    name: 'BOND_RTBA',
    visibleIf: IS_BONDS,
    required: true,
    type: 'CHOICE_SINGLE',
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
    description:
      'The RTBA (Residential Tenancies Bond Authority) holds Victorian rental bonds. Check your email for an RTBA bond receipt, and use it to check your bond lodgment on the RTBA website. If in doubt, call the RTBA.',
    title: `Is your bond still held by the <a target="_blank" href="${RTBA_LINK}">RTBA</a>?`,
  },
  {
    name: 'BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION',
    visibleIf: IS_BONDS,
    required: true,
    type: 'CHOICE_SINGLE',
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
      { value: "I don't know", text: "I don't know" },
    ],
    description: 'VCAT is the Victorian Civil and Administrative Tribunal.',
    title: `Has your landlord/real estate agent made an application to <a target="_blank" href="${VCAT_LINK}">VCAT</a> for your bond?`,
  },
  {
    name: 'BONDS_TENANT_HAS_RTBA_APPLICATION_COPY',
    visibleIf: IS_BONDS_WITH_APPLICATION,
    required: true,
    type: 'CHOICE_SINGLE',
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
    title: `Do you have a copy of the <a target="_blank" href="${VCAT_LINK}">VCAT</a> application?`,
  },
  {
    name: 'BONDS_RTBA_APPLICATION_UPLOAD',
    visibleIf: `${IS_BONDS_WITH_APPLICATION} and {BONDS_TENANT_HAS_RTBA_APPLICATION_COPY} = true`,
    required: false,
    type: 'UPLOAD',
    title: `Please upload the landlord/real estate agent's <a target="_blank" href="${VCAT_LINK}">VCAT</a> application.`,
  },
  {
    name: 'BONDS_CLAIM_REASONS',
    visibleIf: IS_BONDS_WITH_APPLICATION,
    required: true,
    type: 'CHOICE_MULTI',
    choices: [
      { value: REASONS.DAMAGE, text: REASONS.DAMAGE },
      { value: REASONS.MONEY_OWED, text: REASONS.MONEY_OWED },
      { value: REASONS.CLEANING, text: REASONS.CLEANING },
      { value: REASONS.LOCKS, text: REASONS.LOCKS },
      { value: REASONS.OTHER, text: REASONS.OTHER },
    ],
    title:
      'What are the reason(s) your landlord or agent is using to claim your bond?',
    description: 'Please select all that apply.',
  },
  {
    name: 'BONDS_DAMAGE_INTRO',
    visibleIf: isClaimReason(REASONS.DAMAGE),
    required: false,
    type: 'DISPLAY',
    html: "<h2>Damage to the rental property</h2><p>Let's go over the damage that your landlord is making a claim for.</p>",
  },
  {
    name: 'BONDS_DAMAGE_CLAIM_DESCRIPTION',
    visibleIf: isClaimReason(REASONS.DAMAGE),
    required: true,
    type: 'TEXT',
    multiline: true,
    title: 'Tell us more about the damage the landlord is making a claim for.',
  },
  {
    name: 'BONDS_DAMAGE_CLAIM_AMOUNT',
    visibleIf: isClaimReason(REASONS.DAMAGE),
    required: true,
    type: 'NUMBER',
    title: 'How much is the landlord claiming for damage?',
  },
  {
    name: 'BONDS_DAMAGE_CAUSED_BY_TENANT',
    visibleIf: isClaimReason(REASONS.DAMAGE),
    required: true,
    type: 'CHOICE_SINGLE',
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
    title: 'Did you cause the damage?',
  },
  {
    name: 'BONDS_DAMAGE_QUOTE_UPLOAD',
    visibleIf: `${isClaimReason(
      REASONS.DAMAGE
    )} and {BONDS_DAMAGE_CAUSED_BY_TENANT} = true`,
    required: false,
    type: 'UPLOAD',
    title:
      'If you caused the damage, have you obtained your own quote for repair? If so, please upload.',
  },
  {
    name: 'BONDS_MONEY_OWED_INTRO',
    visibleIf: isClaimReason(REASONS.MONEY_OWED),
    required: false,
    type: 'DISPLAY',
    html: "<h2>Rent or other money owing</h2><p>Let's go over the money owed that your landlord is making a claim for.</p>",
  },
  {
    name: 'BONDS_MONEY_OWED_CLAIM_DESCRIPTION',
    visibleIf: isClaimReason(REASONS.MONEY_OWED),
    required: true,
    type: 'TEXT',
    multiline: true,
    title: 'Tell us more about the money the landlord says you owe.',
  },
  {
    name: 'BONDS_MONEY_OWED_CLAIM_AMOUNT',
    visibleIf: isClaimReason(REASONS.MONEY_OWED),
    required: true,
    type: 'NUMBER',
    title: 'How much is the landlord claiming for money owing?',
  },
  {
    name: 'BONDS_MONEY_IS_OWED_BY_TENANT',
    visibleIf: isClaimReason(REASONS.MONEY_OWED),
    required: true,
    type: 'CHOICE_SINGLE',
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
    title: 'Do you owe the money the landlord is claiming?',
  },
  {
    name: 'BONDS_CLEANING_INTRO',
    visibleIf: isClaimReason(REASONS.CLEANING),
    required: false,
    type: 'DISPLAY',
    html: "<h2>Cleaning</h2><p>Let's go over the cleaning that your landlord is making a claim for.</p>",
  },
  {
    name: 'BONDS_CLEANING_CLAIM_DESCRIPTION',
    visibleIf: isClaimReason(REASONS.CLEANING),
    required: true,
    type: 'TEXT',
    multiline: true,
    title:
      'Tell us more about the cleaning costs the landlord is trying to claim.',
  },
  {
    name: 'BONDS_CLEANING_CLAIM_AMOUNT',
    visibleIf: isClaimReason(REASONS.CLEANING),
    required: true,
    type: 'NUMBER',
    title: 'How much is the landlord claiming for cleaning costs?',
  },
  {
    name: 'BONDS_CLEANING_DOCUMENT_UPLOADS',
    visibleIf: isClaimReason(REASONS.CLEANING),
    required: false,
    type: 'UPLOAD',
    // The document list lives in the description (not the title) so it renders
    // as regular supporting text and the "(optional)" title suffix stays on
    // the title sentence rather than trailing the list.
    title:
      "Please upload any of the following documents if you have them. It's okay if you don't.",
    description:
      '<ul><li>Conditions Report at the start of your tenancy</li><li>Conditions Report at the end of your tenancy</li><li>Receipt for end of lease cleaning you have already paid for</li><li>Quote for end of lease cleaning you have not yet paid for</li></ul>',
  },
  {
    name: 'BONDS_LOCKS_INTRO',
    visibleIf: isClaimReason(REASONS.LOCKS),
    required: false,
    type: 'DISPLAY',
    html: "<h2>Locks and security devices</h2><p>Let's go over the locks and security devices that your landlord is making a claim for.</p>",
  },
  {
    name: 'BONDS_LOCKS_CLAIM_AMOUNT',
    visibleIf: isClaimReason(REASONS.LOCKS),
    required: true,
    type: 'NUMBER',
    title: 'How much is the landlord claiming for locks and security devices?',
  },
  {
    name: 'BONDS_LOCKS_CHANGED_BY_TENANT',
    visibleIf: isClaimReason(REASONS.LOCKS),
    required: true,
    type: 'CHOICE_SINGLE',
    choices: [
      { value: true, text: 'Yes' },
      { value: false, text: 'No' },
    ],
    title: 'Have you altered the locks/security devices at your property?',
  },
  {
    name: 'BONDS_LOCKS_CHANGE_QUOTE',
    visibleIf: `${isClaimReason(
      REASONS.LOCKS
    )} and {BONDS_LOCKS_CHANGED_BY_TENANT} = true`,
    required: false,
    type: 'UPLOAD',
    title:
      'If you have altered the locks/security devices at your property and have obtained a quote to change it back, please upload the quote.',
  },
  {
    name: 'BONDS_OTHER_INTRO',
    visibleIf: isClaimReason(REASONS.OTHER),
    required: false,
    type: 'DISPLAY',
    html: "<h2>Other claim reasons</h2><p>Let's go over the other reasons that your landlord is making a claim.</p>",
  },
  {
    name: 'BONDS_OTHER_REASONS_DESCRIPTION',
    visibleIf: isClaimReason(REASONS.OTHER),
    required: true,
    type: 'TEXT',
    multiline: true,
    title: "What are the 'other' reasons that the landlord is claiming?",
  },
  {
    name: 'BONDS_OTHER_REASONS_AMOUNT',
    visibleIf: isClaimReason(REASONS.OTHER),
    required: true,
    type: 'NUMBER',
    title: 'How much is the landlord claiming for other reasons?',
  },
]
