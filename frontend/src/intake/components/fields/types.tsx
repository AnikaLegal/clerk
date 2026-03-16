import type { Field, Upload, Data } from 'intake/types'

export type FormFieldProps = {
  onNext: (e: any) => void
  onSkip: (e: any) => void
  onChange: (any) => void
  onUpload?: (File) => Promise<Upload>
  field: Field
  data: Data
  value: any
  children: any
}
