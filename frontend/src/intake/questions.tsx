import React from 'react'
import moment from 'moment'

import { Field, Data, Submission } from 'intake/types'
import { FIELD_TYPES, ROUTES, LINKS } from 'intake/consts'
import { storeFormData } from 'intake/utils'
import { Icon } from 'intake/design'
import { api } from 'api'

const isManagerAgent = (data: Data) => data.PROPERTY_MANAGER_IS_AGENT
const isManagerLandlord = (data: Data) => !data.PROPERTY_MANAGER_IS_AGENT
const updateSupportWorker = (data: Data) => data.SUPPORT_WORKER_UPDATED

export const STAGES = [
  'Eligbility',
  'Your Client',
  'About You',
  'Tenancy',
  'Landlord',
  'Final Details',
]

export const QUESTIONS: Field[] = [
  // Eligibility stage
  {
    name: 'EXPECTATION_MANAGEMENT',
    stage: 0,
    required: true,
    type: FIELD_TYPES.CHOICE_SINGLE,
    effect: async (data: Data) => {
      if (!data.EXPECTATION_MANAGEMENT) {
        return ROUTES.INELIGIBLE.NO_TENANCY_YET
      }
    },
    choices: [
      { label: 'Yes', value: true },
      { label: 'No', value: false },
    ],
    Prompt: (
      <span>
        Our Service focuses on helping renters under their rights and duties as
        they enter new tenancy arrangements. If the renter does not end up
        signing the rental agreement, we will not be able to assist.
      </span>
    ),
    Help: (
      <span>
        <strong>Would you like to continue? </strong>
      </span>
    ),
  },
  {
    name: 'ELIGIBILITY_INTRO',
    stage: 0,
    required: true,
    type: FIELD_TYPES.DISPLAY,
    Prompt: (
      <span>
        We know you're pressed for time! Before we ask you questions about your
        client's matter, we need to check they're eligible for our service.
      </span>
    ),
    button: { text: 'Continue', Icon: null },
  },
  {
    name: 'CLIENT_RELATIONSHIP',
    stage: 0,
    required: true,
    type: FIELD_TYPES.CHOICE_SINGLE,
    effect: async (data: Data) => {
      if (data.CLIENT_RELATIONSHIP !== 'SOCIAL_WORK_CLIENT') {
        return ROUTES.INELIGIBLE.NOT_SOCIAL_WORK_CLIENT
      }
    },
    choices: [
      { label: 'Social work client', value: 'SOCIAL_WORK_CLIENT' },
      { label: 'Family or friend', value: 'FAMILY_OR_FRIEND' },
      { label: 'Other', value: 'OTHER' },
    ],
    Prompt: (
      <span>
        What is your relationship with the person you're trying to refer?
      </span>
    ),
  },

  {
    name: 'START_DATE',
    stage: 0,
    required: true,
    type: FIELD_TYPES.DATE,
    Prompt: <span>When is/was the renter's move-in date?</span>,
    effect: async (data: Data) => {
      const startDate = moment(data.START_DATE)
      const now = moment()
      const daysSinceStartDate =
        Math.abs((startDate as any) - (now as any)) / 3600 / 24 / 1000
      if (daysSinceStartDate > 21) {
        return ROUTES.INELIGIBLE.TENANCY_TOO_LATE
      }
    },
  },

  {
    name: 'ELIGIBILITY_SKIPPABLE_INTRO',
    stage: 0,
    required: true,
    type: FIELD_TYPES.DISPLAY,
    Prompt: (
      <span>
        If your client is eligible for <strong>your</strong> help, they will
        fall within <strong>our</strong> means test. However, if you have time,
        we'd appreciate if you could tell us a bit more about your client's
        circumstances. Feel free to skip to the next part if you're pressed for
        time.
      </span>
    ),
    button: { text: 'Continue', Icon: null },
  },
  {
    name: 'NUMBER_OF_DEPENDENTS',
    stage: 0,
    required: false,
    type: FIELD_TYPES.NUMBER,
    Prompt: <span>How many dependents does your client have?</span>,
  },
  {
    name: 'WEEKLY_HOUSEHOLD_INCOME',
    stage: 0,
    required: false,
    type: FIELD_TYPES.NUMBER,
    Prompt: <span>What is your client's weekly household income?</span>,
  },
  {
    name: 'ELIGIBILITY_CIRCUMSTANCES',
    stage: 0,
    required: false,
    type: FIELD_TYPES.CHOICE_MULTI,
    skipText: 'None of the above apply',
    Prompt: <span>Do any of the following apply to your client?</span>,
    choices: [
      {
        label: 'Lives in public housing or community housing',
        value: 'HOUSING',
      },
      { label: 'Has a mental illness', value: 'MENTAL_ILLNESS' },
      {
        label: 'Has a intellectual disability',
        value: 'INTELLECTUAL_DISABILITY',
      },
      { label: 'Has a physical disability', value: 'PHYSICAL_DISABILITY' },
      {
        label:
          'On one of the following visa types: Student Visa, Seasonal Worker Visa, Temporary Protection Visa, Safe Haven Enterprise Visa, Permanent Protection Visa, or Bridging Visa awaiting processing of one of the above visa types.',
        value: 'VISA',
      },
      {
        label: 'Is currently/recently experiencing family violence',
        value: 'FAMILY_VIOLENCE',
      },
      {
        label:
          'Is experiencing an unexpected circumstance which has impacted on your current situation i.e., loss of job.',
        value: 'UNEXPECTED_CIRCUMSTANCE',
      },
      {
        label: 'Has experienced substance abuse',
        value: 'SUBSTANCE_ABUSE',
      },
      {
        label: 'Iidentifies as an Aboriginal or Torres Strait Islander person',
        value: 'ABORIGINAL_OR_TORRES_STRAIT',
      },
      {
        label: 'Is renting in a remote or regional location',
        value: 'RENTING',
      },
      {
        label: 'Is struggling to pay bills, repayments or insurance premiums',
        value: 'STRUGGLING',
      },
    ],
  },
  // Client stage
  {
    name: 'CLIENT_INTRO',
    stage: 1,
    required: true,
    type: FIELD_TYPES.DISPLAY,
    Prompt: (
      <span>
        We are going to ask you some questions about you, your client, and how
        you would like us to contact you and the client
      </span>
    ),
    button: { text: 'Continue', Icon: null },
  },
  {
    name: 'FIRST_NAME',
    stage: 1,
    required: true,
    type: FIELD_TYPES.TEXT,
    Prompt: (
      <span>
        What's your client's <strong>first name?</strong>
      </span>
    ),
  },
  {
    name: 'LAST_NAME',
    stage: 1,
    required: true,
    type: FIELD_TYPES.TEXT,
    Prompt: (
      <span>
        And their <strong>last name?</strong>
      </span>
    ),
  },
  {
    name: 'EMAIL',
    stage: 1,
    required: true,
    type: FIELD_TYPES.EMAIL,
    Prompt: (
      <span>
        What <strong>email address</strong> can we reach them at?
      </span>
    ),
    Help: (
      <span>
        We may use this to contact the renter after you complete this
        questionnaire, if that is your preference.
      </span>
    ),
  },
  {
    name: 'PHONE',
    stage: 1,
    required: true,
    type: FIELD_TYPES.PHONE,
    Prompt: (
      <span>
        What is the best <strong>phone number</strong> to contact them on?
      </span>
    ),
    Help: (
      <span>
        We may use this to contact the renter after you complete this
        questionnaire, if that is your preference.
      </span>
    ),
  },
  // SUPPORT WORKER PAGE
  {
    name: 'SUPPORT_WORKER_NAME',
    stage: 2,
    required: true,
    type: FIELD_TYPES.TEXT,

    Prompt: (
      <span>
        What's your <strong>full name?</strong>
      </span>
    ),
  },
  {
    name: 'SUPPORT_WORKER_UPDATED',
    stage: 2,
    required: true,
    type: FIELD_TYPES.CHOICE_SINGLE,
    choices: [
      { label: 'Yes', value: true },
      { label: 'No', value: false },
    ],
    Prompt: (
      <span>
        Would you like to stay updated on how we assist the renter once this
        matter is submitted?
      </span>
    ),
  },
  {
    name: 'SUPPORT_WORKER_EMAIL',
    stage: 2,
    required: true,
    askCondition: updateSupportWorker,
    type: FIELD_TYPES.EMAIL,
    Prompt: (
      <span>
        What <strong>email address</strong> can we reach you at?
      </span>
    ),
  },
  {
    name: 'SUPPORT_WORKER_PHONE',
    stage: 2,
    required: true,
    askCondition: updateSupportWorker,
    type: FIELD_TYPES.PHONE,
    Prompt: (
      <span>
        What is the best <strong>phone number</strong> to contact you on?
      </span>
    ),
  },
  {
    name: 'SUPPORT_WORKER_CONTACT_PREFERENCE',
    stage: 2,
    required: true,
    askCondition: updateSupportWorker,
    type: FIELD_TYPES.CHOICE_SINGLE,
    choices: [
      {
        label: 'Contact me directly instead of the renter',
        value: 'DIRECT_ONLY',
      },
      {
        label: 'Contact the renter directly but copy me into every interaction',
        value: 'COPY_ME_IN',
      },
      {
        label: 'Contact the renter directly but give me a fortnightly update',
        value: 'PERIODIC_UPDATE',
      },
      {
        label:
          'Contact the renter directly and give me an update only once the matter is finalised. ',
        value: 'FINAL_UPDATE',
      },
      {
        label:
          "Contact the renter directly but you may contact me if you can't contact the renter.",
        value: 'RENTER_MIA',
      },
    ],
    Prompt: (
      <span>
        What is your contact preference for staying updated on this matter?
      </span>
    ),
  },
  {
    name: 'HOUSING_SERVICE_REFERRER',
    stage: 2,
    required: true,
    type: FIELD_TYPES.CHOICE_SINGLE,
    Prompt: <span>What agency do you work for?</span>,
    choices: [
      {
        label: 'Launch Housing',
        value: 'Launch Housing',
      },
      {
        label: 'Other',
        value: 'Other',
      },
    ],
  },
  {
    name: 'SUPPORT_WORKER_AUTHORITY_UPLOAD',
    stage: 2,
    required: false,
    type: FIELD_TYPES.UPLOAD,
    Prompt: (
      <span>
        Please upload an authority form signed by the renter authorising to
        speak with you about their matter.
      </span>
    ),
    Help: (
      <span>
        Please skip this upload if you don't have an authority form readily
        available. We can obtain one after the matter is submitted.
      </span>
    ),
  },
  // Tenancy stage
  {
    name: 'TENANCY_INTRO',
    stage: 3,
    required: true,
    type: FIELD_TYPES.DISPLAY,
    Prompt: (
      <span>
        We are going to ask a few more questions about the renter's tenancy to
        help us understand their situation.
      </span>
    ),
    button: { text: 'Continue', Icon: null },
  },
  {
    name: 'RENTAL_CIRCUMSTANCES',
    stage: 3,
    required: true,
    Prompt: <span>Who is the renter renting with?</span>,
    type: FIELD_TYPES.CHOICE_SINGLE,
    choices: [
      { label: 'Renting by themselves', value: 'SOLO' },
      { label: 'Renting with flatmates', value: 'FLATMATES' },
      { label: 'Renting with partner', value: 'PARTNER' },
      { label: 'Renting with family / children', value: 'FAMILY' },
      { label: 'Other', value: 'OTHER' },
    ],
  },
  {
    name: 'SUBURB',
    stage: 3,
    required: true,
    type: FIELD_TYPES.TEXT,
    Prompt: <span>What suburb is the new tenancy in?</span>,
  },
  {
    name: 'POSTCODE',
    stage: 3,
    required: true,
    type: FIELD_TYPES.NUMBER,
    Prompt: <span>What the new tenancy's postcode?</span>,
  },
  {
    name: 'ADDRESS',
    stage: 3,
    required: true,
    type: FIELD_TYPES.TEXT,
    Prompt: <span>What is the new tenancy's street address?</span>,
  },
  {
    name: 'TENANCY_DOCUMENTS_UPLOAD',
    stage: 3,
    required: false,
    type: FIELD_TYPES.UPLOAD,
    Prompt: (
      <span>
        Please upload any of the following documents if you have them handy.
      </span>
    ),
    Help: (
      <span>
        Rental Agreement, Incoming Conditions Report, Confirmation of Key
        Provision, or any other documents relating to the new tenancy.
      </span>
    ),
  },
  // Landord stage
  {
    name: 'PROPERTY_MANAGER_INTRO',
    stage: 4,
    required: true,
    type: FIELD_TYPES.DISPLAY,
    Prompt: (
      <span>
        Almost done! Now just a few questions about the tenancy's landlord.
      </span>
    ),
    Help: (
      <span>
        We use this information to run a conflict check and to help us write
        letters for you. We will <strong>not</strong> contact your landlord
        without your permission.
      </span>
    ),
    button: { text: 'Continue', Icon: null },
  },
  {
    name: 'PROPERTY_MANAGER_IS_AGENT',
    stage: 4,
    required: true,
    type: FIELD_TYPES.CHOICE_SINGLE,
    choices: [
      { label: 'Yes', value: true },
      { label: 'No', value: false },
    ],
    Prompt: (
      <span>
        Does the landlord use a <strong>real estate agent</strong> to manage the
        property?
      </span>
    ),
  },
  {
    name: 'AGENT_NAME',
    stage: 4,
    askCondition: isManagerAgent,
    required: true,
    type: FIELD_TYPES.TEXT,
    Prompt: <span>What is the landlord's agent's full name?</span>,
  },
  {
    name: 'AGENT_ADDRESS',
    stage: 4,
    askCondition: isManagerAgent,
    required: false,
    type: FIELD_TYPES.TEXT,
    Prompt: <span>What is the landlord's agent's address?</span>,
  },
  {
    name: 'AGENT_EMAIL',
    stage: 4,
    askCondition: isManagerAgent,
    required: false,
    type: FIELD_TYPES.EMAIL,
    Prompt: <span>What is the landlord's agent's email?</span>,
  },
  {
    name: 'AGENT_PHONE',
    stage: 4,
    askCondition: isManagerAgent,
    required: false,
    type: FIELD_TYPES.PHONE,
    Prompt: <span>What is the landlord's agent's phone number?</span>,
  },
  {
    stage: 4,
    name: 'LANDLORD_NAME',
    askCondition: isManagerLandlord,
    required: true,
    type: FIELD_TYPES.TEXT,
    Prompt: <span>What is the landlord's full name?</span>,
  },
  {
    name: 'LANDLORD_ADDRESS',
    stage: 4,
    askCondition: isManagerLandlord,
    required: false,
    type: FIELD_TYPES.TEXT,
    Prompt: <span>What is the landlord's address?</span>,
  },
  {
    name: 'LANDLORD_EMAIL',
    stage: 4,
    askCondition: isManagerLandlord,
    required: false,
    type: FIELD_TYPES.EMAIL,
    Prompt: <span>What is the landlord's email?</span>,
  },
  {
    name: 'LANDLORD_PHONE',
    stage: 4,
    askCondition: isManagerLandlord,
    required: false,
    type: FIELD_TYPES.PHONE,
    Prompt: <span>What is the landlord's phone number?</span>,
  },
  // Impact
  {
    name: 'IMPACT_INTRO',
    stage: 5,
    required: true,
    type: FIELD_TYPES.DISPLAY,
    Prompt: (
      <span>
        Great job. That is all the questions we have about the landlord.
        Finally, we just need a few final details about your client.
      </span>
    ),
    Help: (
      <span>
        These details will help us to better understand who your client is.
      </span>
    ),
    button: { text: 'Continue', Icon: null },
  },
  {
    name: 'DOB',
    stage: 5,
    required: true,
    type: FIELD_TYPES.DATE,
    Prompt: <span>What is the renter's date of birth?</span>,
  },
  {
    name: 'GENDER',
    stage: 5,
    required: true,
    type: FIELD_TYPES.CHOICE_SINGLE_TEXT,
    choices: [
      { label: 'Male', value: 'MALE' },
      { label: 'Female', value: 'FEMALE' },
      { label: 'Genderqueer or non-binary', value: 'GENDERQUEER' },
      { label: 'Prefer not to say', value: 'OMITTED' },
    ],
    placeholderText: 'Prefer to self-describe',
    Prompt: <span>What gender does the renter identify as?</span>,
  },
  {
    name: 'IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER',
    stage: 5,
    required: true,
    type: FIELD_TYPES.CHOICE_SINGLE,
    choices: [
      { label: 'Yes', value: true },
      { label: 'No', value: false },
    ],
    Prompt: (
      <span>Is the renter of Aboriginal or Torres Strait Islander origin?</span>
    ),
  },
  {
    name: 'CAN_SPEAK_NON_ENGLISH',
    stage: 5,
    required: true,
    type: FIELD_TYPES.CHOICE_SINGLE,
    choices: [
      { label: 'Yes', value: true },
      { label: 'No', value: false },
    ],
    Prompt: (
      <span>
        Does the renter speak a <strong>first</strong> language other than
        English?
      </span>
    ),
  },
  {
    name: 'INTERPRETER',
    stage: 5,
    required: true,
    type: FIELD_TYPES.CHOICE_SINGLE,
    Prompt: <span>Does the renter need an interpreter?</span>,
    askCondition: (data) => data.CAN_SPEAK_NON_ENGLISH,
    choices: [
      { label: 'Yes', value: true },
      { label: 'No', value: false },
    ],
  },
  {
    name: 'FIRST_LANGUAGE',
    stage: 5,
    required: true,
    type: FIELD_TYPES.TEXT,
    Prompt: (
      <span>
        What is rge renter's <strong>preferred</strong> language other than
        English?
      </span>
    ),
    askCondition: (data) => data.CAN_SPEAK_NON_ENGLISH,
  },
  {
    name: 'CENTRELINK_SUPPORT',
    stage: 6,
    required: true,
    type: FIELD_TYPES.CHOICE_SINGLE,
    choices: [
      { label: 'Yes', value: true },
      { label: 'No', value: false },
    ],
    Prompt: <span>Is your client on government support?</span>,
  },
  {
    name: 'WORK_OR_STUDY_CIRCUMSTANCES',
    stage: 5,
    required: true,
    Prompt: (
      <span>Which best describes the renter's work or study situation?</span>
    ),
    type: FIELD_TYPES.CHOICE_SINGLE,
    choices: [
      {
        label: 'Working part time or casually',
        value: 'WORKING_PART_TIME',
      },
      { label: 'Working full time', value: 'WORKING_FULL_TIME' },
      { label: 'Student', value: 'STUDENT' },
      { label: 'Apprentice or trainee', value: 'APPRENTICE' },
      { label: 'Looking for work', value: 'LOOKING_FOR_WORK' },
      {
        label: 'Income reduced due to COVID-19',
        value: 'INCOME_REDUCED_COVID',
      },
      { label: 'Retired', value: 'RETIRED' },
      { label: 'Full time parent', value: 'PARENT' },
      { label: 'Currently unemployed', value: 'UNEMPLOYED' },
      { label: 'Not looking for work', value: 'NOT_LOOKING_FOR_WORK' },
      { label: 'None of the above', value: null },
    ],
  },
  {
    name: 'SUBMIT',
    required: true,
    stage: 5,
    type: FIELD_TYPES.DISPLAY,
    Prompt: <span>That's it! You can now submit this case to Anika.</span>,
    Help: (
      <span>
        By submitting this form, you are agreeing to our{' '}
        <a href={LINKS.PRIVACY_POLICY}>Privacy Policy</a>,{' '}
        <a href={LINKS.COLLECTIONS_STATEMENT}>Collections Statement</a> and
        website <a href={LINKS.TERMS_OF_USE}>Terms of Use</a>.
      </span>
    ),
    button: {
      text: 'Confirm',
      Icon: Icon.Tick,
    },
    effect: async (data: Data) => {
      const finalData = { ...data }
      // Set all unasked questions to null.
      for (let q of QUESTIONS) {
        const isUndef = typeof data[q.name] === 'undefined'
        const isFailCondition = q.askCondition && !q.askCondition(data)
        if (isUndef || isFailCondition) {
          finalData[q.name] = null
        }
      }
      console.log('Submitting data:', finalData)
      const subId = data['id']
      let sub: Submission | undefined
      if (subId) {
        // We have already created this submission
        const resp = await api.intake.submission.update(subId, finalData)
        sub = resp.data
      } else {
        // This is a new submission
        const resp = await api.intake.submission.create(finalData)
        sub = resp.data
      }
      await api.intake.submission.submit(sub.id)
      // Wipe stored data.
      storeFormData('')
      return ROUTES.SUBMITTED
    },
  },
]
