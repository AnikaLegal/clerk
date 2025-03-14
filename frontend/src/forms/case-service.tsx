import api, {
  ServiceCategory,
  ServiceCreate,
  useAppDispatch,
  useCreateCaseServiceMutation,
} from 'api'
import {
  DISCRETE_SERVICE_TYPES,
  ONGOING_SERVICE_TYPES,
  SERVICE_CATEGORIES,
} from 'consts'
import { Formik, FormikHelpers, useFormikContext } from 'formik'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { Button, Form, Header, Segment } from 'semantic-ui-react'
import { CaseDetailFormProps } from 'types'
import { filterEmpty, getAPIFormErrors } from 'utils'
import {
  DateInputField,
  DropdownField,
  InputField,
  RichTextAreaField,
} from './formik'

export const ServiceForm = ({ issue, onCancel }: CaseDetailFormProps) => {
  const [createService] = useCreateCaseServiceMutation()
  const dispatch = useAppDispatch()

  const handleSubmit = (
    values: ServiceCreate,
    { setSubmitting, setErrors }: FormikHelpers<ServiceCreate>
  ) => {
    createService({ id: issue.id, serviceCreate: filterEmpty(values) })
      .unwrap()
      .then(() => {
        /* Invalidate the case tag so that the file note that is created when a
         * service is created is displayed on the timeline */
        dispatch(api.util.invalidateTags(['CASE']))
        enqueueSnackbar('Service created', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar('Failed to create service', { variant: 'error' })
        const requestErrors = getAPIFormErrors(e)
        if (requestErrors) {
          setErrors(requestErrors)
        }
      })
      .finally(() => {
        setSubmitting(false)
      })
  }

  return (
    <Segment>
      <Header>Add a service</Header>
      <p>
        Record a unit of work to facilitate the collection of consistent and
        comparable data.
      </p>
      <Formik
        initialValues={{ started_at: '', finished_at: '' } as ServiceCreate}
        onSubmit={handleSubmit}
      >
        {({ values, handleSubmit, isSubmitting, errors }) => {
          return (
            <Form
              onSubmit={handleSubmit}
              error={Object.keys(errors).length > 0}
            >
              <FormikServiceFields />
              <div style={{ marginTop: '1rem' }}>
                <Button
                  loading={isSubmitting}
                  disabled={isSubmitting || !values.category}
                  positive
                  type="submit"
                >
                  Create service
                </Button>
                <Button disabled={isSubmitting} onClick={onCancel}>
                  Close
                </Button>
              </div>
            </Form>
          )
        }}
      </Formik>
    </Segment>
  )
}

export const FormikServiceFields = () => {
  const [category, setCategory] = useState<ServiceCategory>()
  const { setFieldValue, isSubmitting } = useFormikContext<ServiceCreate>()

  const onCategoryChange = (e, data) => {
    setCategory(data.value)
    setFieldValue('category', data.value)
    setFieldValue('type', '')
    setFieldValue('count', 1)
  }

  return (
    <>
      <DropdownField
        required
        name="category"
        label="Category"
        placeholder="Select the service category"
        loading={isSubmitting}
        options={Object.entries(SERVICE_CATEGORIES).map(([key, value]) => ({
          key: key,
          text: value,
          value: key,
        }))}
        onChange={onCategoryChange}
      />
      {category && (
        <>
          {category == 'DISCRETE' ? (
            <FormikDiscreteServiceFields />
          ) : (
            <FormikOngoingServiceFields />
          )}
        </>
      )}
    </>
  )
}

export const FormikDiscreteServiceFields = () => {
  const { values } = useFormikContext<ServiceCreate>()

  return (
    <>
      <DropdownField
        required
        name="type"
        label="Type"
        placeholder="Select the service type"
        options={Object.entries(DISCRETE_SERVICE_TYPES).map(([key, value]) => ({
          key: key,
          text: value,
          value: key,
        }))}
      />
      <DateInputField
        required
        name="started_at"
        label="Date"
        dateFormat="DD/MM/YYYY"
        autoComplete="off"
      />
      <InputField required name="count" label="Count" type="number" min="1" />
      <RichTextAreaField name="notes" label="Notes" />
    </>
  )
}

export const FormikOngoingServiceFields = () => {
  const { values } = useFormikContext<ServiceCreate>()

  return (
    <>
      <DropdownField
        required
        name="type"
        label="Type"
        placeholder="Select the service type"
        options={Object.entries(ONGOING_SERVICE_TYPES).map(([key, value]) => ({
          key: key,
          text: value,
          value: key,
        }))}
      />
      <DateInputField
        required
        name="started_at"
        label="Start date"
        dateFormat="DD/MM/YYYY"
        autoComplete="off"
      />
      <DateInputField
        name="finished_at"
        label="Finish date"
        dateFormat="DD/MM/YYYY"
        autoComplete="off"
      />
      <RichTextAreaField name="notes" label="Notes" />
    </>
  )
}
