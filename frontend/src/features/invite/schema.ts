import * as Yup from 'yup'

Yup.setLocale({ mixed: { required: 'This field is required.' } })

export type UserInfo = {
  email: string
  first_name: string
  last_name: string
}

export type UsersCreate = {
  users: UserInfo[]
  groups: string[]
}

export type UsersInvite = {
  users: string[]
  groups: string[]
}

export const UsersInviteSchema = Yup.object().shape({
  users: Yup.array().of(Yup.string()).required(),
  groups: Yup.array().of(Yup.string()).required(),
})
