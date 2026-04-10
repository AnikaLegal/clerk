import * as Yup from 'yup'

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

const required = 'This field is required.'

export const UsersInviteSchema = Yup.object().shape({
  users: Yup.array().of(Yup.string()).min(1, required).required(required),
  groups: Yup.array().of(Yup.string()).min(1, required).required(required),
})
