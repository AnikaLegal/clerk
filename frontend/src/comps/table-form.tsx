import React, { Dispatch, SetStateAction, useState } from 'react'
import { Button, Table } from 'semantic-ui-react'
import { Formik } from 'formik'
import { useSnackbar } from 'notistack'

import { markdownToHtml } from 'utils'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'
import {
  AutoForm,
  getModelChoices,
  getModelInitialValues,
  FormField,
} from 'comps/auto-form'
import { FIELD_TYPES } from './field-component'

import * as Yup from 'yup'

interface TableFormProps<ModelType extends { id: string | number }> {
  fields: FormField[]
  schema: Yup.AnySchema
  model: ModelType
  setModel: Dispatch<SetStateAction<ModelType>>
  modelName: string
  onUpdate: (
    id: string | number,
    values: { [fieldName: string]: unknown }
  ) => Promise<ModelType>
}

// Wrapper around AutoForm for updating a model or displating a table.
export const TableForm = <ModelType extends { id: string | number }>({
  fields,
  schema,
  model,
  setModel,
  modelName,
  onUpdate,
}: TableFormProps<ModelType>) => {
  const { enqueueSnackbar } = useSnackbar()
  const [isEditMode, setEditMode] = useState(false)
  const toggleEditMode = () => setEditMode(!isEditMode)
  if (!isEditMode) {
    return (
      <>
        <FieldTable fields={fields} model={model} />
        <Button onClick={toggleEditMode}>Edit</Button>
      </>
    )
  }
  return (
    <Formik
      initialValues={getModelInitialValues(fields, model)}
      validationSchema={schema}
      onSubmit={(
        values: { [fieldName: string]: unknown },
        { setSubmitting, setErrors }: any
      ) => {
        onUpdate(model.id, values)
          .then((instance) => {
            enqueueSnackbar(`Updated ${modelName}`, { variant: 'success' })
            setModel(instance)
            toggleEditMode()
            setSubmitting(false)
          })
          .catch((err) => {
            enqueueSnackbar(
              getAPIErrorMessage(err, `Failed to update this ${modelName}`),
              {
                variant: 'error',
              }
            )
            const requestErrors = getAPIFormErrors(err)
            if (requestErrors) {
              setErrors(requestErrors)
            }
            setSubmitting(false)
          })
      }}
    >
      {(formik) => (
        <AutoForm
          fields={fields}
          choices={getModelChoices(fields, model)}
          formik={formik}
          onCancel={toggleEditMode}
          submitText="Update"
        />
      )}
    </Formik>
  )
}

const FieldTable = ({ fields, model }) => (
  <Table size="small" definition>
    <Table.Body>
      {fields.map(({ label, name, type }) => (
        <Table.Row key={label}>
          <Table.Cell width={3}>{label}</Table.Cell>
          {type === FIELD_TYPES.TEXTAREA ? (
            <td
              dangerouslySetInnerHTML={{
                __html: model[name] ? markdownToHtml(model[name]) : '-',
              }}
            />
          ) : (
            <Table.Cell>{getValueDisplay(model[name])}</Table.Cell>
          )}
        </Table.Row>
      ))}
    </Table.Body>
  </Table>
)

const getValueDisplay = (val: any): React.ReactNode => {
  const t = typeof val
  if (t === 'undefined' || val === null || val === '') {
    return '-'
  }
  if (t === 'object' && val && val.choices) {
    return val.display || '-'
  }
  if (val === false) {
    return 'No'
  }
  if (val === true) {
    return 'Yes'
  }
  return val
}
