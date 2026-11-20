import * as Yup from 'yup'

export type CallbackFormValues = {
  caller_name: string
  caller_email: string
  purpose: string
  summary: string
  action_items: string
}

export const CallbackSchema: Yup.ObjectSchema<CallbackFormValues> =
  Yup.object().shape({
    caller_name: Yup.string().max(255).defined(),
    caller_email: Yup.string()
      .email('Enter a valid email address.')
      .max(255)
      .defined(),
    purpose: Yup.string().defined(),
    summary: Yup.string().defined(),
    action_items: Yup.string().defined(),
  })

export type PersonDetails = { name: string; email: string }

// A contact typed both in, so neither can be cleared; a call's are optional.
export const personSchema = (isRequired: boolean) => {
  const name = Yup.string().max(255).defined()
  const email = Yup.string()
    .email('Enter a valid email address.')
    .max(255)
    .defined()
  return Yup.object({
    name: isRequired ? name.required('Enter a name.') : name,
    email: isRequired ? email.required('Enter an email address.') : email,
  }) as Yup.ObjectSchema<PersonDetails>
}
