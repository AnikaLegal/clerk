import api, {
  ServiceCreate,
  useAppDispatch,
  useCreateCaseServiceMutation,
} from 'api'
import { Formik, FormikHelpers, useFormikContext } from 'formik'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { Button, Form, Header, Segment } from 'semantic-ui-react'
import { CaseDetailFormProps, CaseFormServiceChoices } from 'types/case'
import { choiceToOptions, filterEmpty, getAPIFormErrors } from 'utils'
import {
  DateInputField,
  DropdownField,
  InputField,
  RichTextAreaField,
} from './formik'

export enum ServiceCategory {
  Discrete = 'DISCRETE',
  Ongoing = 'ONGOING',
}

export const ServiceForm = ({
  issue,
  onCancel,
  choices,
}: CaseDetailFormProps) => {
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
              <FormikServiceFields choices={choices.service} />
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

export const FormikServiceFields = ({
  choices,
}: {
  choices: CaseFormServiceChoices
}) => {
  const [category, setCategory] = useState<string>()
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
        options={choiceToOptions(choices.category)}
        onChange={onCategoryChange}
      />
      {category && (
        <>
          {category == ServiceCategory.Discrete ? (
            <FormikDiscreteServiceFields choices={choices} />
          ) : (
            <FormikOngoingServiceFields choices={choices} />
          )}
        </>
      )}
    </>
  )
}

export const FormikDiscreteServiceFields = ({
  choices,
}: {
  choices: CaseFormServiceChoices
}) => {
  const { values } = useFormikContext<ServiceCreate>()

  return (
    <>
      <DropdownField
        required
        name="type"
        label="Type"
        placeholder="Select the service type"
        options={choiceToOptions(
          choices['type_' + values.category.toUpperCase()]
        )}
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

export const FormikOngoingServiceFields = ({
  choices,
}: {
  choices: CaseFormServiceChoices
}) => {
  const { values } = useFormikContext<ServiceCreate>()

  return (
    <>
      <DropdownField
        required
        name="type"
        label="Type"
        placeholder="Select the service type"
        options={choiceToOptions(
          choices['type_' + values.category.toUpperCase()]
        )}
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
