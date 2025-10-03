import { IssueDateCreate, IssueDateHearingType, IssueDateType } from 'api'
import { CASE_DATE_HEARING_TYPES, CASE_DATE_TYPES } from 'consts'
import * as Yup from 'yup'

Yup.setLocale({ mixed: { required: 'This field is required.' } })

const Types = Object.keys(CASE_DATE_TYPES) as IssueDateType[]
const HearingTypes = Object.keys(
  CASE_DATE_HEARING_TYPES
) as IssueDateHearingType[]

export const DateSchema: Yup.ObjectSchema<IssueDateCreate> = Yup.object().shape(
  {
    issue_id: Yup.string().required(),
    type: Yup.string<IssueDateType>().oneOf(Types).required(),
    date: Yup.string().required(),
    notes: Yup.string().optional(),
    is_reviewed: Yup.boolean().optional(),
    hearing_type: Yup.string<IssueDateHearingType>()
      .oneOf(HearingTypes)
      .when('type', {
        is: (value: IssueDateType) => value === 'HEARING_LISTED',
        then: (schema) => schema.required().default(undefined),
        otherwise: (schema) => schema.optional().default(undefined),
      }),
    hearing_location: Yup.string().when('type', {
      is: (value: IssueDateType) => value === 'HEARING_LISTED',
      then: (schema) => schema.required().default(undefined),
      otherwise: (schema) => schema.optional().default(undefined),
    }),
  }
)
