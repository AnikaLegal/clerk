import { Dispatch, SetStateAction } from 'react'

export type ModelId = string | number
export type SetModel<Type extends ModelType> = Dispatch<SetStateAction<Type>>

export interface Model {
  [fieldName: string]: any
}
export interface ModelType {
  id: ModelId
}
export interface UpdateModel<Type extends ModelType> {
  (values: Model): Promise<Type>
}

export interface ModelChoices {
  [fieldName: string]: [string, string][]
}

export interface UserPermission {
  is_admin: boolean
  is_admin_or_better: boolean
  is_coordinator: boolean
  is_coordinator_or_better: boolean
  is_paralegal: boolean
  is_paralegal_or_better: boolean
}

