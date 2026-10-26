import * as Yup from 'yup'

export type UsersInvite = {
  users: string[]
  groups: string[]
  is_intern: boolean
}

const required = 'This field is required.'

export const UsersInviteSchema = Yup.object().shape({
  users: Yup.array().of(Yup.string()).min(1, required).required(required),
  groups: Yup.array().of(Yup.string()).min(1, required).required(required),
})
