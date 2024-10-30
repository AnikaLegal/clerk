import api, {
  ServiceCreate,
  useAppDispatch,
  useCreateCaseServiceMutation,
} from 'api'
import DateInput from 'comps/date-input'
import { RichTextArea } from 'comps/rich-text'
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
import { CaseDetailFormProps, CaseFormServiceChoices } from 'types'
import { choiceToOptions, filterEmpty, getAPIFormErrors } from 'utils'

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
              </div>
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
          {k != 'non_field_errors' && <div className="header">{k}</div>}
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
      <Dropdown
        fluid
        selection
        name="type"
        loading={isSubmitting}
        placeholder="Service type"
        options={choiceToOptions(
          choices['type_' + values.category.toUpperCase()]
        )}
        onChange={handleChange}
        value={values.type}
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
      <RichTextArea
        disabled={isSubmitting}
        placeholder="Notes"
        onUpdate={({ editor }) =>
          setFieldValue('notes', editor.isEmpty ? '' : editor.getHTML())
        }
        initialContent={values.notes}
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
      <Dropdown
        fluid
        selection
        name="type"
        loading={isSubmitting}
        placeholder="Service type"
        options={choiceToOptions(
          choices['type_' + values.category.toUpperCase()]
        )}
        onChange={handleChange}
        value={values.type}
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
      <RichTextArea
        disabled={isSubmitting}
        placeholder="Notes"
        onUpdate={({ editor }) =>
          setFieldValue('notes', editor.isEmpty ? '' : editor.getHTML())
        }
        initialContent={values.notes}
      />
    </>
  )
}
