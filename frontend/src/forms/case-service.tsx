import { Field, Formik, FormikHelpers, useFormikContext } from 'formik'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import {
  Button,
  Dropdown,
  Form,
  Header,
  Input,
  Message,
  Segment,
} from 'semantic-ui-react'

import { ServiceCreate, useCreateCaseServiceMutation } from 'api'
import DateInput from 'comps/date-input'
import { TextArea } from 'comps/textarea'
import {
  CaseDetailFormProps, CaseFormServiceChoices
} from 'types'
import {
  choiceToOptions,
  filterEmpty,
  getAPIErrorMessage,
  getAPIFormErrors,
} from 'utils'

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

  const handleSubmit = (
    values: ServiceCreate,
    { setSubmitting, setErrors }: FormikHelpers<ServiceCreate>
  ) => {
    createService({ id: issue.id, serviceCreate: filterEmpty(values) })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Service created', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to create service'), {
          variant: 'error',
        })
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
      <Formik initialValues={{} as ServiceCreate} onSubmit={handleSubmit}>
        {({ values, handleSubmit, isSubmitting, errors }) => {
          return (
            <Form
              onSubmit={handleSubmit}
              error={Object.keys(errors).length > 0}
            >
              <FormikServiceFields choices={choices.service} />
              <FormikServiceErrorMessages />
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
            </Form>
          )
        }}
      </Formik>
    </Segment>
  )
}

export const FormikServiceErrorMessages = () => {
  const { errors } = useFormikContext<ServiceCreate>()
  return (
    <>
      {Object.entries(errors).map(([k, v]) => (
        <Message error key={k}>
          <div className="header">{k}</div>
          <p>{v}</p>
        </Message>
      ))}
    </>
  )
}

export const FormikServiceFields = ({
  choices,
}: {
  choices: CaseFormServiceChoices
}) => {
  const [category, setCategory] = useState<string>()
  const { setFieldValue, isSubmitting } = useFormikContext<ServiceCreate>()

  return (
    <>
      <Field
        as={Dropdown}
        fluid
        selection
        name="category"
        loading={isSubmitting}
        placeholder="Service category"
        options={choiceToOptions(choices.category)}
        onChange={(e, data) => {
          setCategory(data.value)
          setFieldValue('category', data.value)
          setFieldValue('type', '')
          setFieldValue('count', 1)
        }}
        style={{ marginBottom: '1rem' }}
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
  const { setFieldValue, isSubmitting, values } =
    useFormikContext<ServiceCreate>()
  const handleChange = (e, { name, value }) => setFieldValue(name, value, false)

  return (
    <>
      <Field
        as={Dropdown}
        fluid
        selection
        name="type"
        loading={isSubmitting}
        placeholder="Service type"
        options={choiceToOptions(
          choices['type_' + values.category.toUpperCase()]
        )}
        onChange={handleChange}
      />
      <DateInput
        name="started_at"
        dateFormat="DD/MM/YYYY"
        autoComplete="off"
        placeholder="Date"
        onChange={handleChange}
        value={values.started_at}
        style={{ marginTop: '1rem' }}
      />
      <Input
        fluid
        name="count"
        type="number"
        min="1"
        placeholder="Count"
        onChange={handleChange}
        value={values.count}
        style={{ marginBottom: '1rem' }}
      />
      <TextArea
        disabled={isSubmitting}
        rows={2}
        placeholder="Notes"
        onChange={(e) => setFieldValue('notes', e.target.value)}
        value={values.notes}
        style={{ marginBottom: '1rem' }}
      />
    </>
  )
}

export const FormikOngoingServiceFields = ({
  choices,
}: {
  choices: CaseFormServiceChoices
}) => {
  const { setFieldValue, isSubmitting, values } =
    useFormikContext<ServiceCreate>()

  const handleChange = (e, { name, value }) => setFieldValue(name, value, false)

  return (
    <>
      <Field
        as={Dropdown}
        fluid
        selection
        name="type"
        loading={isSubmitting}
        placeholder="Service type"
        options={choiceToOptions(
          choices['type_' + values.category.toUpperCase()]
        )}
        onChange={handleChange}
      />
      <DateInput
        name="started_at"
        dateFormat="DD/MM/YYYY"
        autoComplete="off"
        placeholder="Start date"
        onChange={handleChange}
        value={values.started_at}
        style={{ marginTop: '1rem' }}
      />
      <DateInput
        name="finished_at"
        dateFormat="DD/MM/YYYY"
        autoComplete="off"
        placeholder="Finish date"
        onChange={handleChange}
        value={values.finished_at}
      />
      <TextArea
        disabled={isSubmitting}
        rows={2}
        placeholder="Notes"
        onChange={(e) => setFieldValue('notes', e.target.value)}
        value={values.notes}
        style={{ marginBottom: '1rem' }}
      />
    </>
  )
}
