//@flow
import * as React from 'react'
import type { Data } from './core'

export type FieldType =
  | 'TEXT'
  | 'EMAIL'
  | 'DATE'
  | 'CHOICE_SINGLE'
  | 'CHOICE_SINGLE_TEXT'
  | 'CHOICE_MULTI'
  | 'UPLOAD'
  | 'DISPLAY'
  | 'PHONE'
  | 'NUMBER'

export type Field = {
  type: FieldType
  stage: number
  name: string
  effect?: (data: Data) => Promise<string | void>
  askCondition?: (data: Data) => boolean
  skipText?: string
  placeholderText?: string
  required: boolean
  Prompt: React.ReactElement<'span'>
  Help?: React.ReactElement<'span'>
  choices?: Array<{ label: string; value: string | boolean | null }>
  button?: {
    text: string
    Icon: any
  }
}
