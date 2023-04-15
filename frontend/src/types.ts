type TextChoiceField = {
  display: string
  value: string
  choices: string[]
}

export type CreatePerson = {
  full_name: string
  email: string
  address: string
  phone_number: string
  support_contact_preferences: string
}

export type Person = {
  id: number
  full_name: string
  email: string
  address: string
  phone_number: string
  url: string
  support_contact_preferences: TextChoiceField
}
