import { IssueDateCreate, IssueDateType } from 'api'
import { CASE_DATE_TYPES } from 'consts'
import * as Yup from 'yup'

Yup.setLocale({ mixed: { required: 'This field is required.' } })

const Types = Object.keys(CASE_DATE_TYPES) as IssueDateType[]

export const DateSchema: Yup.ObjectSchema<IssueDateCreate> = Yup.object().shape(
  {
    issue_id: Yup.string().required(),
    type: Yup.string<IssueDateType>().oneOf(Types).required(),
    date: Yup.string().required(),
    notes: Yup.string().optional(),
    is_reviewed: Yup.boolean().optional(),
  }
)
